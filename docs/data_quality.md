# Data Quality

> Preencher as colunas de violações depois de rodar
> `python/data_quality/quality_check.py` (Fase 5), e novamente após o ETL
> (Fase 6) para comparar antes/depois.

| Problema | Regra de detecção | Tratamento (ETL) | Violações (raw) | Violações (processed) | Status |
|---|---|---|---|---|---|
| Cidade com grafias diferentes | value_counts() em `cidade` | De-para para nome canônico | - | - | Pendente |
| Categoria com grafias diferentes | value_counts() em `categoria` | De-para + normalização | - | - | Pendente |
| CPF duplicado | duplicated() em `cpf` | Manter registro mais completo/recente | - | - | Pendente |
| E-mail nulo | isnull() em `email` | Manter (não bloqueia venda), registrar % | - | - | Pendente |
| Preço nulo/negativo | preco_tabela.isnull() ou < 0 | Descartar linha, logar quantidade | - | - | Pendente |
| Categoria nula | categoria.isnull() | De-para ou "Não categorizado" | - | - | Pendente |
| Data de pedido inválida | fora do range 2024-01-01 a 2025-12-31 | Descartar, logar quantidade | - | - | Pendente |
| Pedido duplicado | duplicated() em `pedido_id` | Manter primeira ocorrência | - | - | Pendente |
| Preço unitário divergente do preço de tabela | comparação item x produto | Investigar e documentar caso a caso | - | - | Pendente |
| Estoque negativo | quantidade_disponivel < 0 | Zerar ou descartar, logar | - | - | Pendente |
| Produto órfão em estoque | produto_id não existe em produtos | Descartar linha | - | - | Pendente |
