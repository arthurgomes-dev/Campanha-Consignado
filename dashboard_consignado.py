import streamlit as st
import pandas as pd
import altair as alt

# ---------------- LEITURA ----------------
tabela = pd.read_excel(
    "campanha_consignado_2026.xlsx",
    sheet_name="Singulares"
)

# ---------------- BLINDAGEM DE COLUNAS ----------------
tabela.columns = (
    tabela.columns
    .str.strip()
    .str.upper()
)

tabela = tabela.rename(columns={
    "Nº CENTRAL": "CENTRAL",
    "N° CENTRAL": "CENTRAL",
    "Nº SINGULAR": "SINGULAR",
    "N° SINGULAR": "SINGULAR"
})

# Remove colunas duplicadas
tabela = tabela.loc[:, ~tabela.columns.duplicated()]

# ---------------- FUNÇÃO FORMATAÇÃO ----------------
def formata_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------- TÍTULO ----------------
st.title("🏆 Campanha Craques do Consignado")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("logo_sicoob.png", use_container_width=True)
    st.header("Filtros")

    cor = st.color_picker("Cor dos Gráficos", "#38B6AB")

    centrais = st.multiselect(
        "Selecione as Centrais",
        sorted(tabela["CENTRAL"].dropna().unique())
    )

    singulares = st.multiselect(
        "Selecione as Singulares",
        sorted(tabela["SINGULAR"].dropna().unique())
    )

    chaves = st.multiselect(
        "Selecione as Chaves",
        sorted(tabela["CHAVE"].dropna().unique())
    )

# ---------------- FILTROS ----------------
if centrais:
    tabela = tabela[tabela["CENTRAL"].isin(centrais)]

if singulares:
    tabela = tabela[tabela["SINGULAR"].isin(singulares)]

if chaves:
    tabela = tabela[tabela["CHAVE"].isin(chaves)]    

# ---------------- ALERTA SEM DADOS ----------------
if tabela.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ---------------- MÉTRICAS ----------------
st.metric(
    "Valor Cadastrado",
    formata_real(tabela["CADASTRADO ACUMULADO (RP + CCS)"].sum())
)

st.metric(
    "Valor Liberado",
    formata_real(tabela["LIBERADO ACUMULADO (RP + CCS)"].sum())
)

# ---------------- BASE AGRUPADA ----------------
base = tabela.groupby("CENTRAL", as_index=False).sum()

# ---------------- GRÁFICOS ----------------

# ---------------- FORMATAÇÃO PARA TOOLTIP ----------------
# Cria colunas formatadas com separador de milhar + R$
base["CADASTRADO_FMT"] = base["CADASTRADO ACUMULADO (RP + CCS)"].apply(
    lambda x: f"R$ {int(x):,}".replace(",", ".")
)
base["LIBERADO_FMT"] = base["LIBERADO ACUMULADO (RP + CCS)"].apply(
    lambda x: f"R$ {int(x):,}".replace(",", ".")
)

# ---------------- GRÁFICO VALOR CADASTRADO ----------------
graf_cadastrado = alt.Chart(base).mark_bar(color=cor).encode(
    x=alt.X(
        "CADASTRADO ACUMULADO (RP + CCS):Q",
        title="Valor Cadastrado",
        axis=alt.Axis(format=",.0f")  # mantém eixo numérico correto
    ),
    y=alt.Y(
        "CENTRAL:N",
        sort='-x',
        title="Central"
    ),
    tooltip=[
        "CENTRAL",
        alt.Tooltip("CADASTRADO_FMT:N", title="Valor Cadastrado")
    ]
)

st.subheader("📊 Valor Cadastrado por Central")
st.altair_chart(graf_cadastrado, use_container_width=True)

# ---------------- GRÁFICO VALOR LIBERADO ----------------
graf_liberado = alt.Chart(base).mark_bar(color=cor).encode(
    x=alt.X(
        "LIBERADO ACUMULADO (RP + CCS):Q",
        title="Valor Liberado",
        axis=alt.Axis(format=",.0f")
    ),
    y=alt.Y(
        "CENTRAL:N",
        sort='-x',
        title="Central"
    ),
    tooltip=[
        "CENTRAL",
        alt.Tooltip("LIBERADO_FMT:N", title="Valor Liberado")
    ]
)

st.subheader("📊 Valor Liberado por Central")
st.altair_chart(graf_liberado, use_container_width=True)

# ---------------- BASE AGRUPADA POR SINGULAR ----------------
base_singular = (
    tabela
    .groupby("SINGULAR", as_index=False)
    .sum()
)

#produção diária

producao = pd.read_excel(
    "campanha_consignado_2026.xlsx",
    sheet_name="Produção Diária"
)

# Blindagem de colunas
producao.columns = (
    producao.columns
    .str.strip()
    .str.upper()
)

producao["DATA"] = pd.to_datetime(producao["DATA"])

st.subheader("📅 Período Produção Diária")

data_min = producao["DATA"].min()
data_max = producao["DATA"].max()

periodo = st.date_input(
    "Selecione o período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
    format="DD/MM/YYYY"
)

if len(periodo) == 2:
    inicio, fim = periodo
    producao = producao[
        (producao["DATA"] >= pd.to_datetime(inicio)) &
        (producao["DATA"] <= pd.to_datetime(fim))
    ]

tabela_producao = producao[[
    "DATA",
    "VALOR CADASTRADO CCS",
    "VALOR LIBERADO CCS",
    "VALOR CADASTRADO RP",
    "VALOR LIBERADO RP",
    "VALOR TOTAL CADASTRADO",
    "VALOR TOTAL LIBERADO"
]].copy()

colunas_valor = tabela_producao.columns.drop("DATA")

for col in colunas_valor:
    tabela_producao[col] = tabela_producao[col].apply(formata_real)

# Formatar data (dd/mm/aaaa)
tabela_producao["DATA"] = tabela_producao["DATA"].dt.strftime("%d/%m/%Y")

st.subheader("📋 Produção Diária")

st.dataframe(
    tabela_producao.sort_values("DATA"),
    use_container_width=True,
    hide_index=True
)

# ---------------- TOP 10 ----------------
st.subheader("🏆 Top 10 Cooperativas por Valor Liberado")

ranking = (
    base_singular
    .sort_values("LIBERADO ACUMULADO (RP + CCS)", ascending=False)
    .head(10)
    .copy()
)

ranking["POSIÇÃO"] = range(1, len(ranking) + 1)

def medalha(pos):
    if pos == 1: return "🥇"
    if pos == 2: return "🥈"
    if pos == 3: return "🥉"
    return ""

ranking[""] = ranking["POSIÇÃO"].apply(medalha)

# Formatação em Real (padrão BR)
ranking["VALOR LIBERADO"] = ranking["LIBERADO ACUMULADO (RP + CCS)"].apply(formata_real)

st.dataframe(
    ranking[["", "SINGULAR", "VALOR LIBERADO"]],
    use_container_width=True,
    hide_index=True
)
