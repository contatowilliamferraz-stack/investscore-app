
import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import html

from tickers_eurozone import tickers
from tickers_setoriais_eurozone import setores
from data import get_data
from indicators import calculate_indicators
from score_eurozone import calculate_score
from simulador import (
    simular_aporte_retroativo,
    projetar_cenarios,
    obter_historico_precos_dividendos,
)


st.set_page_config(
    page_title="InvestScore Europa",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --bg: #142218;
    --bg-deep: #0e1912;
    --panel: #1c3025;
    --panel-line: #2c4536;
    --parchment: #ECE3CD;
    --parchment-dim: #A9B8A7;
    --gold: #C9A13B;
    --gold-bright: #E4BE5C;
    --sage: #8FBE97;
    --rust: #D07A46;
}
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
.stApp {
    background:
        radial-gradient(ellipse 900px 500px at 12% -8%, rgba(201,161,59,0.08), transparent 60%),
        radial-gradient(ellipse 700px 500px at 100% 5%, rgba(143,190,151,0.06), transparent 55%),
        linear-gradient(180deg, var(--bg-deep) 0%, var(--bg) 100%);
}
[data-testid="stMainBlockContainer"] {
    padding: 0.5rem 2rem 1rem 2rem;
    max-width: 1400px;
}
header[data-testid="stHeader"] {
    background-color: var(--bg) !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Fraunces', serif;
    color: var(--parchment);
}
.stApp p, .stApp span, .stApp label, .stApp div {
    color: var(--parchment-dim);
}
.stApp [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--gold-bright);
}
/* tabs */
.stApp button[data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--parchment-dim);
}
.stApp button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--gold-bright);
}
.stApp [data-baseweb="tab-highlight"] {
    background-color: var(--gold) !important;
}
/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: var(--bg-deep) !important;
    border-right: 1px solid var(--panel-line);
}
[data-testid="stSidebar"] * {
    color: var(--parchment-dim) !important;
}
/* WIDGETS NATIVOS (selectbox, input numerico, texto, slider, botao, checkbox) */
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="base-input"],
.stApp input,
.stApp textarea {
    background-color: var(--panel) !important;
    border-color: var(--panel-line) !important;
    color: var(--parchment) !important;
}
.stApp [data-baseweb="select"] span,
.stApp [data-baseweb="select"] div {
    color: var(--parchment) !important;
}
.stApp [role="listbox"],
.stApp [data-baseweb="popover"] {
    background-color: var(--panel) !important;
}
.stApp [role="option"] {
    background-color: var(--panel) !important;
    color: var(--parchment) !important;
}
.stApp button[kind="secondary"],
.stApp button[kind="primary"],
.stApp .stButton > button {
    background-color: var(--panel) !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold-bright) !important;
}
.stApp .stButton > button:hover {
    background-color: var(--gold) !important;
    color: var(--bg-deep) !important;
}
.stApp .stButton > button p {
    color: inherit !important;
}
.stApp [data-testid="stNumberInputStepDown"],
.stApp [data-testid="stNumberInputStepUp"] {
    background-color: var(--panel) !important;
    color: var(--parchment) !important;
    border-color: var(--panel-line) !important;
}
.stApp [data-baseweb="slider"] [role="slider"] {
    background-color: var(--gold) !important;
}
.stApp [data-baseweb="checkbox"] label span:first-child {
    background-color: var(--panel) !important;
    border-color: var(--panel-line) !important;
}
/* HERO */
.hero {
    padding: 22px 26px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    border-left: 3px solid var(--gold);
    margin: 22px 0 12px 0;
}
.hero h1 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    color: var(--parchment);
}
.hero div {
    color: var(--parchment-dim);
    font-family: 'IBM Plex Sans', sans-serif;
}
.brand-mark {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    background: var(--gold);
    transform: rotate(45deg);
    margin-right: 10px;
    flex-shrink: 0;
}
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gold-bright);
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
}
.sidebar-brand span.name {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: var(--parchment);
}
.badge-blue {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: var(--gold-bright);
    background: rgba(201,161,59,0.12);
    border: 1px solid rgba(201,161,59,0.35);
    padding: 3px 10px;
    border-radius: 3px;
    margin-top: 6px;
}
/* TITULOS */
.section-title {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    margin-top: 12px;
    margin-bottom: 6px;
    font-weight: 600;
    color: var(--parchment);
}
/* CARDS */
.card {
    padding: 14px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    margin: 34px 0 14px 0;
}
.kpi-box {
    padding: 12px 14px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    margin-bottom: 10px;
}
.kpi-card {
    padding: 16px 18px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    min-height: 126px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--parchment-dim);
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    margin-bottom: 10px;
    font-weight: 500;
}
.kpi-value {
    font-family: 'Fraunces', serif;
    font-size: 2.25rem;
    line-height: 1;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--parchment);
}
.kpi-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: var(--gold-bright);
    font-weight: 500;
}
.insight-box {
    padding: 14px 16px;
    border-radius: 4px;
    background: var(--bg-deep);
    border: 1px solid var(--panel-line);
    border-left: 3px solid var(--sage);
    margin-bottom: 10px;
    min-height: 108px;
    display: flex;
    align-items: center;
}
.insight-box p {
    margin: 0;
    color: var(--parchment-dim);
    font-size: 0.94rem;
    line-height: 1.55;
    font-weight: 500;
}
.insight-box strong {
    color: var(--parchment);
}
.signal-good { color: var(--sage); font-weight: 600; }
.signal-mid { color: var(--gold-bright); font-weight: 600; }
.signal-bad { color: var(--rust); font-weight: 600; }
.bar-outer {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: var(--panel-line);
    overflow: hidden;
    margin-top: 6px;
    margin-bottom: 10px;
}
.bar-inner {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--sage), var(--gold-bright));
}
.asset-card {
    padding: 16px 18px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    box-shadow: 0 12px 28px rgba(0,0,0,0.28);
    min-height: 320px;
    margin-bottom: 8px;
}
.asset-sector { color: var(--parchment-dim); font-size: 0.78rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; margin: 0 0 8px 0; font-family: 'IBM Plex Mono', monospace; }
.asset-ticker { color: var(--parchment); font-family: 'Fraunces', serif; font-style: italic; font-size: 1.15rem; font-weight: 600; margin: 0 0 8px 0; }
.asset-level { color: var(--gold-bright); font-size: 0.85rem; font-weight: 600; letter-spacing: 0.03em; margin: 0 0 14px 0; font-family: 'IBM Plex Mono', monospace; }
.asset-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.asset-box { padding: 10px 12px; border-radius: 4px; background: var(--bg-deep); border: 1px solid var(--panel-line); }
.asset-box-label { color: var(--parchment-dim); font-size: 0.74rem; font-weight: 500; margin-bottom: 4px; font-family: 'IBM Plex Mono', monospace; }
.asset-box-value { color: var(--parchment); font-family: 'IBM Plex Mono', monospace; font-size: 1.0rem; font-weight: 600; }
.asset-line { color: var(--parchment-dim); font-size: 0.91rem; margin: 0 0 7px 0; }
.asset-divider { height: 1px; background: var(--panel-line); margin: 12px 0; }
.tese-card {
    padding: 14px 16px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    border-left: 3px solid var(--gold);
    margin-bottom: 12px;
}
.tese-title { color: var(--parchment); font-family: 'Fraunces', serif; font-size: 1.02rem; font-weight: 600; margin-bottom: 8px; }
.tese-line { color: var(--parchment-dim); font-size: 0.90rem; margin-bottom: 5px; }
.compare-mini-card {
    padding: 14px 16px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    min-height: 120px;
    margin-bottom: 8px;
}
.compare-mini-title { color: var(--parchment); font-family: 'Fraunces', serif; font-size: 1.0rem; font-weight: 600; margin-bottom: 8px; }
.compare-mini-line { color: var(--parchment-dim); font-size: 0.90rem; margin-bottom: 5px; }
.profile-card {
    padding: 16px 18px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    box-shadow: 0 12px 28px rgba(0,0,0,0.24);
    min-height: 220px;
}
.profile-title { color: var(--parchment); font-family: 'Fraunces', serif; font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; }
.profile-line { color: var(--parchment-dim); font-size: 0.91rem; margin-bottom: 6px; }
.portfolio-final-card {
    margin-top: 24px;
    margin-bottom: 14px;
    padding: 20px 22px;
    border-radius: 4px;
    background: var(--panel);
    border: 1px solid var(--panel-line);
    box-shadow: 0 12px 28px rgba(0,0,0,0.24);
}
.portfolio-final-title {
    color: var(--parchment);
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 10px;
}
.portfolio-final-divider {
    height: 1px;
    background: var(--panel-line);
    margin: 12px 0;
}
.portfolio-final-line {
    color: var(--parchment-dim);
    font-size: 0.92rem;
    margin-bottom: 8px;
}
.portfolio-final-section {
    color: var(--gold-bright);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 14px 0 8px 0;
}
</style>
""", unsafe_allow_html=True)


def fmt_moeda(valor):
    try:
        valor = float(valor)
        return f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def fmt_delta_moeda(valor):
    try:
        valor = float(valor)
        sinal = "+" if valor > 0 else ""
        return f"{sinal}{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def fmt_pct(valor):
    try:
        valor = float(valor)
        return f"{valor:.1f}%".replace(".", ",")
    except Exception:
        return "—"


def margem_seguranca_exibicao(item):
    try:
        preco_atual = float(item.get("preco_atual", 0) or 0)
        preco_teto = float(item.get("preco_teto", 0) or 0)

        if preco_teto <= 0:
            return "Sem base suficiente"

        margem = ((preco_teto - preco_atual) / preco_teto) * 100

        if margem < -50:
            return "Muito acima do teto"

        return f"{margem:.1f}%".replace(".", ",")

    except Exception:
        return "—"


def nota_fonte_dados():
    st.markdown(
        """
        <div style="
            padding:10px 12px;
            border-radius:12px;
            background: rgba(59,130,246,0.08);
            border: 1px solid rgba(59,130,246,0.20);
            margin-top: 10px;
            font-size: 0.9rem;
        ">
            <strong>Fonte dos dados:</strong> preços e indicadores obtidos via Yahoo Finance.
            Pequenas diferenças podem ocorrer em relação ao fechamento oficial.
        </div>
        """,
        unsafe_allow_html=True
    )


def observacao_classe_acao(item):
    ticker = str(item.get("ticker", ""))
    if ticker.endswith("3.SA") or ticker.endswith("4.SA"):
        return "Pequenas variações entre classes de ações do mesmo grupo são esperadas."
    return ""


def explicacao_comparador(item_1, item_2):
    pontos = []

    if item_1.get("score", 0) > item_2.get("score", 0):
        pontos.append(f"{item_1['ticker']} lidera em score ({item_1['score']} vs {item_2['score']}).")
    elif item_2.get("score", 0) > item_1.get("score", 0):
        pontos.append(f"{item_2['ticker']} lidera em score ({item_2['score']} vs {item_1['score']}).")
    else:
        pontos.append("As duas empresas apresentam score equivalente no modelo atual.")

    p1 = float(item_1.get("preco_atual", 0) or 0)
    p2 = float(item_2.get("preco_atual", 0) or 0)
    t1 = float(item_1.get("preco_teto", 0) or 0)
    t2 = float(item_2.get("preco_teto", 0) or 0)

    if t1 > 0 and t2 > 0:
        d1 = abs(p1 - t1)
        d2 = abs(p2 - t2)
        if d1 < d2:
            pontos.append(f"{item_1['ticker']} está mais próximo do seu preço teto teórico.")
        elif d2 < d1:
            pontos.append(f"{item_2['ticker']} está mais próximo do seu preço teto teórico.")
        else:
            pontos.append("As duas empresas estão a uma distância semelhante do preço teto.")

    m1 = item_1.get("margem_seguranca")
    m2 = item_2.get("margem_seguranca")
    if m1 is not None and m2 is not None:
        if m1 > m2:
            pontos.append(f"{item_1['ticker']} oferece maior margem de segurança na leitura atual.")
        elif m2 > m1:
            pontos.append(f"{item_2['ticker']} oferece maior margem de segurança na leitura atual.")
        else:
            pontos.append("As duas empresas têm margem de segurança muito próxima.")

    if item_1.get("setor") == item_2.get("setor"):
        pontos.append("As empresas pertencem ao mesmo setor, então a comparação tende a ser mais justa.")
    else:
        pontos.append("As empresas estão em setores diferentes, então o comparativo deve ser lido com contexto.")

    return pontos


def mensagem_vencedor_comparador(item_1, item_2):
    vencedor = vencedor_comparativo(item_1, item_2)
    if vencedor == "Empate":
        return "As empresas apresentam equilíbrio nos principais critérios do comparador."
    return f"{vencedor} se destaca no comparativo quantitativo atual."


def classificar(score):
    if score >= 80:
        return "Alta"
    elif score >= 60:
        return "Média"
    return "Baixa"


def descobrir_setor(ticker):
    for nome_setor, lista_tickers in setores.items():
        if ticker in lista_tickers:
            return nome_setor
    return "Outros"


def cor_nivel(nivel):
    if nivel == "Alta":
        return "🟢"
    elif nivel == "Média":
        return "🟡"
    return "🔴"



def rotulo_nivel_card(nivel):
    nivel_txt = str(nivel).strip().lower()
    mapa = {
        "alta": "ALTA",
        "média": "MÉDIA",
        "media": "MÉDIA",
        "mídia": "MÉDIA",
        "baixa": "BAIXA",
    }
    return mapa.get(nivel_txt, str(nivel).upper())

def render_dashboard_info_card(texto, titulo=None):
    prefixo = f"<strong>{esc_html(titulo)}:</strong> " if titulo else ""
    st.markdown(
        f'<div class="insight-box"><p>{prefixo}{esc_html(texto)}</p></div>',
        unsafe_allow_html=True,
    )

def badge_nivel(nivel):
    if nivel == "Alta":
        return "<span class='badge-green'>ALTA QUALIDADE</span>"
    elif nivel == "Média":
        return "<span class='badge-yellow'>QUALIDADE MODERADA</span>"
    return "<span class='badge-red'>BAIXA QUALIDADE</span>"


def badge_perfil(perfil):
    if perfil == "Conservador":
        return "<span class='badge-green'>PERFIL CONSERVADOR</span>"
    elif perfil == "Moderado":
        return "<span class='badge-yellow'>PERFIL MODERADO</span>"
    return "<span class='badge-red'>PERFIL AGRESSIVO</span>"


def explicacao_perfil(perfil):
    if perfil == "Conservador":
        return "Prioriza pontuação alta, preço mais próximo ou abaixo do teto teórico e maior seletividade."
    elif perfil == "Moderado":
        return "Busca equilíbrio entre qualidade, diversificação e flexibilidade de entrada."
    return "Aceita maior amplitude de ativos para capturar oportunidades com mais risco relativo."


def insight(item):
    if item["nivel"] == "Alta":
        return "Empresa bem posicionada segundo os critérios quantitativos do modelo."
    elif item["nivel"] == "Média":
        return "Empresa consistente, mas sem destaque máximo neste momento."
    return "Atratividade mais baixa dentro da leitura atual do modelo."


def calcular_preco_teto(dividendo_anual, dy_alvo=0.04):
    if dividendo_anual <= 0:
        return 0
    return dividendo_anual / dy_alvo


def status_preco(preco_atual, preco_teto):
    if preco_teto <= 0:
        return "Sem base suficiente"
    if preco_atual <= preco_teto * 0.90:
        return "Abaixo do teto"
    elif preco_atual <= preco_teto * 1.05:
        return "Próximo do teto"
    return "Acima do teto"


def vencedor_comparativo(item1, item2):
    pontos_1 = 0
    pontos_2 = 0

    if item1["score"] > item2["score"]:
        pontos_1 += 1
    elif item2["score"] > item1["score"]:
        pontos_2 += 1

    if item1["preco_teto"] > 0 and item2["preco_teto"] > 0:
        dist_1 = abs(item1["preco_atual"] - item1["preco_teto"])
        dist_2 = abs(item2["preco_atual"] - item2["preco_teto"])
        if dist_1 < dist_2:
            pontos_1 += 1
        elif dist_2 < dist_1:
            pontos_2 += 1

    if pontos_1 > pontos_2:
        return item1["ticker"]
    elif pontos_2 > pontos_1:
        return item2["ticker"]
    return "Empate"


def texto_preco(item):
    partes = []
    if item.get("preco_atual", 0) > 0:
        partes.append(f"Preço atual: {fmt_moeda(item['preco_atual'])}")
    if item.get("ultimo_fechamento", 0) > 0:
        partes.append(f"Último fechamento: {fmt_moeda(item['ultimo_fechamento'])}")
    if item.get("preco_teto", 0) > 0:
        partes.append(f"Preço teto: {fmt_moeda(item['preco_teto'])}")
    return " | ".join(partes) if partes else "Preço não disponível no momento"


def render_linha_preco(item):
    st.text(texto_preco(item))


def render_resumo_empresa(item, *, mostrar_badge=True, mostrar_insight=True, preco_em_texto=False):
    st.markdown(f"**{item['ticker']}** {cor_nivel(item['nivel'])}")
    if mostrar_badge:
        st.markdown(badge_nivel(item["nivel"]), unsafe_allow_html=True)
    st.caption(f"Setor: {item['setor']}")
    if mostrar_insight:
        st.markdown(f"**{insight(item)}**")
    if preco_em_texto:
        render_linha_preco(item)
    else:
        st.caption(texto_preco(item))
    st.caption(f"Status: {status_preco(item['preco_atual'], item['preco_teto'])}")


def render_card_top3(item):
    with st.container(border=True):
        st.markdown(f"**{item['ticker']}** {cor_nivel(item['nivel'])}")
        st.markdown(f"**{rotulo_nivel_card(item['nivel'])}**")
        st.caption(f"Setor: {item['setor']}")
        st.caption(f"Pontuação: {item['score']}")
        st.caption(f"Status: {status_preco(item['preco_atual'], item['preco_teto'])}")


def selecionar_top_diversificado(resultados, limite=4, max_por_setor=1):
    selecionados = []
    contagem_setor = {}

    for item in resultados:
        setor = item.get("setor", "Outros")
        atual = contagem_setor.get(setor, 0)

        if atual < max_por_setor:
            selecionados.append(item)
            contagem_setor[setor] = atual + 1

        if len(selecionados) >= limite:
            break

    return selecionados


def render_card_destaque_setorial(item):
    render_asset_card(item, mostrar_setor=True, mostrar_fechamento=True, mostrar_variacao=False)

def render_nota_final():
    st.markdown("<div class='top3-spacer'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <strong>Nota final:</strong>
        o InvestScore organiza indicadores financeiros em uma leitura visual e objetiva para apoiar análise.
        O conteúdo não representa recomendação, promessa de rentabilidade ou orientação personalizada.
        A decisão final é sempre do investidor.
    </div>
    """, unsafe_allow_html=True)




def explicacao_comparador(item_1, item_2):
    pontos = []

    if item_1.get("score", 0) > item_2.get("score", 0):
        pontos.append(f"{item_1['ticker']} lidera em score ({item_1['score']} vs {item_2['score']}).")
    elif item_2.get("score", 0) > item_1.get("score", 0):
        pontos.append(f"{item_2['ticker']} lidera em score ({item_2['score']} vs {item_1['score']}).")
    else:
        pontos.append("As duas empresas apresentam score equivalente no modelo atual.")

    p1 = float(item_1.get("preco_atual", 0) or 0)
    p2 = float(item_2.get("preco_atual", 0) or 0)
    t1 = float(item_1.get("preco_teto", 0) or 0)
    t2 = float(item_2.get("preco_teto", 0) or 0)

    if t1 > 0 and t2 > 0:
        d1 = abs(p1 - t1)
        d2 = abs(p2 - t2)
        if d1 < d2:
            pontos.append(f"{item_1['ticker']} está mais próximo do seu preço teto teórico.")
        elif d2 < d1:
            pontos.append(f"{item_2['ticker']} está mais próximo do seu preço teto teórico.")
        else:
            pontos.append("As duas empresas estão a uma distância semelhante do preço teto.")

    m1 = item_1.get("margem_seguranca")
    m2 = item_2.get("margem_seguranca")
    if m1 is not None and m2 is not None:
        if m1 > m2:
            pontos.append(f"{item_1['ticker']} oferece maior margem de segurança na leitura atual.")
        elif m2 > m1:
            pontos.append(f"{item_2['ticker']} oferece maior margem de segurança na leitura atual.")
        else:
            pontos.append("As duas empresas têm margem de segurança muito próxima.")

    if item_1.get("setor") == item_2.get("setor"):
        pontos.append("As empresas pertencem ao mesmo setor, então a comparação tende a ser mais justa.")
    else:
        pontos.append("As empresas estão em setores diferentes, então o comparativo deve ser lido com contexto.")

    return pontos


def mensagem_vencedor_comparador(item_1, item_2):
    vencedor = vencedor_comparativo(item_1, item_2)
    if vencedor == "Empate":
        return "As empresas apresentam equilíbrio nos principais critérios do comparador."
    return f"{vencedor} se destaca no comparativo quantitativo atual."



def calcular_margem_numerica(item):
    try:
        preco_atual = float(item.get("preco_atual", 0) or 0)
        preco_teto = float(item.get("preco_teto", 0) or 0)
        if preco_teto <= 0:
            return None
        return ((preco_teto - preco_atual) / preco_teto) * 100
    except Exception:
        return None


def prioridade_ativo(item):
    score = item.get("score", 0)
    margem = calcular_margem_numerica(item)
    status = status_preco(item.get("preco_atual", 0), item.get("preco_teto", 0))
    if score >= 85 and status == "Abaixo do teto" and margem is not None and margem >= 15:
        return "Prioridade Alta"
    if score >= 70 and margem is not None and margem >= 5:
        return "Prioridade Média"
    return "Observação"


def faixa_acao(item):
    score = item.get("score", 0)
    margem = calcular_margem_numerica(item)
    status = status_preco(item.get("preco_atual", 0), item.get("preco_teto", 0))
    if status == "Abaixo do teto" and score >= 80 and margem is not None and margem >= 12:
        return "Mais próxima de oportunidade"
    if score >= 70:
        return "Boa qualidade, acompanhar"
    return "Exige mais cautela"


def resumo_carteira(carteira):
    if not carteira:
        return {"setores":0,"abaixo_teto":0,"margem_media":None,"maior_score_ticker":"—","concentracao":"—","tese":"Sem ativos para análise."}
    setores = len(set(item["setor"] for item in carteira))
    abaixo_teto = sum(1 for item in carteira if status_preco(item["preco_atual"], item["preco_teto"]) == "Abaixo do teto")
    margens = [calcular_margem_numerica(item) for item in carteira]
    margens = [m for m in margens if m is not None]
    margem_media = round(sum(margens) / len(margens), 1) if margens else None
    melhor = max(carteira, key=lambda x: x["score"])
    contagem = {}
    for item in carteira:
        contagem[item["setor"]] = contagem.get(item["setor"], 0) + 1
    setor_top, qtd_top = max(contagem.items(), key=lambda kv: kv[1])
    concentracao = f"{setor_top} ({qtd_top}/{len(carteira)})"
    tese = f"Carteira com {setores} setores, {abaixo_teto}/{len(carteira)} ativos abaixo do teto"
    if margem_media is not None:
        tese += f" e margem média de segurança de {str(margem_media).replace('.', ',')}%."
    else:
        tese += "."
    return {"setores":setores,"abaixo_teto":abaixo_teto,"margem_media":margem_media,"maior_score_ticker":melhor["ticker"],"concentracao":concentracao,"tese":tese}


def html_label_prioridade(texto):
    cls = "signal-good" if texto == "Prioridade Alta" else ("signal-mid" if texto == "Prioridade Média" else "signal-bad")
    return f"<span class='{cls}'>{texto}</span>"


def pontuacao_criterios(item_a, item_b):
    placar_a = 0; placar_b = 0; linhas = []
    if item_a["score"] > item_b["score"]:
        placar_a += 1; linhas.append(("Pontuação", item_a["ticker"]))
    elif item_b["score"] > item_a["score"]:
        placar_b += 1; linhas.append(("Pontuação", item_b["ticker"]))
    else:
        linhas.append(("Pontuação", "Empate"))
    try:
        d_a = abs(float(item_a["preco_atual"]) - float(item_a["preco_teto"]))
        d_b = abs(float(item_b["preco_atual"]) - float(item_b["preco_teto"]))
        if d_a < d_b:
            placar_a += 1; linhas.append(("Proximidade do teto", item_a["ticker"]))
        elif d_b < d_a:
            placar_b += 1; linhas.append(("Proximidade do teto", item_b["ticker"]))
        else:
            linhas.append(("Proximidade do teto", "Empate"))
    except Exception:
        linhas.append(("Proximidade do teto", "Empate"))
    m_a = calcular_margem_numerica(item_a); m_b = calcular_margem_numerica(item_b)
    if m_a is not None and m_b is not None:
        if m_a > m_b:
            placar_a += 1; linhas.append(("Margem de segurança", item_a["ticker"]))
        elif m_b > m_a:
            placar_b += 1; linhas.append(("Margem de segurança", item_b["ticker"]))
        else:
            linhas.append(("Margem de segurança", "Empate"))
    else:
        linhas.append(("Margem de segurança", "Empate"))
    s_a = status_preco(item_a["preco_atual"], item_a["preco_teto"]); s_b = status_preco(item_b["preco_atual"], item_b["preco_teto"])
    ordem = {"Abaixo do teto": 3, "Próximo do teto": 2, "Acima do teto": 1, "Sem base suficiente": 0}
    if ordem.get(s_a, 0) > ordem.get(s_b, 0):
        placar_a += 1; linhas.append(("Status de preço", item_a["ticker"]))
    elif ordem.get(s_b, 0) > ordem.get(s_a, 0):
        placar_b += 1; linhas.append(("Status de preço", item_b["ticker"]))
    else:
        linhas.append(("Status de preço", "Empate"))
    return placar_a, placar_b, linhas


def vencedor_por_placar(item_a, item_b):
    placar_a, placar_b, _ = pontuacao_criterios(item_a, item_b)
    if placar_a > placar_b:
        return item_a["ticker"], placar_a, placar_b
    if placar_b > placar_a:
        return item_b["ticker"], placar_a, placar_b
    return "Empate", placar_a, placar_b


def mensagem_vencedor_consistente(item_a, item_b):
    vencedor, placar_a, placar_b = vencedor_por_placar(item_a, item_b)
    if vencedor == "Empate":
        return "As empresas apresentaram equilíbrio nos principais critérios do comparador."
    return f"{vencedor} se destaca no comparativo quantitativo atual ({placar_a}x{placar_b})."


def conclusao_executiva(item_a, item_b):
    partes=[]
    if item_a["score"] > item_b["score"]: partes.append(f"{item_a['ticker']} lidera em pontuação")
    elif item_b["score"] > item_a["score"]: partes.append(f"{item_b['ticker']} lidera em pontuação")
    else: partes.append("as empresas estão empatadas em pontuação")
    m_a = calcular_margem_numerica(item_a); m_b = calcular_margem_numerica(item_b)
    if m_a is not None and m_b is not None:
        if m_a > m_b: partes.append(f"{item_a['ticker']} entrega melhor margem de segurança")
        elif m_b > m_a: partes.append(f"{item_b['ticker']} entrega melhor margem de segurança")
    if item_a["setor"] == item_b["setor"]: partes.append("a comparação é direta por estarem no mesmo setor")
    else: partes.append("a comparação exige contexto por serem de setores diferentes")
    return "; ".join(partes).capitalize() + "."


def barra_margem_html(item):
    m = calcular_margem_numerica(item)
    if m is None:
        return "<div style='font-size:0.85rem;'>Margem indisponível</div>"
    largura = max(0, min(100, m))
    return f"""
    <div style='font-size:0.85rem;'>Distância até o teto: {fmt_pct(m)}</div>
    <div class='bar-outer'><div class='bar-inner' style='width:{largura}%;'></div></div>
    """


def vantagens_comparativas(item_a, item_b):
    vantagens = []

    if item_a.get("score", 0) > item_b.get("score", 0):
        vantagens.append(f"Pontuação superior ({item_a['score']} vs {item_b['score']}).")

    try:
        dist_a = abs(float(item_a.get("preco_atual", 0) or 0) - float(item_a.get("preco_teto", 0) or 0))
        dist_b = abs(float(item_b.get("preco_atual", 0) or 0) - float(item_b.get("preco_teto", 0) or 0))
        if dist_a < dist_b:
            vantagens.append("Preço atual mais próximo do preço teto teórico.")
    except Exception:
        pass

    margem_a = calcular_margem_numerica(item_a)
    margem_b = calcular_margem_numerica(item_b)
    if margem_a is not None and margem_b is not None and margem_a > margem_b:
        vantagens.append(f"Maior margem de segurança ({fmt_pct(margem_a)} vs {fmt_pct(margem_b)}).")

    status_a = status_preco(item_a.get("preco_atual", 0), item_a.get("preco_teto", 0))
    status_b = status_preco(item_b.get("preco_atual", 0), item_b.get("preco_teto", 0))
    ordem = {"Abaixo do teto": 3, "Próximo do teto": 2, "Acima do teto": 1, "Sem base suficiente": 0}
    if ordem.get(status_a, 0) > ordem.get(status_b, 0):
        vantagens.append(f"Melhor posicionamento de preço ({status_a}).")

    if item_a.get("setor") == item_b.get("setor"):
        vantagens.append("Comparação direta dentro do mesmo setor.")

    if not vantagens:
        vantagens.append("Leitura equilibrada, sem vantagem isolada dominante nos critérios principais.")

    return vantagens



def interpretacao_modelo(item):
    try:
        score = item.get("score", 0)
        preco = float(item.get("preco_atual", 0) or 0)
        teto = float(item.get("preco_teto", 0) or 0)
        margem = calcular_margem_numerica(item)

        leituras = []
        if score >= 85:
            leituras.append("Score elevado dentro do modelo")
        elif score >= 70:
            leituras.append("Score consistente")
        else:
            leituras.append("Score mais baixo no modelo")

        if margem is not None:
            if margem >= 15:
                leituras.append("Margem confortável")
            elif margem >= 5:
                leituras.append("Margem moderada")
            else:
                leituras.append("Margem reduzida")

        leituras.append(f"Status: {status_preco(preco, teto)}")
        return " | ".join(leituras)
    except Exception:
        return "Sem interpretação disponível"


def alerta_carteira(carteira):
    try:
        setores_map = {}
        for item in carteira:
            setores_map[item["setor"]] = setores_map.get(item["setor"], 0) + 1

        total = len(carteira)
        alertas = []
        for setor, qtd in setores_map.items():
            if total > 0 and qtd / total > 0.4:
                alertas.append(f"Alta concentração no setor {setor}")

        oportunidades = sum(
            1 for item in carteira
            if status_preco(item["preco_atual"], item["preco_teto"]) == "Abaixo do teto"
        )
        if oportunidades >= 2:
            alertas.append("Múltiplos ativos abaixo do teto na carteira")

        return alertas
    except Exception:
        return []

def filtrar_carteira(perfil, resultados):
    """
    Separa os resultados em três carteiras SEM SOBREPOSIÇÃO entre si — ou
    seja, uma empresa que já qualifica para o perfil Conservador nunca
    volta a aparecer no Moderado ou no Agressivo, e assim por diante.

    Antes desta correção, os três perfis eram apenas o mesmo ranking por
    pontuação com um corte de score diferente — e como o corte só importa
    se de facto excluir alguém das 8 primeiras posições, à medida que mais
    empresas eram carregadas o Moderado (score >= 70) e o Agressivo (sem
    filtro) convergiam para exatamente a mesma lista de 8 empresas, porque
    as 8 melhores por pontuação já pontuavam acima de 70 de qualquer forma.
    """
    todos_ordenados = sorted(resultados, key=lambda x: x["score"], reverse=True)

    conservadores = [
        x for x in todos_ordenados
        if x["score"] >= 80
        and x["preco_teto"] > 0
        and x["preco_atual"] <= x["preco_teto"]
    ]
    tickers_conservadores = {x["ticker"] for x in conservadores}

    moderados = [
        x for x in todos_ordenados
        if x["score"] >= 65
        and x["ticker"] not in tickers_conservadores
    ]
    tickers_moderados = {x["ticker"] for x in moderados}

    agressivos = [
        x for x in todos_ordenados
        if x["ticker"] not in tickers_conservadores
        and x["ticker"] not in tickers_moderados
    ]

    if perfil == "Conservador":
        base = conservadores
    elif perfil == "Moderado":
        base = moderados
    else:
        base = agressivos

    carteira = []
    setores_usados = {}

    for item in base:
        setor = item["setor"]
        if setores_usados.get(setor, 0) < 2:
            carteira.append(item)
            setores_usados[setor] = setores_usados.get(setor, 0) + 1

        if len(carteira) == 8:
            break

    return carteira


@st.cache_data(ttl=14400, show_spinner=False)
def carregar_resultados(tickers_para_carregar):
    resultados = []

    for i, ticker in enumerate(tickers_para_carregar):
        try:
            if i > 0:
                time.sleep(0.15)
            data = get_data(ticker)
            ind = calculate_indicators(data)

            setor = descobrir_setor(ticker)
            ind["Setor"] = setor

            score = calculate_score(ind)
            nivel = classificar(score)

            preco_atual = ind.get("CurrentPrice", 0)
            ultimo_fechamento = ind.get("PreviousClose", 0)
            dividendo_anual = ind.get("AnnualDividend", 0)
            preco_teto = calcular_preco_teto(dividendo_anual, 0.04)

            variacao_abs = 0
            variacao_pct = 0
            if preco_atual > 0 and ultimo_fechamento > 0:
                variacao_abs = preco_atual - ultimo_fechamento
                variacao_pct = (variacao_abs / ultimo_fechamento) * 100

            dividend_yield_pct = 0
            if preco_atual > 0 and dividendo_anual > 0:
                dividend_yield_pct = (dividendo_anual / preco_atual) * 100

            resultados.append({
                "ticker": ticker,
                "score": score,
                "nivel": nivel,
                "setor": ind.get("Setor") or "Outros",
                "preco_atual": preco_atual,
                "ultimo_fechamento": ultimo_fechamento,
                "preco_teto": preco_teto,
                "variacao_abs": variacao_abs,
                "variacao_pct": variacao_pct,
                "dividendo_anual": dividendo_anual,
                "dividend_yield_pct": dividend_yield_pct,
            })
        except Exception:
            continue

    return sorted(resultados, key=lambda x: x["score"], reverse=True)


st.markdown("""
<div class='hero'>
    <div class="hero-eyebrow"><span class="brand-mark"></span>Método Barsi · Zona Euro</div>
    <h1>InvestScore Europa</h1>
    <div>Análise de ações da Zona Euro, objetiva e profissional</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><span class='brand-mark'></span><span class='name'>InvestScore Europa</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("<span class='badge-blue'>ZONA EURO</span>", unsafe_allow_html=True)

total_tickers = len(tickers)
# Sem limite artificial: carrega o universo completo. Combinado com o
# cache de 4h, as tentativas automáticas em caso de bloqueio (429) e a
# pausa entre pedidos em data.py/carregar_resultados, o risco de bloqueio
# pelo Yahoo Finance é mitigado sem sacrificar cobertura. Se voltares a
# ver o erro "Nenhum resultado foi gerado", isso é sinal de que o Yahoo
# bloqueou mesmo assim — nesse caso, reduzir este valor é o primeiro
# ajuste a fazer.
LIMITE_TICKERS = total_tickers
limite = min(LIMITE_TICKERS, total_tickers)

if len(tickers) > limite:
    tickers_para_carregar = tickers[:limite]
else:
    tickers_para_carregar = tickers

with st.spinner("Carregando dados do Yahoo Finance..."):
    resultados = carregar_resultados(tuple(tickers_para_carregar))

if not resultados:
    st.error("Nenhum resultado foi gerado. Verifique os dados do projeto ou a conexão com o Yahoo Finance.")
    st.stop()

melhor = resultados[0]


def selecionar_abaixo_teto(resultados, limite=6):
    filtrados = [
        item for item in resultados
        if status_preco(item.get("preco_atual", 0), item.get("preco_teto", 0)) == "Abaixo do teto"
    ]
    filtrados = sorted(
        filtrados,
        key=lambda x: (
            -(calcular_margem_numerica(x) if calcular_margem_numerica(x) is not None else -9999),
            -x.get("score", 0)
        )
    )
    return filtrados[:limite]


def resumo_setores_dashboard(resultados):
    setores = {}
    for item in resultados:
        setor = item.get("setor", "Outros")
        if setor not in setores:
            setores[setor] = {"qtd": 0, "score_total": 0, "abaixo_teto": 0, "melhor": None}
        setores[setor]["qtd"] += 1
        setores[setor]["score_total"] += item.get("score", 0)
        if status_preco(item.get("preco_atual", 0), item.get("preco_teto", 0)) == "Abaixo do teto":
            setores[setor]["abaixo_teto"] += 1
        if setores[setor]["melhor"] is None or item.get("score", 0) > setores[setor]["melhor"].get("score", 0):
            setores[setor]["melhor"] = item

    linhas = []
    for setor, dados in setores.items():
        linhas.append({
            "Setor": setor,
            "Empresas": dados["qtd"],
            "Score Médio": round(dados["score_total"] / dados["qtd"], 1) if dados["qtd"] else 0,
            "Abaixo do Teto": dados["abaixo_teto"],
            "Melhor Ativo": dados["melhor"]["ticker"] if dados["melhor"] else "—"
        })
    return pd.DataFrame(sorted(linhas, key=lambda x: x["Score Médio"], reverse=True))


def alertas_dashboard(resultados):
    alertas = []
    abaixo_teto = selecionar_abaixo_teto(resultados, limite=len(resultados))
    if len(abaixo_teto) >= 5:
        alertas.append(f"{len(abaixo_teto)} ativos estão abaixo do teto teórico no momento.")
    setores_df = resumo_setores_dashboard(resultados)
    if not setores_df.empty:
        top_setor = setores_df.iloc[0]
        alertas.append(f"Setor mais forte agora: {top_setor['Setor']} (score médio {str(top_setor['Score Médio']).replace('.', ',')}).")
    melhor = max(resultados, key=lambda x: x["score"])
    alertas.append(f"Melhor score atual: {melhor['ticker']} ({melhor['score']}).")
    return alertas[:3]


def render_card_dashboard(item, mostrar_setor=True):
    render_asset_card(item, mostrar_setor=mostrar_setor, mostrar_fechamento=False, mostrar_variacao=False)

def render_kpi_card(titulo, valor, subtitulo=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-sub">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_dashboard_diversificacao(resultados):
    try:
        setores_df = resumo_setores_dashboard(resultados)
        if setores_df.empty:
            return "Sem leitura setorial suficiente para diversificação."
        top_setor = setores_df.iloc[0]
        participacao = round((top_setor["Empresas"] / len(resultados)) * 100, 1) if len(resultados) else 0
        return (
            f"{top_setor['Setor']} lidera o modelo, mas representa {str(participacao).replace('.', ',')}% "
            f"das empresas acompanhadas — vale equilibrar leitura com outros setores."
        )
    except Exception:
        return "Sem leitura de diversificação disponível."


def altura_dataframe_dinamica(df, base=74, linha=35, minimo=140, maximo=320):
    try:
        h = base + (len(df) * linha)
        return max(minimo, min(maximo, h))
    except Exception:
        return minimo



def esc_html(texto):
    return html.escape(str(texto))


def render_asset_card(item, mostrar_setor=True, mostrar_fechamento=True, mostrar_variacao=False):
    setor_html = f'<p class="asset-sector">{esc_html(item.get("setor", "Outros"))}</p>' if mostrar_setor else ""
    fechamento_html = f'<p class="asset-line"><strong>Último fechamento:</strong> {esc_html(fmt_moeda(item.get("ultimo_fechamento", 0)))}</p>' if mostrar_fechamento else ""
    variacao_html = ""
    if mostrar_variacao:
        delta = fmt_delta_moeda(item.get("variacao_abs", 0)) if item.get("variacao_abs", 0) != 0 else "—"
        variacao_html = f'<p class="asset-line"><strong>Variação:</strong> {esc_html(fmt_pct(item.get("variacao_pct", 0)))} | {esc_html(delta)}</p>'

    dividendo_html = ""
    if item.get("dividendo_anual", 0) > 0:
        yield_txt = f"{item.get('dividend_yield_pct', 0):.2f}%"
        dividendo_html = (
            f'<p class="asset-line"><strong>Dividendo/ação:</strong> '
            f'{esc_html(fmt_moeda(item.get("dividendo_anual", 0)))} '
            f'({esc_html(yield_txt)} yield)</p>'
        )

    html_card = (
        f'<div class="asset-card">'
        f'{setor_html}'
        f'<p class="asset-ticker">{esc_html(item["ticker"])} {cor_nivel(item["nivel"])}</p>'
        f'<p class="asset-level">{esc_html(rotulo_nivel_card(item["nivel"]))}</p>'
        f'<div class="asset-grid">'
        f'<div class="asset-box"><div class="asset-box-label">Pontuação</div><div class="asset-box-value">{esc_html(item["score"])}</div></div>'
        f'<div class="asset-box"><div class="asset-box-label">Margem</div><div class="asset-box-value">{esc_html(margem_seguranca_exibicao(item))}</div></div>'
        f'</div>'
        f'<p class="asset-line"><strong>Preço atual:</strong> {esc_html(fmt_moeda(item.get("preco_atual", 0)))}</p>'
        f'{fechamento_html}'
        f'<p class="asset-line"><strong>Preço teto:</strong> {esc_html(fmt_moeda(item.get("preco_teto", 0)))}</p>'
        f'{dividendo_html}'
        f'{variacao_html}'
        f'<div class="asset-divider"></div>'
        f'<p class="asset-line"><strong>Status:</strong> {esc_html(status_preco(item.get("preco_atual", 0), item.get("preco_teto", 0)))}</p>'
        f'<p class="asset-line"><strong>Leitura:</strong> {esc_html(interpretacao_modelo(item))}</p>'
        f'</div>'
    )
    st.markdown(html_card, unsafe_allow_html=True)


def render_tese_carteira(perfil, tese_principal, concentracao, abaixo_teto_txt, margem_media_txt, setores_txt):
    html_tese = (
        f'<div class="tese-card">'
        f'<div class="tese-title">Tese sincronizada da carteira — {esc_html(perfil)}</div>'
        f'<div class="tese-line"><strong>Leitura principal:</strong> {esc_html(tese_principal)}</div>'
        f'<div class="tese-grid">'
        f'<div class="tese-line"><strong>Concentração:</strong> {esc_html(concentracao)}</div>'
        f'<div class="tese-line"><strong>Ativos abaixo do teto:</strong> {esc_html(abaixo_teto_txt)}</div>'
        f'<div class="tese-line"><strong>Margem média:</strong> {esc_html(margem_media_txt)}</div>'
        f'<div class="tese-line"><strong>Setores reais da carteira:</strong> {esc_html(setores_txt)}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html_tese, unsafe_allow_html=True)


def render_compare_mini_card(titulo, linhas):
    itens = ''.join([f'<div class="compare-mini-line">• {esc_html(linha)}</div>' for linha in linhas]) if linhas else '<div class="compare-mini-line">Sem destaques.</div>'
    html_block = f'<div class="compare-mini-card"><div class="compare-mini-title">{esc_html(titulo)}</div>{itens}</div>'
    st.markdown(html_block, unsafe_allow_html=True)


def render_profile_summary_card(perfil_nome, carteira_tmp):
    html_card = f'<div class="profile-card"><div class="profile-title">{esc_html(perfil_nome)}</div>'
    html_card += f'<div class="profile-line">{esc_html(explicacao_perfil(perfil_nome))}</div>'
    if carteira_tmp:
        info_tmp = resumo_carteira(carteira_tmp)
        score_medio = round(sum(x["score"] for x in carteira_tmp) / len(carteira_tmp), 1)
        html_card += f'<div class="profile-line"><strong>Ativos:</strong> {esc_html(len(carteira_tmp))}</div>'
        html_card += f'<div class="profile-line"><strong>Pontuação média:</strong> {esc_html(str(score_medio).replace(".", ","))}</div>'
        html_card += f'<div class="profile-line"><strong>Setores:</strong> {esc_html(info_tmp["setores"])}</div>'
        html_card += f'<div class="profile-line"><strong>Abaixo do teto:</strong> {esc_html(info_tmp["abaixo_teto"])}/{esc_html(len(carteira_tmp))}</div>'
        html_card += f'<div class="profile-line"><strong>Maior score:</strong> {esc_html(info_tmp["maior_score_ticker"])}</div>'
    else:
        html_card += '<div class="profile-line">Sem ativos para este perfil.</div>'
    html_card += '</div>'
    st.markdown(html_card, unsafe_allow_html=True)


# =========================
# CARTEIRA POR PERFIL - FONTE ÚNICA DE VERDADE
# =========================
PERFIS_CARTEIRA = ["Conservador", "Moderado", "Agressivo"]

def _sync_perfil_carteira():
    st.session_state["perfil_carteira_ativo"] = st.session_state.get("perfil_carteira_widget", "Conservador")

def obter_perfil_carteira():
    if "perfil_carteira_ativo" not in st.session_state:
        st.session_state["perfil_carteira_ativo"] = "Conservador"
    if "perfil_carteira_widget" not in st.session_state:
        st.session_state["perfil_carteira_widget"] = st.session_state["perfil_carteira_ativo"]
    widget_val = st.session_state.get("perfil_carteira_widget", st.session_state["perfil_carteira_ativo"])
    if widget_val != st.session_state["perfil_carteira_ativo"]:
        st.session_state["perfil_carteira_ativo"] = widget_val
    return st.session_state["perfil_carteira_ativo"]

def montar_df_carteira(carteira):
    registros = []
    for item in carteira:
        margem_num = calcular_margem_numerica(item)
        registros.append({
            "Ticker": item["ticker"],
            "Setor": item["setor"],
            "Nível": rotulo_nivel_card(item["nivel"]),
            "Pontuação": item["score"],
            "Margem de Segurança": margem_seguranca_exibicao(item),
            "Preço Atual": fmt_moeda(item["preco_atual"]),
            "Preço Teto": fmt_moeda(item["preco_teto"]),
            "Dividendo Anual": fmt_moeda(item.get("dividendo_anual", 0)) if item.get("dividendo_anual", 0) > 0 else "—",
            "Yield": f"{item.get('dividend_yield_pct', 0):.2f}%" if item.get("dividendo_anual", 0) > 0 else "—",
            "Status do Preço": status_preco(item["preco_atual"], item["preco_teto"]),
            "Prioridade": prioridade_ativo(item),
            "Faixa de Ação": faixa_acao(item),
            "_ticker_raw": item["ticker"],
            "_setor_raw": item["setor"],
            "_score_raw": item["score"],
            "_margem_num": margem_num if margem_num is not None else -9999,
            "_preco_num": float(item["preco_atual"]),
            "_abaixo_teto": status_preco(item["preco_atual"], item["preco_teto"]) == "Abaixo do teto",
        })
    return pd.DataFrame(registros)

def resumir_df_carteira(df_carteira):
    if df_carteira.empty:
        return {
            "total": 0,
            "score_medio": "—",
            "setores": 0,
            "maior_score": "—",
            "maior_ticker": "—",
            "leitura": "Sem ativos para análise.",
            "concentracao": "—",
            "abaixo_teto_txt": "0/0",
            "margem_media_txt": "—",
            "setores_txt": "0",
        }

    total = len(df_carteira)
    setores_qtd = int(df_carteira["_setor_raw"].nunique())
    abaixo_teto = int(df_carteira["_abaixo_teto"].sum())

    margens_validas = [m for m in df_carteira["_margem_num"].tolist() if m != -9999]
    margem_media = round(sum(margens_validas) / len(margens_validas), 1) if margens_validas else None
    score_medio = round(float(df_carteira["_score_raw"].mean()), 1)

    maior_idx = df_carteira["_score_raw"].idxmax()
    maior_score = int(df_carteira.loc[maior_idx, "_score_raw"])
    maior_ticker = str(df_carteira.loc[maior_idx, "_ticker_raw"])

    contagem_setores = df_carteira["_setor_raw"].value_counts()
    setor_top = str(contagem_setores.index[0]) if not contagem_setores.empty else "—"
    qtd_top = int(contagem_setores.iloc[0]) if not contagem_setores.empty else 0

    leitura = f"Carteira com {setores_qtd} setores, {abaixo_teto}/{total} ativos abaixo do teto"
    if margem_media is not None:
        leitura += f" e margem média de segurança de {str(margem_media).replace('.', ',')}%."
    else:
        leitura += "."

    return {
        "total": total,
        "score_medio": str(score_medio).replace(".", ","),
        "setores": setores_qtd,
        "maior_score": maior_score,
        "maior_ticker": maior_ticker,
        "leitura": leitura,
        "concentracao": f"{setor_top} ({qtd_top}/{total})",
        "abaixo_teto_txt": f"{abaixo_teto}/{total}",
        "margem_media_txt": fmt_pct(margem_media) if margem_media is not None else "—",
        "setores_txt": str(setores_qtd),
    }



def montar_analise_carteira_premium(df_carteira_final, perfil):
    if df_carteira_final.empty:
        return {
            "titulo": f"Leitura final da carteira — {perfil}",
            "leitura_final": "Sem ativos para análise.",
            "setores": []
        }

    setores_df = (
        df_carteira_final.groupby("_setor_raw")
        .agg(
            empresas=("Ticker", "count"),
            score_medio=("_score_raw", "mean"),
            abaixo_teto=("_abaixo_teto", "sum"),
        )
        .reset_index()
        .sort_values(by=["score_medio", "empresas"], ascending=[False, False])
    )

    total = int(setores_df["empresas"].sum())
    setores_qtd = int(len(setores_df))
    abaixo_teto = int(setores_df["abaixo_teto"].sum())

    margens_validas = [m for m in df_carteira_final["_margem_num"].tolist() if m != -9999]
    margem_media = round(sum(margens_validas) / len(margens_validas), 1) if margens_validas else None

    leitura_final = f"Carteira com {total} ativo(s), {setores_qtd} setor(es), {abaixo_teto}/{total} ativo(s) abaixo do teto"
    if margem_media is not None:
        leitura_final += f" e margem média de {str(margem_media).replace('.', ',')}%."

    linhas = []
    for _, row in setores_df.iterrows():
        linhas.append(
            f"{row['_setor_raw']} — {int(row['empresas'])} empresa(s), "
            f"pontuação média {str(round(float(row['score_medio']), 1)).replace('.', ',')}, "
            f"{int(row['abaixo_teto'])}/{int(row['empresas'])} abaixo do teto"
        )

    return {
        "titulo": f"Leitura final da carteira — {perfil}",
        "leitura_final": leitura_final,
        "setores": linhas,
    }

def render_card_leitura_final_premium(analise):
    setores_html = "".join(
        f'<div class="portfolio-final-line">• {esc_html(linha)}</div>'
        for linha in analise["setores"]
    ) if analise["setores"] else '<div class="portfolio-final-line">Sem leitura setorial.</div>'

    st.markdown(
        f"""
        <div class="portfolio-final-card">
            <div class="portfolio-final-title">{esc_html(analise["titulo"])}</div>
            <div class="portfolio-final-section">Leitura por setor</div>
            {setores_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


media_score = round(sum(x["score"] for x in resultados) / len(resultados), 1)
setores_cobertos = len(set(item["setor"] for item in resultados))

aba_dashboard, aba_visao, aba_comparador, aba_carteira, aba_rankings, aba_simulador = st.tabs([
    "🏛️ Dashboard",
    "📈 Visão Geral",
    "⚖️ Comparador",
    "📁 Carteira por Perfil",
    "📋 Lista de Empresas",
    "💰 Simulador de Aportes"
])


with aba_dashboard:
    st.subheader("Dashboard profissional")
    st.caption("Visão macro do universo acompanhado — força por setor, alertas do modelo e o estado das carteiras por perfil. Para ver empresas específicas, vai à aba Visão Geral.")
    st.caption(f"Atualizado em: {datetime.now().strftime('%H:%M:%S')}")

    ativos_abaixo = selecionar_abaixo_teto(resultados, limite=len(resultados))
    melhor_oportunidade = max(resultados, key=lambda x: x["score"])
    setores_df = resumo_setores_dashboard(resultados)

    d1, d2, d3, d4, d5 = st.columns(5, gap="medium")
    with d1:
        render_kpi_card("Ativos monitorados", len(resultados), "Universo acompanhado")
    with d2:
        render_kpi_card("Pontuação média geral", str(media_score).replace(".", ","), "Qualidade média")
    with d3:
        render_kpi_card("Abaixo do teto", len(ativos_abaixo), "Oportunidades do momento")
    with d4:
        render_kpi_card("Melhor", melhor_oportunidade["score"], melhor_oportunidade["ticker"])
    with d5:
        if not setores_df.empty:
            render_kpi_card("Setor mais forte", str(setores_df.iloc[0]["Score Médio"]).replace(".", ","), setores_df.iloc[0]["Setor"])
        else:
            render_kpi_card("Setor mais forte", "—", "Sem leitura setorial")

    st.markdown("---")
    ac1, ac2, ac3 = st.columns(3, gap="medium")
    alertas = alertas_dashboard(resultados)
    if len(alertas) > 0:
        with ac1:
            render_dashboard_info_card(alertas[0])
    with ac2:
        render_dashboard_info_card(insight_dashboard_diversificacao(resultados), "Insight de diversificação")
    if len(alertas) > 1:
        with ac3:
            render_dashboard_info_card(alertas[-1])

    st.markdown("---")
    st.markdown("### Setores em evidência do modelo")
    st.caption("Leitura setorial com pontuação média, quantidade de empresas e melhor ativo de cada setor.")
    if not setores_df.empty:
        setores_df = setores_df.sort_values(by="Score Médio", ascending=True).reset_index(drop=True)

        setores_df_exibicao = setores_df.copy()
        setores_df_exibicao["Setor"] = setores_df_exibicao["Setor"].astype(str)
        setores_df_exibicao["Empresas"] = setores_df_exibicao["Empresas"].astype(int)
        setores_df_exibicao["Score Médio"] = setores_df_exibicao["Score Médio"].astype(float).round(1)
        setores_df_exibicao["Abaixo do Teto"] = setores_df_exibicao["Abaixo do Teto"].astype(int)
        setores_df_exibicao["Melhor Ativo"] = setores_df_exibicao["Melhor Ativo"].astype(str)

        setores_df_exibicao = setores_df_exibicao.loc[:, ["Setor", "Empresas", "Score Médio", "Abaixo do Teto", "Melhor Ativo"]]

        st.dataframe(
            setores_df_exibicao,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Setor": st.column_config.TextColumn("Setor", width="large"),
                "Empresas": st.column_config.NumberColumn("Empresas", format="%d", width="small"),
                "Score Médio": st.column_config.NumberColumn("Score Médio", format="%.1f", width="small"),
                "Abaixo do Teto": st.column_config.NumberColumn("Abaixo do Teto", format="%d", width="small"),
                "Melhor Ativo": st.column_config.TextColumn("Melhor Ativo", width="medium"),
            },
            height=38 + (len(setores_df_exibicao) * 35),
        )

        st.markdown("#### Força setorial (score médio)")
        grafico_setores = px.bar(
            setores_df,
            x="Score Médio",
            y="Setor",
            orientation="h",
            text="Score Médio",
            hover_data={
                "Empresas": True,
                "Abaixo do Teto": True,
                "Melhor Ativo": True,
                "Score Médio": True,
                "Setor": False
            },
        )
        grafico_setores.update_traces(
            textposition="outside",
            marker=dict(color="#C9A13B", line=dict(width=0)),
            textfont=dict(color="#E4BE5C", family="IBM Plex Mono, monospace"),
            cliponaxis=False
        )
        grafico_setores.update_layout(
            height=360,
            margin=dict(l=10, r=30, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(236,227,205,0.02)",
            xaxis=dict(
                title="Score médio",
                range=[0, 100],
                showgrid=True,
                gridcolor="rgba(236,227,205,0.08)",
                zeroline=False,
            ),
            yaxis=dict(
                title="",
                showgrid=False,
            ),
            font=dict(color="#A9B8A7", family="IBM Plex Sans, sans-serif"),
            showlegend=False,
        )
        st.plotly_chart(grafico_setores, use_container_width=True)
    else:
        st.warning("Sem dados setoriais disponíveis.")

    st.markdown("---")
    st.markdown("### Carteira por perfil resumida")
    st.caption("Resumo rápido das carteiras teóricas para os três perfis de investidor.")
    rp1, rp2, rp3 = st.columns(3, gap="medium")
    for col, perfil_nome in zip([rp1, rp2, rp3], ["Conservador", "Moderado", "Agressivo"]):
        carteira_tmp = filtrar_carteira(perfil_nome, resultados)
        with col:
            render_profile_summary_card(perfil_nome, carteira_tmp)


with aba_visao:
    st.subheader("Visão Geral")
    st.caption("Empresas específicas que se destacam agora, vistas de dois ângulos diferentes — valorização e diversificação setorial. Para leitura agregada do mercado, vai ao Dashboard.")

    st.markdown("### Abaixo do preço-teto")
    st.caption("Ativos com melhor combinação de margem e score dentro da leitura atual do modelo.")
    oportunidades = selecionar_abaixo_teto(resultados, limite=4)
    if oportunidades:
        cols_op = st.columns(4, gap="medium")
        for i, item in enumerate(oportunidades):
            with cols_op[i]:
                render_card_dashboard(item)
    else:
        st.warning("Nenhum ativo abaixo do teto no momento.")

    st.markdown("---")
    st.markdown("### Destaques por setor")
    st.caption("Seleção diversificada do InvestScore com até 1 ativo por setor para evitar concentração excessiva.")
    destaques_setoriais = selecionar_top_diversificado(resultados, limite=4, max_por_setor=1)

    cols = st.columns(4, gap="medium")
    for idx, item in enumerate(destaques_setoriais):
        with cols[idx]:
            render_card_destaque_setorial(item)

with aba_comparador:
    st.subheader("Comparador profissional")
    st.caption("Comparação objetiva entre duas empresas com base em pontuação, preço atual, último fechamento e preço teto teórico.")

    lista_tickers = [item["ticker"] for item in resultados]
    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        ticker_1 = st.selectbox("Empresa 1", lista_tickers, index=0, key="comp_1")

    with col_b:
        opcoes_empresa_2 = [ticker for ticker in lista_tickers if ticker != ticker_1]
        if "comp_2" not in st.session_state or st.session_state.comp_2 not in opcoes_empresa_2:
            st.session_state.comp_2 = opcoes_empresa_2[0]
        ticker_2 = st.selectbox("Empresa 2", opcoes_empresa_2, index=opcoes_empresa_2.index(st.session_state.comp_2), key="comp_2")

    mapa_resultados = {item["ticker"]: item for item in resultados}
    item_1 = mapa_resultados.get(ticker_1)
    item_2 = mapa_resultados.get(ticker_2)

    if item_1 and item_2:
        placar_1, placar_2, linhas_placar = pontuacao_criterios(item_1, item_2)
        mensagem = mensagem_vencedor_consistente(item_1, item_2)

        pc1, pc2, pc3 = st.columns([1.4, 1, 1.4], gap="medium")
        pc1.metric("Placar", placar_1, item_1["ticker"])
        pc2.metric("Critérios", len(linhas_placar))
        pc3.metric("Placar", placar_2, item_2["ticker"])

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            render_asset_card(item_1, mostrar_setor=True, mostrar_fechamento=True, mostrar_variacao=True)
        with col2:
            render_asset_card(item_2, mostrar_setor=True, mostrar_fechamento=True, mostrar_variacao=True)

        if placar_1 == placar_2:
            st.info(mensagem)
        else:
            st.success(mensagem)


        st.markdown("#### 🧮 Placar por critérios")
        for criterio, vencedor_criterio in linhas_placar:
            st.caption(f"• {criterio}: {vencedor_criterio}")

        delta_score = item_1["score"] - item_2["score"]
        delta_preco = float(item_1["preco_atual"]) - float(item_2["preco_atual"])
        margem_1 = calcular_margem_numerica(item_1)
        margem_2 = calcular_margem_numerica(item_2)
        delta_margem_txt = fmt_pct(margem_1 - margem_2) if margem_1 is not None and margem_2 is not None else "—"

        st.markdown("#### 📏 Diferenças absolutas")
        st.caption(f"• Diferença de score: {delta_score:+}")
        st.caption(f"• Diferença de preço atual: {fmt_delta_moeda(delta_preco)}")
        st.caption(f"• Diferença de margem de segurança: {delta_margem_txt}")

        st.markdown("#### 🔎 Quem vence em quê")
        who1 = [c for c, v in linhas_placar if v == item_1["ticker"]]
        who2 = [c for c, v in linhas_placar if v == item_2["ticker"]]
        wc1, wc2 = st.columns(2, gap="medium")
        with wc1:
            render_compare_mini_card(f"{item_1['ticker']} vence em:", who1 if who1 else ["Sem vantagem isolada nos critérios avaliados."])
        with wc2:
            render_compare_mini_card(f"{item_2['ticker']} vence em:", who2 if who2 else ["Sem vantagem isolada nos critérios avaliados."])

        st.markdown("#### 🔎 Diferenças por empresa")
        dcol1, dcol2 = st.columns(2, gap="medium")
        with dcol1:
            render_compare_mini_card(f"Pontos favoráveis de {item_1['ticker']}", vantagens_comparativas(item_1, item_2))
        with dcol2:
            render_compare_mini_card(f"Pontos favoráveis de {item_2['ticker']}", vantagens_comparativas(item_2, item_1))

        observacoes = explicacao_comparador(item_1, item_2)
        if observacoes:
            st.markdown("#### Pontos de observação")
            for ponto in observacoes:
                st.caption(f"• {ponto}")

        st.caption("Resultado quantitativo do modelo. Não representa recomendação de investimento e pode variar conforme a atualização da fonte de dados.")



with aba_carteira:
    st.subheader("Carteira sugerida por perfil")

    perfil = st.selectbox(
        "Escolha seu perfil de investidor",
        ["Conservador", "Moderado", "Agressivo"],
        key="perfil_carteira_direto"
    )

    carteira = list(filtrar_carteira(perfil, resultados))

    st.markdown(badge_perfil(perfil), unsafe_allow_html=True)
    st.caption(explicacao_perfil(perfil))

    if carteira:
        df_carteira = montar_df_carteira(carteira)
        resumo = resumir_df_carteira(df_carteira)

        kc1, kc2, kc3, kc4 = st.columns(4, gap="medium")
        with kc1:
            render_kpi_card("Quantidade de ativos", resumo["total"], "Seleção atual")
        with kc2:
            render_kpi_card("Score médio da carteira", resumo["score_medio"], "Força média")
        with kc3:
            render_kpi_card("Setores na carteira", resumo["setores"], "Diversificação")
        with kc4:
            render_kpi_card("Pontuação maior", resumo["maior_score"], resumo["maior_ticker"])

        ordenar_por = st.selectbox(
            "Encomendar carteira por",
            ["Pontuação", "Margem de Segurança", "Preço Atual", "Setor"],
            key="ordem_carteira"
        )

        if ordenar_por == "Pontuação":
            df_carteira_final = df_carteira.sort_values(by="_score_raw", ascending=False).copy()
        elif ordenar_por == "Margem de Segurança":
            df_carteira_final = df_carteira.sort_values(by="_margem_num", ascending=False).copy()
        elif ordenar_por == "Preço Atual":
            df_carteira_final = df_carteira.sort_values(by="_preco_num", ascending=True).copy()
        else:
            df_carteira_final = df_carteira.sort_values(by=["_setor_raw", "_score_raw"], ascending=[True, False]).copy()

        df_export = df_carteira_final.drop(columns=[
            "_ticker_raw", "_setor_raw", "_score_raw", "_margem_num", "_preco_num", "_abaixo_teto"
        ])
        altura_tabela = 42 + (len(df_export) * 35)
        st.dataframe(df_export, use_container_width=True, hide_index=True, height=altura_tabela)

        csv = df_export.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Baixar carteira em CSV",
            data=csv,
            file_name=f"investscore_carteira_{perfil.lower()}.csv",
            mime="text/csv"
        )

        analise = montar_analise_carteira_premium(df_carteira_final, perfil)
        render_card_leitura_final_premium(analise)
    else:
        st.warning("Nenhuma empresa atende os critérios do perfil selecionado.")

with aba_rankings:
    st.subheader("Lista de empresas")
    st.caption("Visão organizada dos tickers acompanhados pelo InvestScore, com leitura quantitativa baseada em indicadores fundamentalistas.")

    df_ranking = pd.DataFrame([
        {
            "Posição": i,
            "Ticker": item["ticker"],
            "Setor": item["setor"],
            "Nível": rotulo_nivel_card(item["nivel"]),
            "Pontuação": item["score"],
            "Preço Atual": fmt_moeda(item["preco_atual"]),
            "Último Fechamento": fmt_moeda(item["ultimo_fechamento"]),
            "Preço Teto": fmt_moeda(item["preco_teto"]),
            "Status do Preço": status_preco(item["preco_atual"], item["preco_teto"]),
            "Dividendo/Ação": fmt_moeda(item["dividendo_anual"]) if item["dividendo_anual"] > 0 else "—",
            "Dividend Yield": f"{item['dividend_yield_pct']:.2f}%" if item["dividendo_anual"] > 0 else "—",
        }
        for i, item in enumerate(resultados, start=1)
    ])
    st.dataframe(
        df_ranking,
        use_container_width=True,
        hide_index=True,
        height=430,
        column_config={
            "Posição": st.column_config.NumberColumn("Posição", format="%d", width="small"),
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Setor": st.column_config.TextColumn("Setor", width="medium"),
            "Nível": st.column_config.TextColumn("Nível", width="small"),
            "Pontuação": st.column_config.NumberColumn("Pontuação", format="%d", width="small"),
            "Preço Atual": st.column_config.TextColumn("Preço Atual", width="small"),
            "Último Fechamento": st.column_config.TextColumn("Último Fechamento", width="small"),
            "Preço Teto": st.column_config.TextColumn("Preço Teto", width="small"),
            "Status do Preço": st.column_config.TextColumn("Status do Preço", width="medium"),
            "Dividendo/Ação": st.column_config.TextColumn("Dividendo/Ação", width="small"),
            "Dividend Yield": st.column_config.TextColumn("Dividend Yield", width="small"),
        },
    )

    st.markdown("---")
    st.subheader("Lista por setor")
    st.caption("Organização por setor para facilitar a navegação e a comparação entre empresas do mesmo grupo.")

    setores_dict = {}
    for item in resultados:
        setor = item.get("setor", "Outros")
        setores_dict.setdefault(setor, []).append(item)

    for setor, lista in setores_dict.items():
        with st.expander(f"{setor} ({len(lista)} empresas)", expanded=False):
            df_setor = pd.DataFrame([
                {
                    "Posição": i,
                    "Ticker": item["ticker"],
                    "Nível": rotulo_nivel_card(item["nivel"]),
                    "Pontuação": item["score"],
                    "Preço Atual": fmt_moeda(item["preco_atual"]),
                    "Preço Teto": fmt_moeda(item["preco_teto"]),
                    "Status do Preço": status_preco(item["preco_atual"], item["preco_teto"]),
                    "Dividend Yield": f"{item['dividend_yield_pct']:.2f}%" if item["dividendo_anual"] > 0 else "—",
                }
                for i, item in enumerate(sorted(lista, key=lambda x: x["score"], reverse=True), start=1)
            ])
            st.dataframe(
                df_setor,
                use_container_width=True,
                hide_index=True,
                height=38 + (len(df_setor) * 35),
                column_config={
                    "Posição": st.column_config.NumberColumn("Posição", format="%d", width="small"),
                    "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "Nível": st.column_config.TextColumn("Nível", width="small"),
                    "Pontuação": st.column_config.NumberColumn("Pontuação", format="%d", width="small"),
                    "Preço Atual": st.column_config.TextColumn("Preço Atual", width="small"),
                    "Preço Teto": st.column_config.TextColumn("Preço Teto", width="small"),
                    "Status do Preço": st.column_config.TextColumn("Status do Preço", width="medium"),
                    "Dividend Yield": st.column_config.TextColumn("Dividend Yield", width="small"),
                },
            )

st.markdown("---")
nota_fonte_dados()
render_nota_final()

# =============================================================================
# ABA: SIMULADOR DE APORTES
# =============================================================================

with aba_simulador:
    st.subheader("💰 Simulador de Aportes")
    st.caption(
        "Duas ferramentas diferentes, com níveis de certeza muito diferentes. "
        "Lê a explicação de cada uma antes de tirar conclusões."
    )

    st.markdown("---")
    st.markdown("### 📊 1. Aportes Históricos (Backtesting)")
    st.info(
        "**O que é isto:** com base em preços e dividendos REAIS já pagos, calcula "
        "quanto valeria hoje uma carteira se tivesses investido um valor fixo todos "
        "os meses, desde uma data no passado. É um facto histórico verificável — "
        "não é uma previsão, e não é uma recomendação para comprar esta ou aquela ação. "
        "O ticker é escolhido por ti."
    )

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        ticker_sim = st.selectbox("Empresa (ticker)", options=sorted(tickers), key="sim_ticker")
    with col_b:
        aporte_sim = st.number_input(
            "Aporte mensal (€)", min_value=10.0, max_value=100000.0, value=200.0, step=10.0, key="sim_aporte"
        )
    with col_c:
        anos_sim = st.slider("Período (anos)", min_value=1, max_value=15, value=5, key="sim_anos")
    with col_d:
        reinvestir_sim = st.checkbox("Reinvestir dividendos", value=True, key="sim_reinvestir")

    if st.button("Simular aportes históricos", key="btn_simular_hist"):
        with st.spinner("A obter histórico de preços e dividendos..."):
            try:
                stock_sim = yf.Ticker(ticker_sim)
                precos_mensais_sim, dividendos_sim = obter_historico_precos_dividendos(stock_sim, anos=anos_sim)
            except Exception:
                precos_mensais_sim, dividendos_sim = pd.Series(dtype=float), pd.Series(dtype=float)

        resultado_sim = None
        if not precos_mensais_sim.empty:
            resultado_sim = simular_aporte_retroativo(
                precos_mensais_sim, dividendos_sim, aporte_sim, reinvestir_sim
            )

        if resultado_sim is None:
            st.warning(
                f"Não foi possível obter dados suficientes para {ticker_sim} no período pedido. "
                "Tenta um período mais curto ou outra empresa."
            )
        else:
            st.markdown(f"#### Resultado para **{ticker_sim}** — últimos {resultado_sim['anos']:.1f} anos")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total investido", fmt_moeda(resultado_sim["total_investido"]))
            m2.metric("Valor final da carteira", fmt_moeda(resultado_sim["valor_final"]))
            m3.metric("Lucro/Prejuízo", fmt_moeda(resultado_sim["lucro_total"]))
            taxa_txt = (
                f"{resultado_sim['taxa_anual_equivalente_pct']:.2f}% / ano"
                if resultado_sim["taxa_anual_equivalente_pct"] is not None
                else "—"
            )
            m4.metric("Taxa anual equivalente (XIRR)", taxa_txt)

            st.caption(
                f"Rentabilidade total no período: {resultado_sim['rentabilidade_total_pct']:.2f}% · "
                f"Dividendos recebidos: {fmt_moeda(resultado_sim['total_dividendos_recebidos'])} "
                f"({'reinvestidos' if resultado_sim['dividendos_reinvestidos'] else 'não reinvestidos'})"
            )

            hist_df = pd.DataFrame(resultado_sim["historico_mensal"])
            if not hist_df.empty:
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Scatter(
                    x=hist_df["data"], y=hist_df["valor_carteira"],
                    mode="lines", name="Valor da carteira", line=dict(width=3)
                ))
                fig_sim.add_trace(go.Scatter(
                    x=hist_df["data"], y=hist_df["valor_investido_acumulado"],
                    mode="lines", name="Total investido (sem retorno)", line=dict(width=2, dash="dash")
                ))
                fig_sim.update_layout(
                    height=380,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    yaxis_title="€",
                )
                st.plotly_chart(fig_sim, use_container_width=True)

            st.session_state["sim_taxa_sugerida"] = (
                resultado_sim["taxa_anual_equivalente_pct"] / 100
                if resultado_sim["taxa_anual_equivalente_pct"] is not None
                else None
            )

        with st.expander("⚠️ Limitações deste cálculo — ler antes de confiar no resultado"):
            st.markdown(
                "- Os aportes são simulados ao preço de fecho de cada mês — não é necessariamente "
                "o preço exato a que uma ordem real seria executada.\n"
                "- Assume-se que é possível comprar frações de ações, o que nem todas as corretoras permitem.\n"
                "- Não são considerados impostos sobre dividendos ou mais-valias, nem comissões de "
                "corretagem ou custódia — estes custos reduzem o retorno real.\n"
                "- Dividendos são reconciliados por mês civil, não pela data exata de pagamento.\n"
                "- **Isto é uma reconstrução do passado, não uma previsão do futuro.** Rentabilidade "
                "passada não é garantia nem indicação fiável de rentabilidade futura.\n"
                "- Esta ferramenta é puramente informativa e não constitui aconselhamento de investimento "
                "nem recomendação de compra ou venda de qualquer ativo."
            )

    st.markdown("---")
    st.markdown("### 🔮 2. Projeção Futura (extrapolação matemática)")
    st.warning(
        "**Atenção:** isto NÃO é uma previsão nem uma promessa de rentabilidade. É apenas uma "
        "extrapolação matemática — 'se a taxa de retorno se mantivesse constante a X% ao ano, o "
        "valor cresceria assim'. O mercado não se comporta de forma constante e linear; isto é uma "
        "ferramenta de raciocínio, não uma bola de cristal. As taxas abaixo são editáveis — usa-as "
        "com espírito crítico."
    )

    taxa_sugerida = st.session_state.get("sim_taxa_sugerida")
    taxa_moderada_default = round(taxa_sugerida * 100, 1) if taxa_sugerida else 5.0

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        aporte_proj = st.number_input(
            "Aporte mensal futuro (€)", min_value=10.0, max_value=100000.0, value=200.0, step=10.0, key="proj_aporte"
        )
        anos_proj = st.slider("Horizonte (anos)", min_value=1, max_value=40, value=15, key="proj_anos")
    with col_p2:
        valor_inicial_proj = st.number_input(
            "Valor inicial já investido (€)", min_value=0.0, max_value=10_000_000.0, value=0.0, step=100.0, key="proj_inicial"
        )

    st.caption(
        "As três taxas abaixo são um ponto de partida sugerido"
        + (f", com base na taxa histórica calculada acima ({taxa_sugerida*100:.2f}%/ano)." if taxa_sugerida else " (nenhuma simulação histórica corrida ainda).")
        + " Muda-as livremente."
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        taxa_conservadora = st.number_input(
            "Cenário conservador (%/ano)", value=max(0.0, taxa_moderada_default - 3.0), step=0.5, key="taxa_cons"
        )
    with col_t2:
        taxa_moderada = st.number_input(
            "Cenário moderado (%/ano)", value=taxa_moderada_default, step=0.5, key="taxa_mod"
        )
    with col_t3:
        taxa_otimista = st.number_input(
            "Cenário otimista (%/ano)", value=taxa_moderada_default + 3.0, step=0.5, key="taxa_otim"
        )

    if st.button("Projetar cenários", key="btn_projetar"):
        cenarios = projetar_cenarios(
            aporte_mensal=aporte_proj,
            anos=anos_proj,
            taxas_anuais={
                "Conservador": taxa_conservadora / 100,
                "Moderado": taxa_moderada / 100,
                "Otimista": taxa_otimista / 100,
            },
            valor_inicial=valor_inicial_proj,
        )

        cp1, cp2, cp3 = st.columns(3)
        for col, nome in zip([cp1, cp2, cp3], ["Conservador", "Moderado", "Otimista"]):
            res = cenarios[nome]
            with col:
                st.markdown(f"**{nome}** ({res['taxa_anual_pct']:.1f}%/ano)")
                st.metric("Valor projetado", fmt_moeda(res["valor_final"]))
                st.caption(
                    f"Investido: {fmt_moeda(res['total_investido'])} · "
                    f"Estimativa de lucro: {fmt_moeda(res['lucro_estimado'])}"
                )

        fig_proj = go.Figure()
        cores = {"Conservador": "#888888", "Moderado": "#1f77b4", "Otimista": "#2ca02c"}
        for nome in ["Conservador", "Moderado", "Otimista"]:
            serie_df = pd.DataFrame(cenarios[nome]["serie_mensal"])
            fig_proj.add_trace(go.Scatter(
                x=serie_df["mes"], y=serie_df["valor"],
                mode="lines", name=nome, line=dict(width=3, color=cores[nome])
            ))
        serie_investido = pd.DataFrame(cenarios["Moderado"]["serie_mensal"])
        fig_proj.add_trace(go.Scatter(
            x=serie_investido["mes"], y=serie_investido["investido"],
            mode="lines", name="Total investido (sem retorno)", line=dict(width=2, dash="dash", color="#cccccc")
        ))
        fig_proj.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="Meses",
            yaxis_title="€",
        )
        st.plotly_chart(fig_proj, use_container_width=True)

        st.caption(
            "Projeção puramente matemática (juro composto com aportes mensais constantes). "
            "Não considera inflação, impostos, comissões, nem a possibilidade real de perdas "
            "de capital. Não constitui aconselhamento de investimento."
        )
