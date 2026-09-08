# ============================================================
# TP3 - DESENVOLVIMENTO DE INTERFACES COM STREAMLIT
# Aluno: Ruan Luiz Fernandes da Silva Lima
# Dados: portal Data.Rio - secao turismo
#
# INDICE DOS ITENS NESTE ARQUIVO:
#   Itens 6 e 8 - funcao de carregamento com cache, barra de
#                 progresso e spinner. Ficam no topo porque o
#                 Python exige que a funcao seja definida antes
#                 de ser chamada pelo item 2.
#   Item 2  - upload do arquivo XLS
#   Item 9  - session state para guardar as preferencias
#   Item 3  - filtros e seletores (radio, checkbox, dropdown)
#   Item 12 - metricas basicas
#   Item 4  - tabela interativa
#   Item 5  - download dos dados filtrados
#   Item 10 - graficos simples (linha, barras, pizza)
#   Item 11 - graficos avancados (histograma e scatter plot)
#   Item 7  - color picker
# ============================================================

import streamlit as st
import pandas as pd
import io
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Turismo no Rio de Janeiro", layout="wide")

st.title("Turismo no Municipio do Rio de Janeiro")
st.write("Dados do portal Data.Rio")

# ============================================================
# 8. Utilizar Funcionalidade de Cache:
# Utilize a funcionalidade de cache do Streamlit para armazenar
# os dados carregados dos arquivos XLS, evitando a necessidade de
# recarrega-los a cada nova interacao.
#
# 6. Utilizar Barra de Progresso e Spinners:
# Adicione uma barra de progresso e um spinner para indicar o
# carregamento dos dados enquanto o arquivo XLS e processado e
# exibido na interface.
# ============================================================

@st.cache_data
def carregar_planilha(arquivo):
    barra = st.progress(0, text="Lendo o arquivo...")
    with st.spinner("Processando os dados da planilha..."):
        time.sleep(0.5)
        barra.progress(30, text="Abrindo a planilha...")
        tabela = pd.read_excel(arquivo)
        time.sleep(0.5)
        barra.progress(70, text="Organizando as colunas...")
        time.sleep(0.5)
        barra.progress(100, text="Pronto")
    barra.empty()
    return tabela

# ============================================================
# 2. Realizar Upload de Arquivo XLS:
# Crie uma interface em Streamlit que permita ao usuario fazer
# o upload de um arquivo XLS contendo dados de turismo do
# portal Data.Rio.
# ============================================================

arquivo = st.file_uploader("Escolha o arquivo XLS com os dados de turismo", type=["xls", "xlsx"])

if arquivo is not None:

    dados = carregar_planilha(arquivo)
    st.success("Arquivo carregado com sucesso")
    st.caption("Os dados ficam no cache, entao a planilha nao e lida de novo a cada filtro.")

    # ============================================================
    # 9. Persistir Dados Usando Session State:
    # Implemente a persistencia de dados na aplicacao utilizando
    # Session State para manter as preferencias do usuario
    # (selecoes e filtros escolhidos) durante a navegacao.
    # ============================================================

    if "contador" not in st.session_state:
        st.session_state.contador = 0
    st.session_state.contador = st.session_state.contador + 1

    if "nome_arquivo" not in st.session_state:
        st.session_state.nome_arquivo = arquivo.name

    if st.session_state.nome_arquivo != arquivo.name:
        st.session_state.nome_arquivo = arquivo.name
        for chave in list(st.session_state.keys()):
            if chave.startswith("f_") or chave.startswith("col_"):
                del st.session_state[chave]

    # ============================================================
    # 3. Filtro de Dados e Selecao:
    # Exiba o dataset para o usuario e implemente tres seletores
    # diferentes (radio, checkbox, dropdowns) na interface que
    # permitam ao usuario filtrar os dados carregados e selecionar
    # as colunas ou linhas que deseja visualizar.
    # ============================================================

    st.sidebar.header("Filtros")

    colunas_texto = []
    colunas_numero = []
    for c in dados.columns:
        if pd.api.types.is_numeric_dtype(dados[c]):
            colunas_numero.append(c)
        else:
            colunas_texto.append(c)

    coluna_grupo = colunas_texto[0]

    modo = st.sidebar.radio("Como quer filtrar?", ["Mostrar tudo", "Escolher " + coluna_grupo], key="f_modo")

    lista = sorted(dados[coluna_grupo].unique())
    escolhido = st.sidebar.selectbox("Selecione " + coluna_grupo, lista, key="f_grupo")

    st.sidebar.write("Colunas que quer ver:")
    colunas_visiveis = []
    for c in dados.columns:
        marcado = st.sidebar.checkbox(c, value=True, key="col_" + c)
        if marcado:
            colunas_visiveis.append(c)

    ano_min = int(dados["ano"].min())
    ano_max = int(dados["ano"].max())
    faixa = st.sidebar.slider("Periodo", ano_min, ano_max, (ano_min, ano_max), key="f_periodo")

    if st.sidebar.button("Limpar filtros"):
        for chave in list(st.session_state.keys()):
            if chave.startswith("f_") or chave.startswith("col_"):
                del st.session_state[chave]
        st.rerun()

    st.sidebar.caption("Interacoes nesta sessao: " + str(st.session_state.contador))

    if modo == "Mostrar tudo":
        filtrado = dados
    else:
        filtrado = dados[dados[coluna_grupo] == escolhido]

    filtrado = filtrado[filtrado["ano"] >= faixa[0]]
    filtrado = filtrado[filtrado["ano"] <= faixa[1]]

    if len(colunas_visiveis) > 0:
        filtrado = filtrado[colunas_visiveis]

    colunas_valor = []
    for c in filtrado.columns:
        if c != "ano" and pd.api.types.is_numeric_dtype(filtrado[c]):
            colunas_valor.append(c)

    # ============================================================
    # 12. Exibir Metricas Basicas:
    # Implemente a exibicao de metricas basicas (como contagem de
    # registros, medias, somas) diretamente na interface para
    # fornecer um resumo rapido dos dados carregados.
    # ============================================================

    st.header("Resumo dos dados filtrados")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registros", len(filtrado))
    m2.metric("Periodo", str(faixa[0]) + " a " + str(faixa[1]))

    if coluna_grupo in filtrado.columns:
        m3.metric("Grupos", filtrado[coluna_grupo].nunique())
    else:
        m3.metric("Grupos", "-")

    if len(colunas_valor) > 0:
        m4.metric("Media de " + colunas_valor[0], round(filtrado[colunas_valor[0]].mean(), 1))
    else:
        m4.metric("Media", "-")

    if len(colunas_valor) > 0:
        st.write("Resumo por coluna numerica:")
        resumo = []
        for c in colunas_valor:
            resumo.append({
                "coluna": c,
                "soma": round(filtrado[c].sum(), 1),
                "media": round(filtrado[c].mean(), 1),
                "minimo": round(filtrado[c].min(), 1),
                "maximo": round(filtrado[c].max(), 1)
            })
        st.dataframe(pd.DataFrame(resumo), hide_index=True, width="stretch")

    # ============================================================
    # 4. Criar Visualizacoes de Dados - Tabelas:
    # Crie uma tabela interativa que exiba os dados filtrados de
    # acordo com os seletores carregados e permita ao usuario
    # ordenar e filtrar as colunas diretamente pela interface.
    # ============================================================

    st.header("Tabela interativa")
    st.write("Clique no nome da coluna para ordenar. Use a lupa no canto da tabela para buscar.")
    st.write("Linhas encontradas:", len(filtrado))

    formato = {}
    for c in filtrado.columns:
        if c == "ano":
            formato[c] = st.column_config.NumberColumn("ano", format="%d")
        elif pd.api.types.is_numeric_dtype(filtrado[c]):
            formato[c] = st.column_config.NumberColumn(c, format="%.2f")

    st.dataframe(filtrado, column_config=formato, width="stretch", hide_index=True)

    # ============================================================
    # 5. Desenvolver Servico de Download de Arquivos:
    # Implemente um servico que permita ao usuario fazer o download
    # dos dados filtrados em formato XLS diretamente pela interface
    # da aplicacao.
    # ============================================================

    st.header("Baixar os dados filtrados")

    buffer = io.BytesIO()
    escritor = pd.ExcelWriter(buffer, engine="xlsxwriter")
    filtrado.to_excel(escritor, index=False, sheet_name="dados")
    escritor.close()

    st.download_button(
        label="Baixar em XLSX",
        data=buffer.getvalue(),
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("O arquivo baixado tem as mesmas", len(filtrado), "linhas que estao na tabela acima.")

    # ============================================================
    # 10. Criar Visualizacoes de Dados - Graficos Simples:
    # Desenvolva graficos simples (barras, linhas, e pie charts)
    # para visualizacao dos dados carregados, utilizando o
    # Streamlit.
    # ============================================================

    st.header("Graficos simples")

    if len(colunas_valor) == 0:
        st.warning("Marque pelo menos uma coluna de numero na barra lateral para ver os graficos.")
    else:
        valor = st.selectbox("Qual valor quer ver nos graficos?", colunas_valor, key="g_valor")
        escala_log = st.checkbox("Usar escala logaritmica (ajuda quando os valores sao muito diferentes)", key="g_log")

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Linha - evolucao por ano")
            if coluna_grupo in filtrado.columns:
                linha = filtrado.pivot_table(index="ano", columns=coluna_grupo, values=valor)
            else:
                linha = filtrado.groupby("ano")[valor].mean()

            figura1, eixo1 = plt.subplots(figsize=(5, 3))
            linha.plot(ax=eixo1, marker="o", markersize=3, linewidth=1.2)
            if escala_log:
                eixo1.set_yscale("log")
            eixo1.set_xlabel("ano", fontsize=8)
            eixo1.set_ylabel(valor, fontsize=8)
            eixo1.tick_params(labelsize=7)
            eixo1.legend(fontsize=6)
            eixo1.grid(alpha=0.3)
            figura1.tight_layout()
            st.pyplot(figura1, use_container_width=False)

        with col_b:
            st.subheader("Barras - total por " + coluna_grupo)
            if coluna_grupo in filtrado.columns:
                barras = filtrado.groupby(coluna_grupo)[valor].sum().sort_values()
            else:
                barras = filtrado.groupby("ano")[valor].sum()

            figura2, eixo2 = plt.subplots(figsize=(5, 3))
            barras.plot(kind="barh", ax=eixo2, color="#1f77b4")
            if escala_log:
                eixo2.set_xscale("log")
            eixo2.set_xlabel(valor, fontsize=8)
            eixo2.set_ylabel("", fontsize=8)
            eixo2.tick_params(labelsize=7)
            figura2.tight_layout()
            st.pyplot(figura2, use_container_width=False)

        st.subheader("Pizza - participacao de cada " + coluna_grupo)
        if coluna_grupo in filtrado.columns:
            pizza = filtrado.groupby(coluna_grupo)[valor].sum()
            col_c, col_d = st.columns([1, 2])
            with col_c:
                figura3, eixo3 = plt.subplots(figsize=(3.2, 3.2))
                eixo3.pie(pizza, labels=pizza.index, autopct="%1.1f%%", textprops={"fontsize": 6})
                eixo3.axis("equal")
                figura3.tight_layout()
                st.pyplot(figura3, use_container_width=False)
            with col_d:
                st.write("Valores somados no periodo escolhido:")
                st.dataframe(pizza, width="stretch")
        else:
            st.info("Marque a coluna " + coluna_grupo + " na barra lateral para ver a pizza.")

        # ============================================================
        # 11. Criar Visualizacoes de Dados - Graficos Avancados:
        # Adicione graficos avancados (histograma e scatter plot)
        # para fornecer insights mais profundos sobre os dados.
        # ============================================================

        st.header("Graficos avancados")

        col_e, col_f = st.columns(2)

        with col_e:
            st.subheader("Histograma")
            caixas = st.slider("Quantas faixas?", 5, 30, 12, key="g_bins")

            figura4, eixo4 = plt.subplots(figsize=(5, 3))
            eixo4.hist(filtrado[valor], bins=caixas, color="#1f77b4", edgecolor="white")
            eixo4.set_xlabel(valor, fontsize=8)
            eixo4.set_ylabel("quantidade de registros", fontsize=8)
            eixo4.tick_params(labelsize=7)
            eixo4.grid(alpha=0.3)
            figura4.tight_layout()
            st.pyplot(figura4, use_container_width=False)
            st.caption("Mostra em quais faixas de valor os registros se concentram.")

        with col_f:
            st.subheader("Scatter plot")

            if len(colunas_valor) >= 2:
                eixo_x = st.selectbox("Eixo X", colunas_valor, index=0, key="g_x")
                eixo_y = st.selectbox("Eixo Y", colunas_valor, index=1, key="g_y")
            else:
                eixo_x = "ano"
                eixo_y = valor
                st.caption("Como so tem uma coluna de valor, o eixo X e o ano.")

            figura5, eixo5 = plt.subplots(figsize=(5, 3))

            if coluna_grupo in filtrado.columns:
                for grupo in filtrado[coluna_grupo].unique():
                    parte = filtrado[filtrado[coluna_grupo] == grupo]
                    eixo5.scatter(parte[eixo_x], parte[eixo_y], label=grupo, s=18, alpha=0.7)
                eixo5.legend(fontsize=6)
            else:
                eixo5.scatter(filtrado[eixo_x], filtrado[eixo_y], s=18, alpha=0.7, color="#1f77b4")

            eixo5.set_xlabel(eixo_x, fontsize=8)
            eixo5.set_ylabel(eixo_y, fontsize=8)
            eixo5.tick_params(labelsize=7)
            eixo5.grid(alpha=0.3)
            figura5.tight_layout()
            st.pyplot(figura5, use_container_width=False)
            st.caption("Mostra se as duas colunas escolhidas crescem juntas ou nao.")

        if len(colunas_valor) >= 2:
            correlacao = filtrado[colunas_valor].corr()
            st.write("Correlacao entre as colunas numericas:")
            st.dataframe(correlacao.round(3), width="stretch")

else:
    st.info("Faca o upload de aeroportos.xlsx ou hoteis.xlsx para comecar")

# ============================================================
# 7. Utilizar Color Picker:
# Adicione um color picker a interface que permita ao usuario
# personalizar a cor de fundo do painel e das fontes exibidas
# na aplicacao.
# ============================================================

st.sidebar.header("Aparencia")
cor_fundo = st.sidebar.color_picker("Cor de fundo do painel", "#FFFFFF", key="cor_fundo")
cor_fonte = st.sidebar.color_picker("Cor da fonte", "#000000", key="cor_fonte")

estilo = """
<style>
.stApp {
    background-color: FUNDO;
}
section[data-testid="stSidebar"] {
    background-color: FUNDO;
}
.stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp span, .stApp li,
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: FONTE;
}
</style>
"""
estilo = estilo.replace("FUNDO", cor_fundo)
estilo = estilo.replace("FONTE", cor_fonte)
st.markdown(estilo, unsafe_allow_html=True)