# Regras de Negócio

> Este arquivo evolui nas Fases 5 e 6 (Data Quality e ETL) - os itens abaixo são o
> ponto de partida definido no desenho do projeto; ajuste conforme as decisões reais
> tomadas durante o tratamento dos dados.

## O que é uma venda válida
- Pedido com status "concluído" e `valor_liquido > 0`.
- (Detalhar demais critérios ao final da Fase 6.)

## Como a receita é calculada
`valor_liquido = valor_bruto - valor_desconto`

## Como a margem é calculada
`margem = valor_liquido - custo_total`

`custo_total = quantidade x custo do produto` (custo ATUAL do cadastro, não custo
histórico na data da venda - simplificação assumida para o escopo deste projeto;
ver `methodology.md`).

## Critério de desempate para clientes duplicados
(Definir na Fase 6: qual registro prevalece quando há CPF duplicado entre
`cliente_id` diferentes - sugestão: manter o cadastro mais recente/mais completo.)

## Regras de status de pedido
(Definir na Fase 6: quais status existem após a padronização, e quais entram nas
métricas de receita - pedidos cancelados devem ser incluídos ou não?)
