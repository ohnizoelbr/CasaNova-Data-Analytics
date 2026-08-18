# Metodologia e Decisões Técnicas

| Decisão | Escolha | Motivo |
|---|---|---|
| Banco SQL | SQLite | Zero setup de servidor, arquivo único, suporta CTE e Window Functions |
| Funil de e-commerce | Agregado (dia x categoria x dispositivo), não clickstream por sessão | Volume proporcional ao ganho analítico - o agregado já responde onde há abandono |
| Preços de concorrência | 100% sintéticos | Não há coleta real de Amazon/Mercado Livre - deixar isso explícito evita confundir dado simulado com dado real |
| Custo do produto | Custo atual, não histórico | Simplificação assumida para o escopo do projeto |
| CPF dos clientes | Mascarado no ETL, não replicado no modelo analítico | Boa prática mesmo em dado sintético (referência: LGPD) |
| Seed de geração dos dados | Fixo | Reprodutibilidade - qualquer pessoa que rodar o script gera a mesma base |

> Adicionar uma linha aqui sempre que uma decisão técnica relevante for tomada
> em qualquer fase do projeto - é esse histórico que demonstra raciocínio, não
> só o resultado final.
