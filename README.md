# 💰 Simulador de Aprovação de Empréstimos com IA

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](LINK_DA_SUA_APP_STREAMLIT_CLOUD_AQUI) Este projeto implementa um modelo de Machine Learning para prever a probabilidade de aprovação de pedidos de empréstimo e disponibiliza um simulador interativo construído com Streamlit. O objetivo é demonstrar um pipeline completo de ciência de dados, desde a análise exploratória até o deploy de uma aplicação web.

**Link para a aplicação (Streamlit Community Cloud):** [COLOQUE_O_LINK_DA_SUA_APP_STREAMLIT_CLOUD_AQUI](#)
*(Você obterá este link após fazer o deploy no Streamlit Community Cloud.)*

## 📝 Sobre o Projeto

O núcleo deste projeto é um modelo de classificação treinado para identificar a elegibilidade de crédito de solicitantes com base em diversas características financeiras e pessoais. A análise e o desenvolvimento do modelo foram realizados em um [notebook Jupyter (`Grant Loan Prediction.ipynb`)](#), enquanto a interface interativa para simulação foi criada usando a biblioteca [Streamlit (`main.py`)](#).

### ✨ Funcionalidades Principais
* **Análise Exploratória de Dados (EDA):** Investigação detalhada do conjunto de dados para identificar padrões, correlações e insights.
* **Engenharia de Features:** Criação de novas features e transformação das existentes para melhorar o desempenho do modelo.
* **Modelagem Preditiva:** Treinamento e avaliação de um modelo `RandomForestClassifier` para a tarefa de classificação.
* **Interface Interativa:** Uma aplicação web construída com Streamlit que permite aos usuários inserir seus dados e obter uma simulação da aprovação do empréstimo.
* **Deploy:** O projeto está preparado para deploy no Streamlit Community Cloud.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Análise e Manipulação de Dados:** Pandas, NumPy
* **Visualização de Dados:** Matplotlib, Seaborn
* **Machine Learning:** Scikit-learn (`RandomForestClassifier`, `StandardScaler`, `SimpleImputer`)
* **Interface Web:** Streamlit
* **Serialização do Modelo:** Pickle (ou Joblib)
* **Versionamento:** Git e GitHub

## 📂 Estrutura do Projeto

├── Grant Loan Prediction.ipynb  # Notebook com o desenvolvimento do modelo
├── LoanData.csv                 # Dataset de treinamento
├── test.csv                     # Dataset de teste (para previsões em novos dados)
├── main.py                      # Script da aplicação Streamlit
├── modelo_treinado.pkl          # Modelo de Machine Learning serializado
├── scaler.pkl                   # Objeto StandardScaler serializado
├── model_columns_ordered.json   # Ordem das colunas esperada pelo modelo
├── scaled_columns.json          # Nomes das colunas que foram escalonadas
├── requirements.txt             # Lista de dependências do Python
├── .gitignore                   # Arquivos e pastas ignorados pelo Git
└── README.md                    # Este arquivo de documentação

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto no seu ambiente local.

### 1. Pré-requisitos
* [Python](https://www.python.org/downloads/) (versão 3.8 ou superior recomendada)
* [Git](https://git-scm.com/downloads/) instalado

### 2. Configuração do Ambiente
Primeiro, clone este repositório (se ainda não o fez):
```bash
git clone [https://github.com/SEU_USUARIO/NOME_DO_SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_SEU_REPOSITORIO.git)
cd NOME_DO_SEU_REPOSITORIO