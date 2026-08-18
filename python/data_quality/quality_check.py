import os
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("       FASE 5 — DATA QUALITY CHECK (RAW)          ")
    print("==================================================\n")

    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    quality_dir = base_dir / "data" / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    # 1. Carregar Tabelas Brutas
    try:
        df_clientes = pd.read_csv(raw_dir / "clientes.csv")
        df_lojas = pd.read_csv(raw_dir / "lojas.csv")
        df_produtos = pd.read_csv(raw_dir / "produtos.csv")
        df_pedidos = pd.read_csv(raw_dir / "pedidos.csv")
        df_itens = pd.read_csv(raw_dir / "itens_pedido.csv")
        df_estoque = pd.read_csv(raw_dir / "estoque.csv")
        df_funil = pd.read_csv(raw_dir / "funil_ecommerce.csv")
        df_concorrencia = pd.read_csv(raw_dir / "concorrencia_precos.csv")
        print("  ✅ Todas as tabelas foram carregadas para auditoria.\n")
    except Exception as e:
        print(f"  ❌ Erro ao carregar arquivos: {e}")
        return

    reports = []

    def add_check(tabela, coluna, regra, violacoes, total, severidade_se_erro="WARNING"):
        pct = round((violacoes / total) * 100, 2) if total > 0 else 0
        status = "OK" if violacoes == 0 else severidade_se_erro
        reports.append({
            "tabela": tabela,
            "coluna": coluna,
            "regra": regra,
            "numero_violacoes": violacoes,
            "pct_violacoes": pct,
            "status": status
        })

    # --- 1. COMPLETUDE (Nulos) ---
    print("--- [ 1. CHECANDO COMPLETUDE ] ---")
    for name, df in [
        ("clientes", df_clientes), ("lojas", df_lojas), ("produtos", df_produtos),
        ("pedidos", df_pedidos), ("itens_pedido", df_itens), ("estoque", df_estoque),
        ("funil_ecommerce", df_funil), ("concorrencia_precos", df_concorrencia)
    ]:
        for col in df.columns:
            nulos = df[col].isnull().sum()
            sev = "WARNING" if name in ["clientes", "produtos"] else "CRITICAL"
            add_check(name, col, "Não Nulo (Completude)", nulos, len(df), sev)

    # --- 2. UNICIDADE (Duplicados de Chave) ---
    print("--- [ 2. CHECANDO UNICIDADE E CHAVES ] ---")
    add_check("clientes", "cliente_id", "Chave Primária Única", df_clientes["cliente_id"].duplicated().sum(), len(df_clientes), "CRITICAL")
    add_check("clientes", "cpf", "CPF Único", df_clientes["cpf"].dropna().duplicated().sum(), len(df_clientes), "WARNING")
    add_check("produtos", "produto_id", "Chave Primária Única", df_produtos["produto_id"].duplicated().sum(), len(df_produtos), "CRITICAL")
    add_check("lojas", "loja_id", "Chave Primária Única", df_lojas["loja_id"].duplicated().sum(), len(df_lojas), "CRITICAL")
    add_check("pedidos", "pedido_id", "Chave Primária Única", df_pedidos["pedido_id"].duplicated().sum(), len(df_pedidos), "CRITICAL")
    add_check("itens_pedido", "item_id", "Chave Primária Única", df_itens["item_id"].duplicated().sum(), len(df_itens), "CRITICAL")

    # --- 3. VALIDADE DE VALORES (Preços e Quantidades) ---
    print("--- [ 3. CHECANDO REGRAS DE VALIDADE ] ---")
    add_check("produtos", "preco_tabela", "Preço > 0", (df_produtos["preco_tabela"] <= 0).sum(), len(df_produtos), "CRITICAL")
    add_check("produtos", "custo", "Custo > 0", (df_produtos["custo"] <= 0).sum(), len(df_produtos), "CRITICAL")
    add_check("itens_pedido", "quantidade", "Quantidade > 0", (df_itens["quantidade"] <= 0).sum(), len(df_itens), "CRITICAL")
    add_check("itens_pedido", "preco_unitario", "Preço Unitário > 0", (df_itens["preco_unitario"] <= 0).sum(), len(df_itens), "CRITICAL")
    add_check("estoque", "quantidade_disponivel", "Estoque >= 0", (df_estoque["quantidade_disponivel"] < 0).sum(), len(df_estoque), "WARNING")

    # --- 4. INTEGRIDADE REFERENCIAL ---
    print("--- [ 4. CHECANDO INTEGRIDADE REFERENCIAL ] ---")
    pedidos_invalid_cli = (~df_pedidos["cliente_id"].astype(str).isin(df_clientes["cliente_id"].astype(str))).sum()
    add_check("pedidos", "cliente_id", "FK em clientes.csv", pedidos_invalid_cli, len(df_pedidos), "CRITICAL")

    pedidos_invalid_loja = (~df_pedidos["loja_id"].astype(str).isin(df_lojas["loja_id"].astype(str))).sum()
    add_check("pedidos", "loja_id", "FK em lojas.csv", pedidos_invalid_loja, len(df_pedidos), "CRITICAL")

    itens_invalid_ped = (~df_itens["pedido_id"].astype(str).isin(df_pedidos["pedido_id"].astype(str))).sum()
    add_check("itens_pedido", "pedido_id", "FK em pedidos.csv", itens_invalid_ped, len(df_itens), "CRITICAL")

    itens_invalid_prod = (~df_itens["produto_id"].astype(str).isin(df_produtos["produto_id"].astype(str))).sum()
    add_check("itens_pedido", "produto_id", "FK em produtos.csv", itens_invalid_prod, len(df_itens), "CRITICAL")

    estoque_invalid_prod = (~df_estoque["produto_id"].astype(str).isin(df_produtos["produto_id"].astype(str))).sum()
    add_check("estoque", "produto_id", "FK em produtos.csv", estoque_invalid_prod, len(df_estoque), "WARNING")

    # --- 5. EXPORTAÇÃO DO RELATÓRIO ---
    df_report = pd.DataFrame(reports)
    output_report = quality_dir / "quality_report.csv"
    df_report.to_csv(output_report, index=False, encoding="utf-8")

    total_regras = len(df_report)
    violacoes_totais = len(df_report[df_report["status"] != "OK"])

    print(f"\n  ✅ Auditoria finalizada: {total_regras} regras auditadas.")
    print(f"  ⚠️ Quantidade de testes com inconformidades: {violacoes_totais}")
    print(f"  📄 Relatório salvo em: {output_report}")
    print("\n==================================================")
    print("         FASE 5 CONCLUÍDA COM SUCESSO!            ")
    print("==================================================\n")

if __name__ == "__main__":
    main()