import streamlit as st
import numpy as np
import pandas as pd
import pickle
import json

# --- Configurações Iniciais e Carregamento de Artefatos ---
# Inicializar variáveis de estado da sessão para controle da simulação
if 'simulacao_ativa' not in st.session_state:
    st.session_state.simulacao_ativa = False
if 'dados_simulacao' not in st.session_state:
    st.session_state.dados_simulacao = {}

# Carregar modelo, scaler, e arquivos JSON (com try-except)
try:
    model = pickle.load(open('modelo_treinado.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    with open('model_columns_ordered.json', 'r') as f:
        MODEL_COLUMNS_ORDERED = json.load(f)
    with open('scaled_columns.json', 'r') as f:
        COLS_TO_SCALE_FROM_NOTEBOOK = json.load(f)
except FileNotFoundError as e:
    # Tenta construir o nome do arquivo que faltou para a mensagem de erro
    missing_file = ""
    if 'modelo_treinado.pkl' not in str(e): missing_file = 'modelo_treinado.pkl'
    elif 'scaler.pkl' not in str(e): missing_file = 'scaler.pkl'
    elif 'model_columns_ordered.json' not in str(e): missing_file = 'model_columns_ordered.json'
    elif 'scaled_columns.json' not in str(e): missing_file = 'scaled_columns.json'
    
    st.error(f"Erro ao carregar arquivos necessários. Arquivo não encontrado: {missing_file if missing_file else str(e)}. Verifique se todos os arquivos .pkl e .json existem no mesmo diretório do script.")
    st.stop()
except Exception as e:
    st.error(f"Erro no carregamento inicial de arquivos: {e}")
    st.stop()

st.title("Simulador de Empréstimo 💰")
st.write("Preencha os dados abaixo para simular se você poderá obter um empréstimo.")

# --- Mapeamentos ---
gender_mapping = {'Masculino': 1, 'Feminino': 0}
married_mapping = {'Sim': 1, 'Não': 0}
dependents_mapping = {'0': 0, '1': 1, '2': 2, '3+': 3}
education_mapping = {'Graduado': 1, 'Não graduado': 0}
self_employed_mapping = {'Sim': 1, 'Não': 0}
property_mapping = {'Rural': 0, 'Semi Urbano': 1, 'Urbano': 2}

# Valores Padrão para os Widgets
DEFAULT_VALUES = {
    "v5_nome": "",
    "v5_gender": list(gender_mapping.keys())[0], # Ex: 'Masculino'
    "v5_married": list(married_mapping.keys())[1], # Ex: 'Não' como padrão
    "v5_dependents": list(dependents_mapping.keys())[0], # Ex: '0'
    "v5_education": list(education_mapping.keys())[0], # Ex: 'Graduado'
    "v5_self_employed": list(self_employed_mapping.keys())[1], # Ex: 'Não'
    "v5_applicant_income": 5000.0,
    "v5_coapplicant_income": 0.0,
    "v5_loan_amount": 100.0,
    "v5_loan_term": 360.0,
    "v5_credit_history": "Sim",
    "v5_property_area": list(property_mapping.keys())[1] # Ex: 'Semi Urbano'
}

# Inicializar chaves no session_state APENAS SE NÃO EXISTIREM
for key, default_value in DEFAULT_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


def format_currency_brl(value):
    try:
        val = float(value)
        s = f"{val:,.2f}".replace(',', '#TEMP#').replace('.', ',').replace('#TEMP#', '.')
        return s
    except (ValueError, TypeError): return str(value)

# --- Barra Lateral para Inputs do Usuário ---
st.sidebar.header('Preencha os dados do solicitante')

# Widgets da UI (eles automaticamente atualizam st.session_state[key] quando o usuário interage)
st.sidebar.text_input("Nome do requerente", key="v5_nome") # O valor inicial será pego do st.session_state.v5_nome
st.sidebar.selectbox("Gênero", list(gender_mapping.keys()), key="v5_gender")
st.sidebar.selectbox("Casado(a)", list(married_mapping.keys()), key="v5_married")
st.sidebar.selectbox("Dependentes", list(dependents_mapping.keys()), key="v5_dependents")
st.sidebar.selectbox("Educação", list(education_mapping.keys()), key="v5_education")
st.sidebar.selectbox("Autônomo(a)", list(self_employed_mapping.keys()), key="v5_self_employed")

st.sidebar.subheader("Informações Financeiras")
st.sidebar.number_input("Renda do requerente (R$)", min_value=0.0, step=100.0, format="%.2f", key="v5_applicant_income")
st.sidebar.number_input("Renda do coaplicante (R$)", min_value=0.0, step=100.0, format="%.2f", key="v5_coapplicant_income")
st.sidebar.number_input("Valor do empréstimo (em Milhares de R$)", min_value=1.0, step=1.0, format="%.1f", key="v5_loan_amount")
st.sidebar.number_input("Prazo do empréstimo (meses)", min_value=12.0, max_value=480.0, step=12.0, format="%.0f", key="v5_loan_term")
st.sidebar.selectbox("Possui histórico de crédito?", ("Sim", "Não"), key="v5_credit_history")
st.sidebar.selectbox("Área da propriedade", list(property_mapping.keys()), key="v5_property_area")


def collect_and_process_inputs():
    # Lê os valores ATUAIS dos widgets a partir do st.session_state
    # (Os widgets já atualizaram o session_state com seus valores atuais)
    nome = st.session_state.v5_nome
    gender_ui = st.session_state.v5_gender
    married_ui = st.session_state.v5_married
    dependents_ui = st.session_state.v5_dependents
    education_ui = st.session_state.v5_education
    self_employed_ui = st.session_state.v5_self_employed
    applicant_income = st.session_state.v5_applicant_income
    coapplicant_income = st.session_state.v5_coapplicant_income
    loan_amount_thousands_ui = st.session_state.v5_loan_amount
    loan_term_months_ui = st.session_state.v5_loan_term
    credit_history_ui = st.session_state.v5_credit_history
    property_area_ui = st.session_state.v5_property_area

    # --- Início do Pré-processamento ---
    gender_mapped = float(gender_mapping[gender_ui])
    married_mapped = float(married_mapping[married_ui])
    dependents_mapped = float(dependents_mapping[dependents_ui])
    education_mapped = float(education_mapping[education_ui])
    self_employed_mapped = float(self_employed_mapping[self_employed_ui])
    credit_history_mapped = 1.0 if credit_history_ui == 'Sim' else 0.0
    property_area_mapped = float(property_mapping[property_area_ui])

    total_income_raw = float(applicant_income) + float(coapplicant_income)
    # Adicionar uma pequena constante para evitar log(0) ou log de negativo se total_income_raw for 0
    total_income_log = np.log1p(total_income_raw)
    loan_amount_log = np.log1p(float(loan_amount_thousands_ui))
    loan_term_original = float(loan_term_months_ui)

    data_to_scale_df = pd.DataFrame({
        'TotalIncome': [total_income_log],
        'LoanAmount': [loan_amount_log],
        'Loan_Amount_Term': [loan_term_original]
    }, columns=COLS_TO_SCALE_FROM_NOTEBOOK)
    
    scaled_features_array = scaler.transform(data_to_scale_df)

    input_dict_for_model = {
        'Gender': gender_mapped, 'Married': married_mapped, 'Dependents': dependents_mapped,
        'Education': education_mapped, 'Self_Employed': self_employed_mapped,
        'Credit_History': credit_history_mapped, 'Property_Area': property_area_mapped,
        'TotalIncome': scaled_features_array[0, COLS_TO_SCALE_FROM_NOTEBOOK.index('TotalIncome')],
        'LoanAmount': scaled_features_array[0, COLS_TO_SCALE_FROM_NOTEBOOK.index('LoanAmount')],
        'Loan_Amount_Term': scaled_features_array[0, COLS_TO_SCALE_FROM_NOTEBOOK.index('Loan_Amount_Term')]
    }
    model_input_df = pd.DataFrame([input_dict_for_model], columns=MODEL_COLUMNS_ORDERED)
    
    data_for_display = {
        "nome": nome, "gender_feature": gender_ui, "married_feature": married_ui,
        "dependents_feature": dependents_ui, "education_feature": education_ui,
        "self_employed_feature": self_employed_ui, "property_feature": property_area_ui,
        "applicant_income": applicant_income, "coapplicant_income": coapplicant_income,
        "total_income_display": total_income_raw, "loan_amount_for_display": loan_amount_thousands_ui,
        "loan_term": loan_term_months_ui, "credit_history_feature_for_display": credit_history_ui
    }
    return model_input_df, data_for_display

# Botão Simular
if st.sidebar.button('Simular Empréstimo', key="v5_simular_btn"):
    model_input_df, data_for_display = collect_and_process_inputs()

    if not data_for_display["nome"].strip():
        st.sidebar.warning("Por favor, preencha o nome do requerente.")
        st.session_state.simulacao_ativa = False
    # Permitir renda zero para um dos aplicantes, mas não para ambos (via TotalIncome)
    elif data_for_display["total_income_display"] <= 0 and data_for_display["applicant_income"] <=0 and data_for_display["coapplicant_income"] <=0:
         st.sidebar.warning("A renda total (requerente ou coaplicante) deve ser maior que zero.")
         st.session_state.simulacao_ativa = False
    else:
        try:
            prediction = model.predict(model_input_df)
            prediction_probability = model.predict_proba(model_input_df)

            st.session_state.dados_simulacao = {
                **data_for_display,
                "prediction": prediction,
                "prediction_probability": prediction_probability
            }
            st.session_state.simulacao_ativa = True
            st.rerun() # Adicionado para garantir que a UI atualize após a simulação

        except ValueError as ve:
            st.error(f"Erro durante a predição: {ve}")
            st.write("DataFrame enviado ao modelo (model_input_df):")
            st.dataframe(model_input_df)
            st.write("Colunas esperadas pelo modelo (MODEL_COLUMNS_ORDERED):")
            st.code(f"{MODEL_COLUMNS_ORDERED}")
            st.write("Colunas no input do modelo (model_input_df.columns):")
            st.code(f"{list(model_input_df.columns)}")
            st.session_state.simulacao_ativa = False
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            st.session_state.simulacao_ativa = False

# --- Exibição dos Resultados ---
if st.session_state.get('simulacao_ativa', False) and st.session_state.get('dados_simulacao'):
    data_exibicao = st.session_state.dados_simulacao
    
    st.subheader('Dados Informados para Simulação:')
    # Layout da exibição dos dados (igual ao anterior)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        - **Nome:** {data_exibicao['nome']}
        - **Gênero:** {data_exibicao['gender_feature']}
        - **Casado(a):** {data_exibicao['married_feature']}
        - **Dependentes:** {data_exibicao['dependents_feature']}
        """)
    with col2:
        st.markdown(f"""
        - **Educação:** {data_exibicao['education_feature']}
        - **Autônomo(a):** {data_exibicao['self_employed_feature']}
        - **Área Propriedade:** {data_exibicao['property_feature']}
        - **Histórico Crédito:** {data_exibicao['credit_history_feature_for_display']}
        """)
    
    st.markdown(f"""
    - **Renda Requerente:** R$ {format_currency_brl(data_exibicao['applicant_income'])}
    - **Renda Coaplicante:** R$ {format_currency_brl(data_exibicao['coapplicant_income'])}
    - **Renda Total:** R$ {format_currency_brl(data_exibicao['total_income_display'])}
    - **Valor Empréstimo:** R$ {data_exibicao['loan_amount_for_display'] * 1000:,.2f} ({data_exibicao['loan_amount_for_display']} mil)
    - **Prazo:** {data_exibicao['loan_term']:.0f} meses
    """)
    st.markdown("---")

    resultado_texto = "Parabéns! Seu empréstimo foi APROVADO!" if data_exibicao['prediction'][0] == 1 else "Com base nos dados, não será possível oferecer o empréstimo no momento."
    cor_resultado = "green" if data_exibicao['prediction'][0] == 1 else "red"

    st.subheader(f"Resultado da Simulação para {data_exibicao['nome']}:")
    st.markdown(f"<h3 style='color:{cor_resultado};'>{resultado_texto}</h3>", unsafe_allow_html=True)

    prob_aprovacao = data_exibicao['prediction_probability'][0][1] * 100
    st.metric(label="Probabilidade de Aprovação", value=f"{prob_aprovacao:.2f}%")
    st.progress(prob_aprovacao / 100)

    if data_exibicao['prediction'][0] == 1:
        if prob_aprovacao >= 75: st.success("Você tem uma excelente chance de aprovação!")
        elif prob_aprovacao >= 50: st.info("Suas chances de aprovação são boas.")
    else:
        if prob_aprovacao < 25: st.error("Suas chances de aprovação são baixas. Considere melhorar seu perfil financeiro.")
        else: st.warning("Suas chances de aprovação não são altas.")

    if st.button("Fazer Nova Simulação", key="v5_nova_simulacao_btn"):
        st.session_state.simulacao_ativa = False
        st.session_state.dados_simulacao = {}
        
        # Remover as chaves dos widgets do session_state para que eles
        # peguem seus valores padrão na próxima execução (definidos em DEFAULT_VALUES).
        # Isso fará com que o loop de inicialização no topo do script os redefina.
        for key_widget in DEFAULT_VALUES.keys():
            if key_widget in st.session_state:
                del st.session_state[key_widget]
        st.rerun()