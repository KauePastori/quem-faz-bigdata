"""MVP demonstrativo: consumo local do CSV agregado exportado da Gold/Databricks.

Executar dentro da pasta mvp: python -m streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from validacao import DadosInvalidos, ler_categorias, resumir

st.set_page_config(
    page_title="Quem Faz | Painel de oportunidades",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded",
)

ARQUIVO = Path(__file__).resolve().parent / "dados" / "categorias_publicas.csv"

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {background: #0B1424;}
    [data-testid="stSidebar"] {background: #111D2D;}
    [data-testid="stMetric"] {
        border: 1px solid #26384D; border-radius: 14px;
        padding: 16px 18px; background: #142237;
    }
    [data-testid="stMetricLabel"] {color: #B5C7D8;}
    [data-testid="stMetricValue"] {color: #EAF8F4;}
    div[data-testid="stVerticalBlock"] h2, div[data-testid="stVerticalBlock"] h3 {color:#EAF8F4;}
    .qf-eyebrow {letter-spacing: .12em; color: #64D6B1; font-size: 12px; font-weight: 700;}
    .qf-title {font-size: 38px; font-weight: 800; line-height: 1.12; margin: 10px 0 8px 0; color:#F5F8FD;}
    .qf-sub {color: #B4C3D4; font-size: 15px; margin-bottom: 20px;}
    .qf-foot {color: #99ADC4; font-size: 13px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def carregar(modificacao_ns: int):
    """O mtime invalida o cache quando o CSV exportado é atualizado."""
    return ler_categorias(ARQUIVO)


if not ARQUIVO.is_file():
    st.error("CSV não encontrado. Coloque categorias_publicas.csv na pasta mvp/dados/.")
    st.stop()

try:
    registros = carregar(ARQUIVO.stat().st_mtime_ns)
except (DadosInvalidos, UnicodeError, OSError) as exc:
    st.error(f"Não foi possível carregar o CSV exportado: {exc}")
    st.stop()

st.sidebar.markdown("## 🧰 Quem Faz")
st.sidebar.caption("Inteligência de serviços • São Paulo")
st.sidebar.divider()
st.sidebar.markdown("### Filtros")
nomes = sorted((linha["categoria"] for linha in registros), key=str.casefold)
selecionadas = st.sidebar.multiselect(
    "Categorias",
    options=nomes,
    default=nomes,
    help="Os indicadores e gráficos serão recalculados usando apenas as categorias selecionadas.",
)
ordenacao = st.sidebar.selectbox(
    "Ordenar por",
    ["Mais pedidos", "Maior taxa de conclusão", "Mais contratações"],
)
st.sidebar.divider()
st.sidebar.info("🔎 Fonte: view Gold agregada do Databricks, exportada em CSV. Integração local, sem atualização automática.")
st.sidebar.warning("⚠️ PROVA DE CONCEITO — DADOS SIMULADOS. Os resultados não representam serviços reais em São Paulo.")

st.markdown('<div class="qf-eyebrow">QUEM FAZ · GLOBAL SOLUTION FIAP 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="qf-title">Visão de oportunidades</div>', unsafe_allow_html=True)
st.markdown('<div class="qf-sub">Indicadores da jornada de serviços, da solicitação à conclusão.</div>', unsafe_allow_html=True)

filtrados = [linha for linha in registros if linha["categoria"] in selecionadas]
if not filtrados:
    st.warning("Selecione ao menos uma categoria na barra lateral para visualizar os resultados.")
    st.stop()

totais = resumir(filtrados)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Solicitações", f'{totais["total_pedidos"]:,}'.replace(",", "."))
c2.metric("Com propostas", f'{totais["pedidos_com_proposta"]:,}'.replace(",", "."))
c3.metric("Contratados ou concluídos", f'{totais["pedidos_contratados"]:,}'.replace(",", "."))
c4.metric("Serviços concluídos", f'{totais["servicos_concluidos"]:,}'.replace(",", "."))

st.write("")
col_a, col_b = st.columns(2, gap="large")
with col_a:
    st.subheader("Solicitações por categoria")
    df = pd.DataFrame(filtrados)
    if ordenacao == "Mais pedidos":
        df = df.sort_values("total_pedidos", ascending=False)
    elif ordenacao == "Maior taxa de conclusão":
        df = df.sort_values("taxa_conclusao_percentual", ascending=False)
    else:
        df = df.sort_values("pedidos_contratados", ascending=False)
    st.bar_chart(
        df, x="categoria", y="total_pedidos", horizontal=True,
        sort=False, color="#39C99E", height=350,
        x_label="Pedidos", y_label="Categoria",
    )
with col_b:
    st.subheader("Taxa de conclusão por categoria")
    st.bar_chart(
        df, x="categoria", y="taxa_conclusao_percentual", horizontal=True,
        sort=False, color="#72A7FF", height=350,
        x_label="Percentual (%)", y_label="Categoria",
    )

st.subheader("Funil de desempenho")
a, b, c = st.columns(3)
with a:
    st.metric("Pedidos com propostas", f'{totais["taxa_propostas"]:.1f}%'.replace(".", ","))
    st.progress(totais["taxa_propostas"] / 100)
with b:
    st.metric("Taxa de contratação", f'{totais["taxa_contratacao"]:.1f}%'.replace(".", ","))
    st.progress(totais["taxa_contratacao"] / 100)
with c:
    st.metric("Taxa de conclusão", f'{totais["taxa_conclusao"]:.1f}%'.replace(".", ","))
    st.progress(totais["taxa_conclusao"] / 100)

st.subheader("Detalhamento por categoria")
exibicao = pd.DataFrame(filtrados)[[
    "categoria", "total_pedidos", "pedidos_com_proposta", "pedidos_contratados",
    "servicos_concluidos", "taxa_conclusao_percentual",
]].rename(columns={
    "categoria": "Categoria",
    "total_pedidos": "Pedidos",
    "pedidos_com_proposta": "Com propostas",
    "pedidos_contratados": "Contratados ou concluídos",
    "servicos_concluidos": "Concluídos",
    "taxa_conclusao_percentual": "Taxa de conclusão (%)",
})
st.dataframe(exibicao, hide_index=True, width="stretch")

st.download_button(
    "⬇ Exportar dados filtrados (CSV)",
    data=exibicao.to_csv(index=False).encode("utf-8-sig"),
    file_name="quem_faz_indicadores_filtrados.csv",
    mime="text/csv",
)
st.markdown(
    '<div class="qf-foot">Origem: Airflow → Databricks (Bronze / Prata / Ouro) → '
    'view agregada → exportação CSV → Streamlit. Nenhuma pessoa ou contratação real '
    'está representada.</div>',
    unsafe_allow_html=True,
)
