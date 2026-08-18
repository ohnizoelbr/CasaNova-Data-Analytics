import os
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("     FASE 4 — ANÁLISE EXPLORATÓRIA DE DADOS (EDA)  ")
    print("==================================================\n")

    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_files = [
        "clientes.csv", "lojas.csv", "produtos.csv", "pedidos.csv",
        "itens_pedido.csv", "estoque.csv", "funil_ecommerce.csv", "concorrencia_precos.csv"
    ]

    report_lines = []
    report_lines.append("RAIO-X ESTATÍSTICO DAS TABELAS (DATA/RAW)\n" + "="*50 + "\n")

    for filename in csv_files:
        filepath = raw_dir / filename
        if not filepath.exists():
            print(f"⚠️ Arquivo não encontrado: {filename}")
            continue

        df = pd.read_csv(filepath)
        n_rows, n_cols = df.shape
        duplicates = df.duplicated().sum()
        null_counts = df.isnull().sum()
        nulls_str = ", ".join([f"{col}: {cnt}" for col, cnt in null_counts.items() if cnt > 0])
        if not nulls_str:
            nulls_str = "Nenhum"

        summary = (
            f"📄 TABELA: {filename}\n"
            f"   • Dimensão: {n_rows} linhas x {n_cols} colunas\n"
            f"   • Linhas Duplicadas: {duplicates}\n"
            f"   • Val. Nulos por Coluna: {nulls_str}\n"
            f"   • Colunas ({n_cols}): {list(df.columns)}\n"
        )
        print(summary)
        report_lines.append(summary + "-"*50 + "\n")

    output_txt = reports_dir / "eda_summary.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"✅ Diagnóstico salvo com sucesso em: {output_txt}")
    print("\n==================================================")
    print("  FASE 4 CONCLUÍDA COM SUCESSO!                    ")
    print("==================================================\n")

if __name__ == "__main__":
    main()