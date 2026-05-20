import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Startups e Inovação no Brasil",
    page_icon="🚀",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    caminho = Path("dados") / "simulacao_startups_brasil.csv"
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["ano_mes"] = df["data"].dt.to_period("M").astype(str)
    return df

df = carregar_dados()

st.title("🚀 Análise de Startups e Inovação Tecnológica no Brasil")
st.markdown("""
Este dashboard analisa o ecossistema brasileiro de startups entre **2015 e 2024**, com foco em setores,
regiões, investimentos, crescimento, tecnologias emergentes e níveis de inovação.

**Pergunta central:** quais grupos de startups, setores e regiões concentram maior força inovadora e potencial de crescimento?
""")

# Sidebar filters
st.sidebar.header("🔎 Filtros interativos")

anos = sorted(df["ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)

meses = sorted(df["mes"].unique())
mes_sel = st.sidebar.multiselect("Mês", meses, default=meses)

regioes = sorted(df["regiao"].unique())
regiao_sel = st.sidebar.multiselect("Região", regioes, default=regioes)

ufs = sorted(df["uf"].unique())
uf_sel = st.sidebar.multiselect("Estado (UF)", ufs, default=ufs)

setores = sorted(df["setor"].unique())
setor_sel = st.sidebar.multiselect("Setor", setores, default=setores)

estagios = sorted(df["estagio"].unique())
estagio_sel = st.sidebar.multiselect("Estágio", estagios, default=estagios)

inovacoes = sorted(df["nivel_inovacao"].unique())
inovacao_sel = st.sidebar.multiselect("Nível de inovação", inovacoes, default=inovacoes)

df_f = df[
    (df["ano"].isin(ano_sel)) &
    (df["mes"].isin(mes_sel)) &
    (df["regiao"].isin(regiao_sel)) &
    (df["uf"].isin(uf_sel)) &
    (df["setor"].isin(setor_sel)) &
    (df["estagio"].isin(estagio_sel)) &
    (df["nivel_inovacao"].isin(inovacao_sel))
].copy()

if df_f.empty:
    st.warning("Nenhum registro encontrado com os filtros selecionados.")
    st.stop()

# KPIs
total_startups = df_f["startup"].nunique()
invest_total = df_f["investimento_recebido"].sum()
faturamento_total = df_f["faturamento"].sum()
crescimento_medio = df_f["crescimento_percentual"].mean()
setor_promissor = df_f.groupby("setor")["investimento_recebido"].sum().idxmax()
estado_inovador = df_f.groupby("uf")["investimento_recebido"].sum().idxmax()
startup_top = df_f.groupby("startup")["faturamento"].sum().idxmax()

st.subheader("📌 KPIs principais")
c1, c2, c3 = st.columns(3)
c1.metric("Total de startups únicas", f"{total_startups:,}".replace(",", "."))
c2.metric("Investimento total", f"R$ {invest_total/1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Faturamento total", f"R$ {faturamento_total/1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", "."))

c4, c5, c6 = st.columns(3)
c4.metric("Crescimento médio", f"{crescimento_medio:.1f}%".replace(".", ","))
c5.metric("Setor mais promissor", setor_promissor)
c6.metric("Estado mais inovador", estado_inovador)

st.info(f"Startup com maior faturamento no recorte filtrado: **{startup_top}**.")

# Charts
st.subheader("📈 Evolução temporal do ecossistema")
temporal = df_f.groupby("ano").agg(
    startups=("startup", "nunique"),
    investimento=("investimento_recebido", "sum"),
    faturamento=("faturamento", "sum"),
    crescimento=("crescimento_percentual", "mean")
).reset_index()

fig_temporal = px.line(
    temporal,
    x="ano",
    y="investimento",
    markers=True,
    title="Evolução anual do investimento recebido pelas startups",
    labels={"ano": "Ano", "investimento": "Investimento recebido (R$)"}
)
fig_temporal.update_layout(template="plotly_white")
st.plotly_chart(fig_temporal, use_container_width=True)

st.markdown("""
**Interpretação:** a evolução anual permite identificar períodos de maior concentração de capital e sinaliza
momentos em que o ecossistema esteve mais aquecido. Para gestão pública ou privada, isso ajuda a decidir
quando ampliar programas de incentivo, aceleração ou captação.
""")

col1, col2 = st.columns(2)

with col1:
    setor = df_f.groupby("setor").agg(
        quantidade=("startup", "count"),
        investimento=("investimento_recebido", "sum"),
        crescimento=("crescimento_percentual", "mean")
    ).reset_index().sort_values("investimento", ascending=False)

    fig_setor = px.bar(
        setor,
        x="setor",
        y="investimento",
        title="Investimento recebido por setor",
        labels={"setor": "Setor", "investimento": "Investimento recebido (R$)"}
    )
    fig_setor.update_layout(template="plotly_white", xaxis_tickangle=-35)
    st.plotly_chart(fig_setor, use_container_width=True)

with col2:
    estado = df_f.groupby("uf").agg(
        quantidade=("startup", "count"),
        investimento=("investimento_recebido", "sum"),
        crescimento=("crescimento_percentual", "mean")
    ).reset_index().sort_values("investimento", ascending=False)

    fig_estado = px.bar(
        estado.head(15),
        x="uf",
        y="investimento",
        title="Top 15 estados por investimento",
        labels={"uf": "Estado", "investimento": "Investimento recebido (R$)"}
    )
    fig_estado.update_layout(template="plotly_white")
    st.plotly_chart(fig_estado, use_container_width=True)

st.markdown("""
**Interpretação:** setores e estados com maior investimento tendem a concentrar capacidade de escala,
maturidade empresarial e atratividade para investidores. Entretanto, investimento alto não significa
automaticamente maior inovação; por isso, a leitura deve ser combinada com crescimento, tecnologia e nível de inovação.
""")

st.subheader("🧭 Comparação regional")
regiao = df_f.groupby("regiao").agg(
    startups=("startup", "nunique"),
    investimento=("investimento_recebido", "sum"),
    faturamento=("faturamento", "sum"),
    crescimento=("crescimento_percentual", "mean")
).reset_index().sort_values("investimento", ascending=False)

fig_regiao = px.bar(
    regiao,
    x="regiao",
    y=["investimento", "faturamento"],
    barmode="group",
    title="Investimento e faturamento por região",
    labels={"regiao": "Região", "value": "Valor (R$)", "variable": "Indicador"}
)
fig_regiao.update_layout(template="plotly_white")
st.plotly_chart(fig_regiao, use_container_width=True)

st.subheader("🔥 Heatmap de inovação: setor x nível de inovação")
heat = pd.crosstab(df_f["setor"], df_f["nivel_inovacao"])
fig_heat = px.imshow(
    heat,
    text_auto=True,
    aspect="auto",
    title="Distribuição de startups por setor e nível de inovação",
    labels=dict(x="Nível de inovação", y="Setor", color="Quantidade")
)
fig_heat.update_layout(template="plotly_white")
st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("💸 Relação entre investimento e crescimento")
fig_disp = px.scatter(
    df_f,
    x="investimento_recebido",
    y="crescimento_percentual",
    color="setor",
    size="faturamento",
    hover_data=["startup", "uf", "regiao", "estagio", "tecnologia_principal"],
    title="Investimento recebido x crescimento percentual",
    labels={
        "investimento_recebido": "Investimento recebido (R$)",
        "crescimento_percentual": "Crescimento percentual (%)",
        "setor": "Setor"
    }
)
fig_disp.update_layout(template="plotly_white")
st.plotly_chart(fig_disp, use_container_width=True)

corr = df_f[["investimento_recebido", "crescimento_percentual"]].corr().iloc[0, 1]
st.markdown(f"""
**Interpretação:** a correlação entre investimento e crescimento no recorte atual é **{corr:.2f}**.
Quando a correlação é próxima de zero, isso sugere que investimento, sozinho, não explica o crescimento.
Nesse caso, fatores como setor, tecnologia, estágio e nível de inovação também devem ser considerados.
""")

st.subheader("🧪 Tecnologias emergentes")
tec = df_f.groupby("tecnologia_principal").agg(
    quantidade=("startup", "count"),
    investimento=("investimento_recebido", "sum"),
    crescimento=("crescimento_percentual", "mean")
).reset_index().sort_values("quantidade", ascending=False)

fig_tec = px.bar(
    tec,
    x="tecnologia_principal",
    y="quantidade",
    title="Quantidade de registros por tecnologia principal",
    labels={"tecnologia_principal": "Tecnologia principal", "quantidade": "Quantidade de registros"}
)
fig_tec.update_layout(template="plotly_white", xaxis_tickangle=-35)
st.plotly_chart(fig_tec, use_container_width=True)

st.subheader("🏆 Ranking de startups")
ranking = df_f.groupby(["startup", "setor", "uf", "regiao"]).agg(
    investimento_total=("investimento_recebido", "sum"),
    faturamento_total=("faturamento", "sum"),
    crescimento_medio=("crescimento_percentual", "mean"),
    funcionarios_medios=("funcionarios", "mean")
).reset_index().sort_values("faturamento_total", ascending=False)

st.dataframe(ranking.head(30), use_container_width=True)

st.subheader("📋 Tabela dinâmica")
pivot = pd.pivot_table(
    df_f,
    values=["investimento_recebido", "faturamento", "crescimento_percentual", "funcionarios"],
    index=["regiao", "uf"],
    columns=["setor"],
    aggfunc={
        "investimento_recebido": "sum",
        "faturamento": "sum",
        "crescimento_percentual": "mean",
        "funcionarios": "mean"
    },
    fill_value=0
)
st.dataframe(pivot, use_container_width=True)

st.subheader("✅ Conclusão executiva")
st.markdown(f"""
A análise indica que o ecossistema de startups deve ser avaliado por múltiplos critérios: volume de empresas,
investimento, faturamento, crescimento e nível de inovação.

No recorte filtrado, o setor mais promissor por investimento é **{setor_promissor}**, o estado com maior força
financeira é **{estado_inovador}** e a startup com maior faturamento é **{startup_top}**.

**Recomendação:** priorizar políticas, programas de aceleração e estratégias de investimento em setores e regiões
que combinem alto investimento, crescimento consistente e maior concentração de inovação.
""")
