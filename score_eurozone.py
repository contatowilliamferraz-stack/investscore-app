# Modelo de pontuação InvestScore recalibrado para a Zona Euro.
#
# Porque é preciso recalibrar (e não só copiar score.py do Brasil):
# O método Barsi original foi pensado para o mercado brasileiro, onde
# dividend yields de 8-12% em empresas de qualidade são normais (reflexo
# de juros historicamente altos no Brasil e de dividendos isentos de
# imposto). Na Zona Euro isso não existe: segundo dados do Euro Stoxx 50
# (STOXX, dados de 30/06/2026), o yield médio (dividend yield trailing)
# do índice andava à volta de 2,5%, com yield projetado de 3,5%. Isto é,
# uma empresa europeia de grande qualidade a pagar 5-6% já é considerada
# um yield elevado — o oposto do que o modelo brasileiro assumiria.
#
# Se aplicássemos os limiares brasileiros tal e qual, quase nenhuma
# empresa europeia pontuaria bem em dividendos, e o preço-teto (que usa
# um yield-alvo de 6%) classificaria praticamente tudo como "acima do
# teto" — mesmo empresas historicamente sólidas.
#
# Ajustes feitos aqui, com a lógica por trás de cada um:
#
# 1. Dividend yield: limiares aproximadamente reduzidos para refletir a
#    distribuição real de yields na Zona Euro (a maioria das blue chips
#    fica entre 1% e 5%; acima de 6% já é setor de alto yield como
#    utilities/telecom/bancos; acima de 8% é excepcional, e muitas vezes
#    sinal de que o mercado desconfia da sustentabilidade do dividendo).
#
# 2. Yield-alvo do preço-teto (Bazin): reduzido de 6% para 4%. Isto
#    mantém o espírito do método (só considerar "barata" uma ação que
#    pague um yield exigente face ao preço atual), mas calibrado à
#    realidade de taxas de juro e yields estruturalmente mais baixos da
#    Zona Euro.
#
# 3. Crescimento (earnings/revenue growth): limiares reduzidos, porque a
#    Zona Euro tem inflação e crescimento nominal do PIB estruturalmente
#    mais baixos do que o Brasil — um crescimento de lucros de 12% ao ano
#    numa blue chip europeia madura já é excelente, ao passo que no
#    Brasil esse patamar era apenas "bom".
#
# 4. ROE: limiares ligeiramente reduzidos — mercados desenvolvidos como a
#    Zona Euro tendem a ter ROEs médios um pouco mais baixos do que
#    mercados emergentes como o Brasil, dado o perfil de risco e o custo
#    de capital diferentes.
#
# 5. Dívida (debt-to-equity) e margem: mantidos praticamente iguais aos
#    do modelo brasileiro, porque são rácios relativos (não dependem da
#    moeda nem do nível de juros do país) — uma empresa sobre-endividada
#    é sobre-endividada em qualquer mercado.
#
# NOTA: estes limiares foram calibrados com base em estatísticas públicas
# do Euro Stoxx 50 (STOXX/Deutsche Börse) e no conhecimento geral de
# blue chips europeias, não numa análise estatística completa do universo
# de 191 tickers deste projeto. Recomenda-se rever estes números com
# dados reais (via yfinance) assim que o motor estiver a correr, e
# ajustar se a distribuição observada divergir muito do esperado.


def score_dividend_yield(dy):
    if dy >= 0.08:
        return 20
    elif dy >= 0.06:
        return 16
    elif dy >= 0.04:
        return 12
    elif dy >= 0.025:
        return 8
    elif dy > 0:
        return 4
    return 0


def score_roe(roe):
    if roe >= 0.20:
        return 20
    elif roe >= 0.15:
        return 16
    elif roe >= 0.10:
        return 12
    elif roe >= 0.06:
        return 8
    elif roe > 0:
        return 4
    return 0


def score_margem(margin):
    if margin >= 0.30:
        return 15
    elif margin >= 0.20:
        return 12
    elif margin >= 0.10:
        return 9
    elif margin >= 0.05:
        return 5
    elif margin > 0:
        return 2
    return 0


def score_divida(debt):
    if debt <= 0:
        return 10
    elif debt < 30:
        return 20
    elif debt < 60:
        return 16
    elif debt < 100:
        return 10
    elif debt < 150:
        return 5
    return 0


def score_crescimento(growth):
    if growth >= 0.12:
        return 25
    elif growth >= 0.08:
        return 20
    elif growth >= 0.05:
        return 15
    elif growth >= 0.02:
        return 10
    elif growth > 0:
        return 5
    return 0


def ajuste_setorial(score, setor, dy, roe, margin, growth):
    ajuste = 0

    if setor == "Bancos e Serviços Financeiros":
        if roe > 0.15:
            ajuste += 5
        if margin > 0.20:
            ajuste += 3

    elif setor == "Energia e Utilities":
        if dy > 0.06:
            ajuste += 6
        if growth < 0.03:
            ajuste += 2

    elif setor == "Petróleo, Gás e Químicos":
        if growth > 0.08:
            ajuste += 5
        if margin > 0.12:
            ajuste += 3

    elif setor == "Materiais e Química":
        if growth > 0.06:
            ajuste += 4
        if margin > 0.10:
            ajuste += 3

    elif setor == "Luxo e Bens Premium":
        if margin > 0.15:
            ajuste += 5
        if growth > 0.06:
            ajuste += 3

    return score + ajuste


def calculate_score(ind):
    dy = ind.get("DividendYield", 0) or 0
    roe = ind.get("ROE", 0) or 0
    margin = ind.get("Margin", 0) or 0
    debt = ind.get("Debt", 0) or 0
    growth = ind.get("Growth", 0) or 0

    total = (
        score_dividend_yield(dy)
        + score_roe(roe)
        + score_margem(margin)
        + score_divida(debt)
        + score_crescimento(growth)
    )

    penalidade = 0

    if dy >= 0.06 and roe < 0.08:
        penalidade += 10

    if margin < 0.05:
        penalidade += 5

    if growth < 0:
        penalidade += 10

    if debt > 150:
        penalidade += 10

    score_final = total - penalidade

    if roe <= 0:
        score_final = min(score_final, 40)

    if margin <= 0:
        score_final = min(score_final, 40)

    setor = ind.get("Setor") or "Outros"
    score_final = ajuste_setorial(score_final, setor, dy, roe, margin, growth)

    return max(0, min(score_final, 98))


def calcular_preco_teto(dividendo_anual, dy_alvo=0.04):
    """Método de Bazin adaptado à Zona Euro: yield-alvo de 4% em vez dos
    6% usados no modelo brasileiro, refletindo o patamar estrutural mais
    baixo de dividend yields na Europa (ver nota de calibração no topo
    deste ficheiro)."""
    if dividendo_anual <= 0:
        return 0
    return dividendo_anual / dy_alvo
