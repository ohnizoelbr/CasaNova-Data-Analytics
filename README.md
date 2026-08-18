# CasaNova Data Analytics

## Sobre o projeto
Projeto de portfólio de análise de dados: pipeline completo, do dado bruto ao
dashboard, para um case fictício de varejo (CasaNova - casa, ferramentas e
utilidades).

## Problema de negócio
Ver [docs/business_problem.md](docs/business_problem.md).

## Arquitetura
```
BUSINESS PROBLEM
      |
COLETA / GERAÇÃO DOS DADOS (Python)
      |
EXCEL (exploração leve)
      |
PYTHON (EDA + Data Quality + ETL)
      |
SQL - SQLite (modelagem dimensional + views)
      |
EXCEL (conferência cruzada)
      |
POWER BI (modelo semântico + DAX)
      |
INSIGHTS (GAPs e recomendações)
      |
GITHUB -> LINKEDIN
```

## Tecnologias
Python (pandas), SQL (SQLite), Power BI (DAX), Excel, Git/GitHub

## Como rodar
1. `python -m venv .venv` e ativar
2. `pip install -r requirements.txt`
3. `python setup_project.py` - gera a estrutura de pastas e a documentação inicial
4. Demais passos conforme o projeto avança - ver `docs/phase_status.md`

## Estrutura de pastas
```
data/            raw, processed, quality, star_schema
python/          generation, analysis, data_quality, etl, sql_load
sql/             staging, dimensions, facts, analytics
docs/            documentação do projeto
reports/         insights e imagens
notebooks/       EDA em notebook (opcional)
```

## Principais insights
(preencher na Fase 10 - ver `reports/insights.md`)

## Documentação completa
Ver pasta [`docs/`](docs/):
- `business_problem.md` - o problema de negócio
- `business_rules.md` - regras de negócio
- `data_dictionary.md` - dicionário de dados
- `data_model.md` - modelo dimensional
- `data_quality.md` - qualidade de dados
- `kpi_catalog.md` - catálogo de KPIs
- `methodology.md` - decisões técnicas
- `validation.md` - validação cruzada
- `phase_status.md` - status do projeto
