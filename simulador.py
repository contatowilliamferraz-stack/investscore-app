# Simulador de aporte periódico — InvestScore
#
# Este módulo tem DOIS simuladores, com propósitos e níveis de certeza
# muito diferentes. É importante não os confundir na interface:
#
# 1. simular_aporte_retroativo() — BACKTESTING
#    Responde: "se eu tivesse investido X por mês nesta ação/carteira,
#    nos últimos N anos, com base em preços e dividendos REAIS, teria
#    hoje quanto?"
#    Isto é um cálculo sobre factos passados. É rigoroso, verificável, e
#    não é uma previsão — é história.
#
# 2. projetar_cenarios() — PROJEÇÃO FUTURA
#    Responde: "se eu continuar a investir X por mês a uma taxa de
#    retorno assumida, quanto poderei vir a ter daqui a N anos?"
#    Isto NÃO é um facto, é uma extrapolação matemática de uma taxa que
#    o utilizador escolhe (por defeito, sugerida a partir do desempenho
#    histórico, mas sempre editável e sempre rotulada como suposição).
#    Nunca deve ser apresentado como garantia, promessa ou recomendação.
#
# Limitações explícitas de ambos os simuladores (documentar sempre na UI):
# - Não consideram impostos sobre mais-valias nem sobre dividendos.
# - Não consideram taxas de corretagem/custódia.
# - Assumem que é possível comprar frações de ação (nem todas as
#   corretoras permitem isto para todos os mercados).
# - O aporte mensal e o dividendo do mês são aplicados de forma
#   simplificada (mês a mês), não ao cêntimo/dia exato de pagamento.
# - Dividendos reinvestidos assumem-se reinvestidos ao preço de fecho
#   do mesmo mês em que foram recebidos, o que raramente é o preço
#   exato a que a reinvestimento real ocorreria.
# - Rentabilidade passada NÃO é garantia de rentabilidade futura. Isto
#   aplica-se sobretudo ao simulador de projeção futura.

from datetime import datetime
import pandas as pd


def _xirr(fluxo_caixa):
    """Calcula a taxa interna de retorno anualizada (XIRR) de uma série
    de fluxos de caixa com datas irregulares, por bisseção.

    fluxo_caixa: lista de tuplos (data: datetime, valor: float).
    Valores negativos = saída de caixa (aportes). Valores positivos =
    entrada de caixa (valor final da carteira, dividendos não
    reinvestidos, etc.).

    Devolve a taxa anual (ex.: 0.07 = 7% ao ano) ou None se não for
    possível calcular (ex.: todos os fluxos com o mesmo sinal).
    """
    if not fluxo_caixa or len(fluxo_caixa) < 2:
        return None

    t0 = fluxo_caixa[0][0]

    def valor_presente_liquido(taxa):
        total = 0.0
        for data, valor in fluxo_caixa:
            dias = (data - t0).days
            total += valor / ((1 + taxa) ** (dias / 365.0))
        return total

    baixo, alto = -0.9999, 10.0
    vpl_baixo = valor_presente_liquido(baixo)
    vpl_alto = valor_presente_liquido(alto)

    if vpl_baixo * vpl_alto > 0:
        return None

    meio = 0.0
    for _ in range(200):
        meio = (baixo + alto) / 2
        vpl_meio = valor_presente_liquido(meio)
        if abs(vpl_meio) < 1e-6:
            break
        if vpl_baixo * vpl_meio < 0:
            alto = meio
        else:
            baixo = meio
            vpl_baixo = vpl_meio

    return meio


def simular_aporte_retroativo(precos_mensais, dividendos, aporte_mensal, reinvestir_dividendos=True):
    """Simula aportes mensais retroativos numa única ação, com dados
    históricos reais.

    precos_mensais: pandas.Series indexada por data (mensal), valores =
        preço de fecho.
    dividendos: pandas.Series indexada por data (qualquer frequência),
        valores = dividendo por ação pago nessa data. Pode ser vazia.
    aporte_mensal: valor investido em cada mês, na moeda do preço.
    reinvestir_dividendos: se True, dividendos recebidos compram mais
        ações no mês em que são pagos. Se False, ficam como saldo em
        caixa não investido (contam para a rentabilidade mas não geram
        mais ações).

    Devolve um dicionário com os resultados e uma série mensal para
    gráfico. Devolve None se não houver dados suficientes.
    """
    precos_mensais = precos_mensais.dropna().sort_index()
    if precos_mensais.empty or len(precos_mensais) < 2:
        return None

    if dividendos is None:
        dividendos = pd.Series(dtype=float)
    dividendos_por_mes = pd.Series(dtype=float)
    if not dividendos.empty:
        dividendos.index = pd.to_datetime(dividendos.index).tz_localize(None)
        dividendos_por_mes = dividendos.resample("MS").sum()

    acoes_acumuladas = 0.0
    total_investido = 0.0
    total_dividendos_recebidos = 0.0
    total_dividendos_em_caixa = 0.0
    fluxo_caixa = []
    historico_mensal = []

    for data, preco in precos_mensais.items():
        if preco is None or preco <= 0 or pd.isna(preco):
            continue

        data_mes = pd.Timestamp(data.year, data.month, 1)

        novas_acoes = aporte_mensal / preco
        acoes_acumuladas += novas_acoes
        total_investido += aporte_mensal
        fluxo_caixa.append((data.to_pydatetime(), -aporte_mensal))

        dividendo_por_acao_mes = float(dividendos_por_mes.get(data_mes, 0.0) or 0.0)
        if dividendo_por_acao_mes > 0:
            valor_dividendo = dividendo_por_acao_mes * acoes_acumuladas
            total_dividendos_recebidos += valor_dividendo
            if reinvestir_dividendos:
                acoes_acumuladas += valor_dividendo / preco
            else:
                total_dividendos_em_caixa += valor_dividendo
                fluxo_caixa.append((data.to_pydatetime(), valor_dividendo))

        historico_mensal.append({
            "data": data,
            "valor_investido_acumulado": total_investido,
            "valor_carteira": acoes_acumuladas * preco + (total_dividendos_em_caixa if not reinvestir_dividendos else 0.0),
        })

    if total_investido <= 0:
        return None

    preco_final = float(precos_mensais.iloc[-1])
    data_final = precos_mensais.index[-1]
    valor_acoes_final = acoes_acumuladas * preco_final
    valor_final = valor_acoes_final + (total_dividendos_em_caixa if not reinvestir_dividendos else 0.0)

    fluxo_caixa.append((data_final.to_pydatetime(), valor_acoes_final))

    anos = (data_final - precos_mensais.index[0]).days / 365.25
    taxa_anual = _xirr(fluxo_caixa)

    return {
        "total_investido": total_investido,
        "total_dividendos_recebidos": total_dividendos_recebidos,
        "dividendos_reinvestidos": reinvestir_dividendos,
        "acoes_acumuladas": acoes_acumuladas,
        "preco_final": preco_final,
        "valor_final": valor_final,
        "lucro_total": valor_final - total_investido,
        "rentabilidade_total_pct": (valor_final / total_investido - 1) * 100,
        "taxa_anual_equivalente_pct": (taxa_anual * 100) if taxa_anual is not None else None,
        "anos": anos,
        "historico_mensal": historico_mensal,
    }


def projetar_cenarios(aporte_mensal, anos, taxas_anuais, valor_inicial=0.0):
    """Projeta o valor futuro de uma carteira com aportes mensais
    constantes, sob diferentes taxas de retorno anual assumidas.

    Isto é uma extrapolação matemática, não uma previsão. As taxas
    devem ser fornecidas pelo chamador (idealmente derivadas do
    resultado de simular_aporte_retroativo, com uma margem para cima e
    para baixo) e devem ser sempre editáveis/visíveis para quem usa a
    ferramenta.

    taxas_anuais: dicionário {"nome_do_cenario": taxa_anual_decimal}.

    Devolve um dicionário por cenário com valor final, total investido,
    lucro e uma série mensal para gráfico.
    """
    resultados = {}
    meses = max(1, round(anos * 12))

    for nome, taxa_anual in taxas_anuais.items():
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1
        valor = valor_inicial
        total_investido = valor_inicial
        serie = []
        for mes in range(1, meses + 1):
            valor = valor * (1 + taxa_mensal) + aporte_mensal
            total_investido += aporte_mensal
            serie.append({"mes": mes, "valor": valor, "investido": total_investido})

        resultados[nome] = {
            "taxa_anual_pct": taxa_anual * 100,
            "valor_final": valor,
            "total_investido": total_investido,
            "lucro_estimado": valor - total_investido,
            "serie_mensal": serie,
        }

    return resultados


def obter_historico_precos_dividendos(stock, anos=5):
    """Recebe um objeto yfinance.Ticker já criado (para reaproveitar a
    mesma sessão/cache de get_data) e devolve (precos_mensais,
    dividendos) prontos para simular_aporte_retroativo.

    precos_mensais: pandas.Series mensal de preços de fecho.
    dividendos: pandas.Series de dividendos por ação, na frequência
    original de pagamento.
    """
    periodo = f"{anos}y" if anos <= 10 else "max"
    hist = stock.history(period=periodo, interval="1mo", auto_adjust=False)

    precos_mensais = pd.Series(dtype=float)
    if hist is not None and not hist.empty and "Close" in hist.columns:
        hist = hist.copy()
        hist.index = pd.to_datetime(hist.index).tz_localize(None)
        precos_mensais = hist["Close"].dropna()

    dividendos = pd.Series(dtype=float)
    try:
        divs = stock.dividends
        if divs is not None and not divs.empty:
            divs = divs.copy()
            divs.index = pd.to_datetime(divs.index).tz_localize(None)
            corte = pd.Timestamp.today() - pd.DateOffset(years=anos)
            dividendos = divs[divs.index >= corte]
    except Exception:
        dividendos = pd.Series(dtype=float)

    return precos_mensais, dividendos
