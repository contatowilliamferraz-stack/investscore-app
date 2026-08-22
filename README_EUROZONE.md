# InvestScore Europa (Zona Euro)

Versão adaptada do InvestScore para o mercado da Zona Euro, calibrada com base
em dados reais do Euro Stoxx 50 (yield médio ~2,5-3,5%, muito abaixo do
mercado brasileiro).

## Cobertura
191 empresas dos principais índices nacionais da Zona Euro:
PSI20 (Portugal), CAC40 (França), DAX40 (Alemanha), IBEX35 (Espanha),
AEX25 (Países Baixos), BEL20 (Bélgica), FTSE MIB (Itália).

## Ficheiros
- `app_eurozone.py`: aplicação principal (correr com `streamlit run app_eurozone.py`)
- `tickers_eurozone.py`: universo de 191 tickers
- `tickers_setoriais_eurozone.py`: classificação por 10 setores
- `score_eurozone.py`: modelo de pontuação recalibrado (ver comentários no topo do ficheiro para a lógica de cada ajuste)
- `data.py` / `indicators.py`: iguais aos do projeto brasileiro (lógica agnóstica de mercado)

## Rodar
```bash
pip install -r requirements.txt
streamlit run app_eurozone.py
```

## Estado de validação (importante ler antes de usar a sério)
- A lista de tickers foi cruzada contra fontes oficiais (Wikipedia/Euronext/STOXX/BME) para
  os 7 índices em 18/08/2026. Correções aplicadas nessa validação: adicionadas Accor,
  ArcelorMittal, Bureau Veritas, Teleperformance (França); Daimler Truck, Porsche AG,
  Porsche SE, Siemens Energy (Alemanha); Ferrovial, Laboratorios Rovi, Sacyr (Espanha);
  Unilever, RELX, ABN AMRO, BE Semiconductor (Países Baixos); Ackermans & van Haaren,
  Lotus Bakeries, D'Ieteren, Aperam (Bélgica). Removida a duplicação da Stellantis (estava
  contada em França e Itália ao mesmo tempo, com tickers diferentes para a mesma empresa) e
  da Worldline (já não é constituinte do CAC40).
- A validação foi feita por pesquisa e cruzamento de fontes (Wikipedia, factsheets Euronext/
  STOXX/BME, TradingView), não por acesso direto e sistemático à API oficial de cada bolsa —
  composições de índice mudam a cada revisão trimestral, por isso vale a pena repetir esta
  validação periodicamente, sobretudo antes de qualquer lançamento público.
- Itália (FTSE MIB) teve uma verificação mais ligeira do que os restantes 6 índices — não
  foram encontradas correções óbvias, mas não houve o mesmo cruzamento linha-a-linha.
