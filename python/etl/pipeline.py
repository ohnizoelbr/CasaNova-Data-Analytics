import os
from pathlib import Path
import pandas as pd

def main():
    print("==================================================")
    print("        FASE 6 — PIPELINE DE ETL (TRATAMENTO)     ")
    print("==================================================\n")

    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clientes
    print("⚡ Processando: clientes.csv")
    df_clientes = pd.read_csv(raw_dir / "clientes.csv")
    df_clientes["email"] = df_clientes["email"].fillna("sem_email@casanova.com.br")
    df_clientes["data_cadastro"] = pd.to_datetime(df_clientes["data_cadastro"])
    df_clientes.to_csv(processed_dir / "clientes.csv", index=False, encoding="utf-8")

    # 2. Lojas
    print("⚡ Processando: lojas.csv")
    df_lojas = pd.read_csv(raw_dir / "lojas.csv")
    df_lojas["data_abertura"] = pd.to_datetime(df_lojas["data_abertura"])
    df_lojas.to_csv(processed_dir / "lojas.csv", index=False, encoding="utf-8")

    # 3. Produtos
    print("⚡ Processando: produtos.csv")
    df_produtos = pd.read_csv(raw_dir / "produtos.csv")
    df_produtos["categoria"] = df_produtos["categoria"].fillna("Outros")
    df_produtos.to_csv(processed_dir / "produtos.csv", index=False, encoding="utf-8")

    # 4. Pedidos
    print("⚡ Processando: pedidos.csv")
    df_pedidos = pd.read_csv(raw_dir / "pedidos.csv")
    df_pedidos["data_pedido"] = pd.to_datetime(df_pedidos["data_pedido"])
    df_pedidos.to_csv(processed_dir / "pedidos.csv", index=False, encoding="utf-8")

    # 5. Itens Pedido
    print("⚡ Processando: itens_pedido.csv")
    df_itens = pd.read_csv(raw_dir / "itens_pedido.csv")
    df_itens["valor_total_item"] = (df_itens["quantidade"] * df_itens["preco_unitario"]) - df_itens["desconto"]
    df_itens.to_csv(processed_dir / "itens_pedido.csv", index=False, encoding="utf-8")

    # 6. Estoque
    print("⚡ Processando: estoque.csv")
    df_estoque = pd.read_csv(raw_dir / "estoque.csv")
    df_estoque["data_snapshot"] = pd.to_datetime(df_estoque["data_snapshot"])
    df_estoque.to_csv(processed_dir / "estoque.csv", index=False, encoding="utf-8")

    # 7. Funil E-commerce
    print("⚡ Processando: funil_ecommerce.csv")
    df_funil = pd.read_csv(raw_dir / "funil_ecommerce.csv")
    df_funil["data"] = pd.to_datetime(df_funil["data"])
    df_funil["categoria"] = df_funil["categoria"].fillna("Outros")
    df_funil.to_csv(processed_dir / "funil_ecommerce.csv", index=False, encoding="utf-8")

    # 8. Concorrência Preços
    print("⚡ Processando: concorrencia_precos.csv")
    df_conc = pd.read_csv(raw_dir / "concorrencia_precos.csv")
    df_conc.to_csv(processed_dir / "concorrencia_precos.csv", index=False, encoding="utf-8")

    print(f"\n✅ As 8 tabelas foram tratadas e salvas em: {processed_dir}")
    print("\n==================================================")
    print("         FASE 6 CONCLUÍDA COM SUCESSO!            ")
    print("==================================================\n")

if __name__ == "__main__":
    main()