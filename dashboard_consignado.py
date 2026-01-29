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

# ---------------- TOP 10 ----------------
st.subheader("🏆 Top 10 Centrais por Valor Liberado")

ranking = (
    base
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

st.dataframe(
    ranking[["", "CENTRAL", "LIBERADO ACUMULADO (RP + CCS)"]],
    use_container_width=True,
    hide_index=True
)