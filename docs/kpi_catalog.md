# Catálogo de KPIs

| KPI | Fórmula (DAX) | Granularidade | Fonte |
|---|---|---|---|
| Receita Total | SUM(fato_vendas[valor_liquido]) | Qualquer | fato_vendas |
| Pedidos | DISTINCTCOUNT(fato_vendas[pedido_id]) | Qualquer | fato_vendas |
| Ticket Médio | DIVIDE([Receita Total],[Pedidos]) | Qualquer | fato_vendas |
| Margem % | DIVIDE([Receita Total]-SUM(fato_vendas[custo_total]),[Receita Total]) | Qualquer | fato_vendas |
| Receita Ano Anterior | CALCULATE([Receita Total],SAMEPERIODLASTYEAR(dim_data[data])) | Mensal/Anual | fato_vendas + dim_data |
| Crescimento YoY % | DIVIDE([Receita Total]-[Receita Ano Anterior],[Receita Ano Anterior]) | Mensal/Anual | fato_vendas + dim_data |
| Taxa de Conversão E-commerce | DIVIDE(SUM(fato_funil[compra_concluida]),SUM(fato_funil[visualizacoes])) | Categoria/dispositivo | fato_funil |

> Completar conforme novas medidas forem criadas na Fase 9.
