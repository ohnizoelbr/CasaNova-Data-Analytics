# Dicionário de Dados

> Cobre a camada `data/processed` (pós-ETL, Fase 6). O modelo dimensional
> (`dim_*` / `fato_*`) está descrito em `docs/data_model.md`.

## clientes
| Coluna | Tipo | Descrição |
|---|---|---|
| cliente_id | texto | Identificador original do cliente |
| nome | texto | Nome do cliente |
| cpf | texto | Mascarado no ETL (Fase 6) |
| email | texto | E-mail de contato |
| telefone | texto | Telefone de contato |
| cidade | texto | Cidade, padronizada no ETL |
| estado | texto | UF |
| data_cadastro | data | Data de cadastro do cliente |

## lojas
| Coluna | Tipo | Descrição |
|---|---|---|
| loja_id | texto | Identificador da loja |
| nome_loja | texto | Nome comercial |
| cidade | texto | Cidade, padronizada no ETL |
| estado | texto | UF |
| tipo_canal | texto | 'fisica' ou 'ecommerce' |
| data_abertura | data | Data de abertura/lançamento do canal |

## produtos
| Coluna | Tipo | Descrição |
|---|---|---|
| produto_id | texto | Identificador do produto |
| nome_produto | texto | Nome do produto |
| categoria | texto | Categoria, padronizada no ETL |
| preco_tabela | numérico | Preço de tabela (R$) |
| custo | numérico | Custo unitário atual (R$) |
| ativo | booleano | Se o produto está ativo no catálogo |

## pedidos
| Coluna | Tipo | Descrição |
|---|---|---|
| pedido_id | texto | Identificador do pedido |
| cliente_id | texto | Cliente que fez o pedido |
| loja_id | texto | Loja/canal onde o pedido foi feito |
| canal | texto | 'fisico' ou 'ecommerce' |
| data_pedido | data | Data do pedido |
| status | texto | Status do pedido, padronizado no ETL |

## itens_pedido
| Coluna | Tipo | Descrição |
|---|---|---|
| item_id | texto | Identificador do item |
| pedido_id | texto | Pedido ao qual o item pertence |
| produto_id | texto | Produto vendido |
| quantidade | inteiro | Quantidade vendida |
| preco_unitario | numérico | Preço praticado no momento da venda |
| desconto | numérico | Desconto aplicado (R$) |

## estoque
| Coluna | Tipo | Descrição |
|---|---|---|
| produto_id | texto | Produto |
| loja_id | texto | Loja |
| data_snapshot | data | Data do snapshot mensal |
| quantidade_disponivel | inteiro | Quantidade disponível na loja |

## funil_ecommerce
| Coluna | Tipo | Descrição |
|---|---|---|
| data | data | Dia de referência |
| categoria | texto | Categoria de produto |
| dispositivo | texto | 'mobile' ou 'desktop' |
| visualizacoes | inteiro | Número de visualizações de produto |
| add_carrinho | inteiro | Número de adições ao carrinho |
| checkout_iniciado | inteiro | Número de checkouts iniciados |
| compra_concluida | inteiro | Número de compras concluídas |

## concorrencia_precos
| Coluna | Tipo | Descrição |
|---|---|---|
| produto_id | texto | Produto |
| mes_referencia | data | Mês de referência |
| preco_casanova | numérico | Preço praticado pela CasaNova |
| preco_medio_mercado | numérico | Preço médio de mercado - 100% sintético, ver `methodology.md` |
