import os
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("     GERAÇÃO DO RELATÓRIO CONSOLIDADO (FASE 3)   ")
    print("==================================================\n")

    # Garante a resolução correta dos caminhos independentemente de onde o script é executado
    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Carregar os CSVs sanitizados
    print("--- [ 1. LENDO DADOS DE DATA/RAW ] ---")
    try:
        df_pedidos = pd.read_csv(raw_dir / "pedidos.csv")
        df_itens = pd.read_csv(raw_dir / "itens_pedido.csv")
        df_produtos = pd.read_csv(raw_dir / "produtos.csv")
        df_lojas = pd.read_csv(raw_dir / "lojas.csv")
        df_clientes = pd.read_csv(raw_dir / "clientes.csv")
        print("  ✅ Todos os CSVs foram carregados com sucesso.\n")
    except Exception as e:
        print(f"  ❌ Erro ao ler CSVs: {e}")
        return

    # Padronizar colunas de identificação como string para evitar inconsistência de tipos
    id_cols = ["pedido_id", "produto_id", "loja_id", "cliente_id"]
    for df in [df_pedidos, df_itens, df_produtos, df_lojas, df_clientes]:
        for col in id_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

    # Garantir conversão numérica nos itens
    df_itens["quantidade"] = pd.to_numeric(df_itens["quantidade"], errors="coerce").fillna(0)
    df_itens["preco_unitario"] = pd.to_numeric(df_itens["preco_unitario"], errors="coerce").fillna(0)
    df_itens["desconto"] = pd.to_numeric(df_itens["desconto"], errors="coerce").fillna(0)

    # 2. Calcular Receita Líquida por Item
    df_itens["receita_item"] = (
        df_itens["quantidade"] * df_itens["preco_unitario"] * (1 - df_itens["desconto"])
    )

    # 3. Cruzamento das Tabelas
    print("--- [ 2. PROCESSANDO E CRUZANDO DADOS ] ---")
    
    df_lojas_prep = df_lojas[["loja_id", "nome_loja", "cidade", "estado", "tipo_canal"]].rename(
        columns={"cidade": "cidade_loja", "estado": "estado_loja"}
    )
    df_clientes_prep = df_clientes[["cliente_id", "cidade", "estado"]].rename(
        columns={"cidade": "cidade_cliente", "estado": "estado_cliente"}
    )
    df_produtos_prep = df_produtos[["produto_id", "categoria", "nome_produto"]]

    df_merged = (
        df_itens
        .merge(df_pedidos, on="pedido_id", how="inner")
        .merge(df_produtos_prep, on="produto_id", how="left")
        .merge(df_lojas_prep, on="loja_id", how="left")
        .merge(df_clientes_prep, on="cliente_id", how="left")
    )

    # Tratar data para extrair o mês/ano
    df_merged["data_pedido"] = pd.to_datetime(df_merged["data_pedido"], errors="coerce")
    df_merged["ano_mes"] = df_merged["data_pedido"].dt.to_period("M").astype(str)

    # --- Visão 1: Vendas por Cidade do Cliente ---
    v1_cidade = (
        df_merged.groupby(["cidade_cliente", "estado_cliente"], dropna=False)
        .agg(
            total_pedidos=("pedido_id", "nunique"),
            itens_vendidos=("quantidade", "sum"),
            receita_total=("receita_item", "sum")
        )
        .reset_index()
        .sort_values(by="receita_total", ascending=False)
    )

    # --- Visão 2: Vendas por Categoria ---
    v2_categoria = (
        df_merged.groupby("categoria", dropna=False)
        .agg(
            itens_vendidos=("quantidade", "sum"),
            total_pedidos=("pedido_id", "nunique"),
            receita_total=("receita_item", "sum")
        )
        .reset_index()
        .sort_values(by="receita_total", ascending=False)
    )

    # --- Visão 3: Evolução Mensal de Pedidos e Receita ---
    v3_mensal = (
        df_merged.groupby("ano_mes", dropna=False)
        .agg(
            total_pedidos=("pedido_id", "nunique"),
            itens_vendidos=("quantidade", "sum"),
            receita_total=("receita_item", "sum")
        )
        .reset_index()
        .sort_values(by="ano_mes")
    )

    # --- Visão 4: Receita por Loja e Canal ---
    v4_loja_canal = (
        df_merged.groupby(["nome_loja", "tipo_canal", "cidade_loja"], dropna=False)
        .agg(
            total_pedidos=("pedido_id", "nunique"),
            receita_total=("receita_item", "sum")
        )
        .reset_index()
        .sort_values(by="receita_total", ascending=False)
    )

    # 4. Exportação para Excel
    print("--- [ 3. GERANDO PLANILHA DE SAÍDA ] ---")
    output_excel = reports_dir / "relatorio_fase3.xlsx"

    try:
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            v1_cidade.to_excel(writer, sheet_name="Por Cidade", index=False)
            v2_categoria.to_excel(writer, sheet_name="Por Categoria", index=False)
            v3_mensal.to_excel(writer, sheet_name="Evolucao Mensal", index=False)
            v4_loja_canal.to_excel(writer, sheet_name="Por Loja e Canal", index=False)
        print(f"  ✅ Arquivo Excel gerado em: {output_excel}")
    except Exception as e:
        print(f"  ⚠️ Aviso ao gerar Excel ({e}). Gerando arquivos CSV individuais...")
        v1_cidade.to_csv(reports_dir / "fase3_cidade.csv", index=False)
        v2_categoria.to_csv(reports_dir / "fase3_categoria.csv", index=False)
        v3_mensal.to_csv(reports_dir / "fase3_mensal.csv", index=False)
        v4_loja_canal.to_csv(reports_dir / "fase3_loja_canal.csv", index=False)
        print("  ✅ CSVs salvos na pasta reports/.")

    print("\n==================================================")
    print("  PRONTO! Agora é só abrir a pasta 'reports' e   ")
    print("  utilizar a planilha 'relatorio_fase3.xlsx'.    ")
    print("==================================================\n")

if __name__ == "__main__":
    main()