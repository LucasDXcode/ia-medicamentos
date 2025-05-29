import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

ARQUIVO = 'medicamentos_completos_com_bromazepam.csv'

# --- Funções ---
def carregar_dados():
    try:
        return pd.read_csv(ARQUIVO)
    except:
        cols = ["Medicamento", "Classe", "Indicação", "Reações Adversas", "Apresentação", "Dosagem"]
        return pd.DataFrame(columns=cols)

def salvar_dados(df):
    df.to_csv(ARQUIVO, index=False)

def buscar(df, coluna, valor):
    if not valor:
        return pd.DataFrame()
    return df[df[coluna].str.lower().str.contains(valor.lower(), na=False)]

def adicionar_medicamento(df, novo):
    if novo["Medicamento"] == "":
        st.warning("Nome do medicamento é obrigatório!")
        return df
    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    salvar_dados(df)
    st.success("Medicamento adicionado com sucesso!")
    return df

# --- Streamlit UI ---
st.title("Sistema de Medicamentos - Versão Web")

df = carregar_dados()

menu = st.sidebar.selectbox("Menu", ["Buscar Medicamento", "Adicionar Medicamento", "Visualizar Dados", "Importar CSV"])

if menu == "Buscar Medicamento":
    st.header("Buscar Medicamento")
    tipo_busca = st.selectbox("Buscar por:", ["Medicamento", "Classe", "Indicação", "Reações Adversas"])
    valor = st.text_input("Digite o termo para busca:")
    if st.button("Buscar"):
        resultados = buscar(df, tipo_busca, valor)
        if resultados.empty:
            st.info("Nenhum resultado encontrado.")
        else:
            for _, row in resultados.iterrows():
                st.markdown(f"**Medicamento:** {row['Medicamento']}")
                st.markdown(f"Classe: {row['Classe']}")
                st.markdown(f"Indicação: {row['Indicação']}")
                st.markdown(f"Reações Adversas: {row['Reações Adversas']}")
                st.markdown(f"Apresentação: {row.get('Apresentação', '')}")
                st.markdown(f"Dosagem: {row.get('Dosagem', '')}")
                st.markdown("---")

elif menu == "Adicionar Medicamento":
    st.header("Adicionar Novo Medicamento")
    with st.form("form_add"):
        nome = st.text_input("Nome")
        classe = st.text_input("Classe")
        indicacao = st.text_input("Indicação")
        reacoes = st.text_input("Reações Adversas")
        apresentacao = st.text_input("Apresentação")
        dosagem = st.text_input("Dosagem")
        submitted = st.form_submit_button("Adicionar Medicamento")
        if submitted:
            novo = {
                "Medicamento": nome,
                "Classe": classe,
                "Indicação": indicacao,
                "Reações Adversas": reacoes,
                "Apresentação": apresentacao,
                "Dosagem": dosagem
            }
            df = adicionar_medicamento(df, novo)

elif menu == "Visualizar Dados":
    st.header("Gráficos e Listagem")
    if st.button("Listar Todos Medicamentos"):
        st.dataframe(df)

    if st.button("Gráfico: Top 10 Reações Adversas"):
        todas = ','.join(df['Reações Adversas'].dropna().tolist()).lower().split(',')
        freq = pd.Series([r.strip() for r in todas]).value_counts().head(10)
        fig, ax = plt.subplots()
        freq.plot(kind='barh', ax=ax)
        ax.set_xlabel("Frequência")
        ax.set_title("Top 10 Reações Adversas")
        st.pyplot(fig)

    if st.button("Gráfico: Medicamentos por Classe"):
        fig, ax = plt.subplots()
        df['Classe'].value_counts().head(10).plot(kind='bar', ax=ax)
        ax.set_ylabel("Quantidade")
        ax.set_title("Medicamentos por Classe")
        st.pyplot(fig)

elif menu == "Importar CSV":
    st.header("Importar dados de arquivo CSV")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            novo_df = pd.read_csv(uploaded_file, sep=None, engine='python')
            # Manter colunas esperadas (adaptar se necessário)
            cols_esperadas = ["Medicamento", "Classe", "Indicação", "Reações Adversas", "Apresentação", "Dosagem"]
            # Verificar colunas e tentar adaptar nomes se possível (ou avisar)
            missing_cols = [col for col in cols_esperadas if col not in novo_df.columns]
            if missing_cols:
                st.warning(f"Colunas faltando no CSV: {missing_cols}")
            else:
                df = pd.concat([df, novo_df], ignore_index=True).drop_duplicates().reset_index(drop=True)
                salvar_dados(df)
                st.success("Dados importados e base atualizada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao importar arquivo: {e}")
