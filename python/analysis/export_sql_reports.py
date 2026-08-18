import sqlite3
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("     FASE 8 — EXPORTAÇÃO DE RELATÓRIOS SQL (VIEWS) ")
    print("==================================================\n")

    base_dir = Path(__file__).resolve().parent.parent.parent
    db_path = base_dir / "data" / "casanova.db"
    output_dir = base_dir / "reports" / "sql_views"
    output_dir.mkdir(parents=True, exist_ok=True)

    views = [
        "vw_receita_mensal",
        "vw_performance_produto",
        "vw_rfm_clientes",
        "vw_funil_ecommerce",
        "vw_competitividade"
    ]

    conn = sqlite3.connect(db_path)

    for view in views:
        query = f"SELECT * FROM {view}"
        df = pd.read_sql_query(query, conn)
        
        output_file = output_dir / f"{view}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8")
        
        print(f"📊 View '{view}': {len(df):,} linhas exportadas -> {output_file.name}")

    conn.close()

    print(f"\n✅ Todos os relatórios analíticos foram salvos em: {output_dir}")
    print("\n==================================================")
    print("         FASE 8 CONCLUÍDA COM SUCESSO!            ")
    print("==================================================\n")

if __name__ == "__main__":
    main()