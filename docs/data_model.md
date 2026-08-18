# Modelo de Dados

## Visão geral (modelo estrela)

```
                    dim_data
                       |
dim_loja ---- fato_vendas ---- dim_produto
                       |
                  dim_cliente

fato_estoque (data_key, produto_key, loja_key)
fato_funil (data_key, categoria, dispositivo)
fato_concorrencia (data_key, produto_key)
```

## Dimensões

### dim_data
Calendário. Uma linha por dia do período do case (2024-01-01 a 2025-12-31).
`data_key, data, ano, trimestre, mes, nome_mes, semana_ano, dia, dia_semana, nome_dia_semana, fim_de_semana`

### dim_loja
`loja_key, loja_id, nome_loja, cidade, estado, tipo_canal, ativo`

### dim_produto
`produto_key, produto_id, nome_produto, categoria, ativo`

### dim_cliente
`cliente_key, cliente_id, cidade, estado, data_cadastro`

Sem nome/CPF/e-mail/telefone - dado sensível fica só na camada `processed`,
não entra no modelo analítico.

## Fatos

### fato_vendas - grão: 1 linha = 1 item de pedido vendido
`venda_key, data_key, loja_key, produto_key, cliente_key, pedido_id, quantidade, valor_bruto, valor_desconto, valor_liquido, custo_total`

### fato_estoque - grão: 1 linha = 1 snapshot mensal de produto x loja
`id, data_key, loja_key, produto_key, quantidade_disponivel`

### fato_funil - grão: 1 linha = 1 dia x categoria x dispositivo
`id, data_key, categoria, dispositivo, visualizacoes, add_carrinho, checkout_iniciado, compra_concluida`

### fato_concorrencia - grão: 1 linha = 1 produto x mês
`id, produto_key, data_key, preco_casanova, preco_medio_mercado`

DDL completo em `sql/schema.sql` (criado na Fase 7).
