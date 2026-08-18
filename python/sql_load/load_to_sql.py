import sqlite3
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("      FASE 7 — CARGA SQL E CRIAÇÃO DE VIEWS       ")
    print("==================================================\n")

    base_dir = Path(__file__).resolve().parent.parent.parent
    processed_dir = base_dir / "data" / "processed"
    data_dir = base_dir / "data"
    db_path = data_dir / "casanova.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"📦 Banco de dados SQLite: {db_path}\n")

    # 1. Carga das tabelas tratadas
    print("--- [ 1. CARREGANDO TABELAS PROCESSADAS ] ---")
    tables = [
        "clientes", "lojas", "produtos", "pedidos",
        "itens_pedido", "estoque", "funil_ecommerce", "concorrencia_precos"
    ]

    for table in tables:
        csv_path = processed_dir / f"{table}.csv"
        if not csv_path.exists():
            print(f"⚠️ Arquivo não encontrado: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  • Tabela '{table}': {count:,} registros inseridos.")

    # 2. Criação das Views Analíticas (CTE, Window Functions)
    print("\n--- [ 2. CRIANDO VIEWS ANALÍTICAS EM SQL ] ---")

    views = {
        "vw_receita_mensal": """
            CREATE VIEW IF NOT EXISTS vw_receita_mensal AS
            SELECT 
                strftime('%Y-%m', p.data_pedido) AS ano_mes,
                COUNT(DISTINCT p.pedido_id) AS total_pedidos,
                ROUND(SUM(i.valor_total_item), 2) AS receita_total,
                ROUND(SUM(i.valor_total_item) / COUNT(DISTINCT p.pedido_id), 2) AS ticket_medio
            FROM pedidos p
            JOIN itens_pedido i ON p.pedido_id = i.pedido_id
            GROUP BY ano_mes
            ORDER BY ano_mes;
        """,
        "vw_performance_produto": """
            CREATE VIEW IF NOT EXISTS vw_performance_produto AS
            SELECT 
                pr.categoria,
                pr.nome_produto,
                SUM(i.quantidade) AS qtd_vendida,
                ROUND(SUM(i.valor_total_item), 2) AS receita_total,
                RANK() OVER (PARTITION BY pr.categoria ORDER BY SUM(i.valor_total_item) DESC) AS ranking_categoria
            FROM itens_pedido i
            JOIN produtos pr ON i.produto_id = pr.produto_id
            GROUP BY pr.categoria, pr.nome_produto;
        """,
        "vw_rfm_clientes": """
            CREATE VIEW IF NOT EXISTS vw_rfm_clientes AS
            WITH base_rfm AS (
                SELECT 
                    p.cliente_id,
                    CAST(julianday('2025-12-31') - julianday(MAX(p.data_pedido)) AS INT) AS recencia_dias,
                    COUNT(DISTINCT p.pedido_id) AS frequencia,
                    ROUND(SUM(i.valor_total_item), 2) AS monetario
                FROM pedidos p
                JOIN itens_pedido i ON p.pedido_id = i.pedido_id
                GROUP BY p.cliente_id
            )
            SELECT 
                cliente_id,
                recencia_dias,
                frequencia,
                monetario,
                NTILE(5) OVER (ORDER BY recencia_dias DESC) AS score_r,
                NTILE(5) OVER (ORDER BY frequencia ASC) AS score_f,
                NTILE(5) OVER (ORDER BY monetario ASC) AS score_m
            FROM base_rfm;
        """,
        "vw_funil_ecommerce": """
            CREATE VIEW IF NOT EXISTS vw_funil_ecommerce AS
            SELECT 
                categoria,
                SUM(visualizacoes) AS total_visualizacoes,
                SUM(checkout_iniciado) AS total_checkouts,
                SUM(compra_concluida) AS total_compras,
                ROUND(SUM(compra_concluida) * 100.0 / NULLIF(SUM(visualizacoes), 0), 2) AS taxa_conversao_pct,
                ROUND((SUM(checkout_iniciado) - SUM(compra_concluida)) * 100.0 / NULLIF(SUM(checkout_iniciado), 0), 2) AS taxa_abandono_checkout_pct
            FROM funil_ecommerce
            GROUP BY categoria
            ORDER BY taxa_conversao_pct ASC;
        """,
  "vw_competitividade": """
            CREATE VIEW IF NOT EXISTS vw_competitividade AS
            SELECT 
                pr.categoria,
                pr.nome_produto,
                c.preco_casanova,
                c.preco_medio_mercado,
                ROUND((c.preco_casanova - c.preco_medio_mercado) * 100.0 / c.preco_medio_mercado, 2) AS gap_pct
            FROM concorrencia_precos c
            JOIN produtos pr 
              ON CAST(REPLACE(c.produto_id, 'P', '') AS INTEGER) = CAST(pr.produto_id AS INTEGER)
            ORDER BY gap_pct DESC;
        """
    }

    for view_name, sql_script in views.items():
        cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        cursor.execute(sql_script)
        print(f"  ✅ View '{view_name}' criada com sucesso.")

    conn.commit()
    conn.close()

    print(f"\n✅ Banco 'casanova.db' populado com tabelas e views em: {db_path}")
    print("\n==================================================")
    print("         FASE 7 CONCLUÍDA COM SUCESSO!            ")
    print("==================================================\n")

if __name__ == "__main__":
    main()