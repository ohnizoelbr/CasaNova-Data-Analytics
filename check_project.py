import os
import shutil
from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

RAW_DIR = Path("data/raw")
EXPECTED_CSVS = [
    "clientes.csv", "lojas.csv", "produtos.csv", "pedidos.csv",
    "itens_pedido.csv", "estoque.csv", "funil_ecommerce.csv", "concorrencia_precos.csv"
]

def ensure_directories():
    """Garante que a estrutura de pastas do projeto exista."""
    dirs = [
        "data/raw", "docs", "python/analysis", "python/data_quality",
        "python/etl", "python/generation", "python/sql_load",
        "sql", "reports", "notebooks"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def recover_misplaced_csvs():
    """Procura por CSVs perdidos em subpastas e move para data/raw/."""
    print("--- [ 1. BUSCANDO ARQUIVOS NAS SUBPASTAS ] ---")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    moved_count = 0

    for file_name in EXPECTED_CSVS:
        target_path = RAW_DIR / file_name
        if not target_path.exists():
            for found_path in Path(".").rglob(file_name):
                if "raw_backup" not in str(found_path) and found_path.resolve() != target_path.resolve():
                    shutil.move(str(found_path), str(target_path))
                    print(f"  ✅ Resgatado: {found_path} -> {target_path}")
                    moved_count += 1
                    break

    if moved_count == 0:
        print("  ℹ️ Nenhum CSV novo resgatado de subpastas.")
    print()

def purge_corrupted_csvs():
    """Identifica e remove CSVs que foram corrompidos ou salvos incorretamente."""
    print("--- [ 2. SANITIZAÇÃO DE ARQUIVOS CORROMPIDOS ] ---")
    
    min_rows = {
        "clientes.csv": 1000,
        "lojas.csv": 5,
        "produtos.csv": 50,
        "pedidos.csv": 10000,
        "itens_pedido.csv": 10000,
        "estoque.csv": 1000,
        "funil_ecommerce.csv": 1000,
        "concorrencia_precos.csv": 1000
    }

    purged = 0
    for file_name in EXPECTED_CSVS:
        file_path = RAW_DIR / file_name
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                # Se tiver 1 coluna só (erro de separador) ou poucas linhas, apaga para regenerar
                if len(df.columns) <= 1 or len(df) < min_rows.get(file_name, 1):
                    print(f"  ⚠️ Removendo arquivo corrompido/incompleto: {file_name} ({len(df)} linhas, {len(df.columns)} colunas)")
                    file_path.unlink()
                    purged += 1
            except Exception:
                print(f"  ⚠️ Erro ao ler {file_name}. Apagando para recriação...")
                file_path.unlink()
                purged += 1

    if purged == 0:
        print("  ✅ Nenhum arquivo corrompido foi encontrado.")
    print()

def generate_missing_csvs():
    """Gera os CSVs faltantes com dados sintéticos válidos para o projeto."""
    print("--- [ 3. GERAÇÃO DE DADOS LIMPOS ] ---")
    np.random.seed(42)
    random.seed(42)

    # 1. lojas.csv
    if not (RAW_DIR / "lojas.csv").exists():
        print("  ⚙️ Gerando lojas.csv...")
        lojas_df = pd.DataFrame([
            {"loja_id": 1, "nome_loja": "Matriz RJ", "cidade": "Rio de Janeiro", "estado": "RJ", "tipo_canal": "Física", "data_abertura": "2018-01-15"},
            {"loja_id": 2, "nome_loja": "Filial SP", "cidade": "São Paulo", "estado": "SP", "tipo_canal": "Física", "data_abertura": "2019-05-20"},
            {"loja_id": 3, "nome_loja": "Filial BH", "cidade": "Belo Horizonte", "estado": "MG", "tipo_canal": "Física", "data_abertura": "2020-11-10"},
            {"loja_id": 4, "nome_loja": "Filial Curitiba", "cidade": "Curitiba", "estado": "PR", "tipo_canal": "Física", "data_abertura": "2021-03-01"},
            {"loja_id": 5, "nome_loja": "E-commerce Oficial", "cidade": "Rio de Janeiro", "estado": "RJ", "tipo_canal": "Online", "data_abertura": "2017-06-01"},
            {"loja_id": 6, "nome_loja": "Marketplace App", "cidade": "São Paulo", "estado": "SP", "tipo_canal": "Online", "data_abertura": "2021-08-15"},
            {"loja_id": 7, "nome_loja": "Filial Porto Alegre", "cidade": "Porto Alegre", "estado": "RS", "tipo_canal": "Física", "data_abertura": "2022-02-10"}
        ])
        lojas_df.to_csv(RAW_DIR / "lojas.csv", index=False)

    # 2. produtos.csv
    if not (RAW_DIR / "produtos.csv").exists():
        print("  ⚙️ Gerando produtos.csv...")
        cats = ["Móveis", "Decoração", "Iluminação", "Cozinha", "Jardim", "Banheiro"]
        prods = []
        for i in range(1, 151):
            cat = random.choice(cats)
            preco = round(random.uniform(20.0, 2500.0), 2)
            custo = round(preco * random.uniform(0.4, 0.7), 2)
            prods.append({
                "produto_id": i,
                "nome_produto": f"Produto {cat} {i}",
                "categoria": cat,
                "preco_tabela": preco,
                "custo": custo,
                "ativo": 1
            })
        prods_df = pd.DataFrame(prods)
        prods_df.loc[0:5, "categoria"] = np.nan
        prods_df.to_csv(RAW_DIR / "produtos.csv", index=False)

    # 3. clientes.csv
    if not (RAW_DIR / "clientes.csv").exists():
        print("  ⚙️ Gerando clientes.csv...")
        cidades = [("Rio de Janeiro", "RJ"), ("São Paulo", "SP"), ("Belo Horizonte", "MG"), ("Curitiba", "PR"), ("Niterói", "RJ")]
        cli = []
        start_date = datetime(2020, 1, 1)
        for i in range(1, 12001):
            cid, est = random.choice(cidades)
            dt_cad = start_date + timedelta(days=random.randint(0, 1400))
            cli.append({
                "cliente_id": i,
                "nome": f"Cliente {i}",
                "cpf": f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}",
                "email": f"cliente{i}@email.com" if i > 600 else np.nan,
                "telefone": f"(21) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "cidade": cid,
                "estado": est,
                "data_cadastro": dt_cad.strftime("%Y-%m-%d")
            })
        pd.DataFrame(cli).to_csv(RAW_DIR / "clientes.csv", index=False)

    # 4. pedidos.csv & 5. itens_pedido.csv
    if not (RAW_DIR / "pedidos.csv").exists() or not (RAW_DIR / "itens_pedido.csv").exists():
        print("  ⚙️ Gerando pedidos.csv e itens_pedido.csv...")
        pedidos = []
        itens = []
        item_id_seq = 1
        start_date = datetime(2022, 1, 1)
        status_list = ["Entregue", "Entregue", "Entregue", "Cancelado", "Pendente"]
        canals = ["Física", "Online", "App"]

        prods_df = pd.read_csv(RAW_DIR / "produtos.csv")

        for p_id in range(1, 45905):
            c_id = random.randint(1, 12000)
            l_id = random.randint(1, 7)
            dt = start_date + timedelta(days=random.randint(0, 730), minutes=random.randint(0, 1440))
            
            pedidos.append({
                "pedido_id": p_id,
                "cliente_id": c_id,
                "loja_id": l_id,
                "canal": random.choice(canals),
                "data_pedido": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "status": random.choice(status_list)
            })

            n_itens = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
            for _ in range(n_itens):
                prod = prods_df.sample(1).iloc[0]
                qtd = random.randint(1, 4)
                desc = round(random.uniform(0, 0.15), 2) if random.random() > 0.7 else 0.0
                itens.append({
                    "item_id": item_id_seq,
                    "pedido_id": p_id,
                    "produto_id": int(prod["produto_id"]),
                    "quantidade": qtd,
                    "preco_unitario": float(prod["preco_tabela"]),
                    "desconto": desc
                })
                item_id_seq += 1

        pd.DataFrame(pedidos).to_csv(RAW_DIR / "pedidos.csv", index=False)
        pd.DataFrame(itens).to_csv(RAW_DIR / "itens_pedido.csv", index=False)

    # 6. estoque.csv
    if not (RAW_DIR / "estoque.csv").exists():
        print("  ⚙️ Gerando estoque.csv...")
        est = []
        for prod_id in range(1, 151):
            for loja_id in range(1, 7):
                for month in range(1, 29):
                    est.append({
                        "produto_id": prod_id,
                        "loja_id": loja_id,
                        "data_snapshot": (datetime(2023, 1, 1) + timedelta(days=month*14)).strftime("%Y-%m-%d"),
                        "quantidade_disponivel": random.randint(0, 150)
                    })
        pd.DataFrame(est).to_csv(RAW_DIR / "estoque.csv", index=False)

    # 7. funil_ecommerce.csv
    if not (RAW_DIR / "funil_ecommerce.csv").exists():
        print("  ⚙️ Gerando funil_ecommerce.csv...")
        funil = []
        cats = ["Móveis", "Decoração", "Iluminação", "Cozinha", "Jardim", "Banheiro"]
        devs = ["Desktop", "Mobile", "Tablet"]
        curr_dt = datetime(2022, 1, 1)
        while curr_dt <= datetime(2023, 12, 31):
            for c in cats:
                for d in devs:
                    views = random.randint(1000, 5000)
                    carrinho = int(views * random.uniform(0.1, 0.25))
                    chk = int(carrinho * random.uniform(0.4, 0.7))
                    comp = int(chk * random.uniform(0.6, 0.9))
                    funil.append({
                        "data": curr_dt.strftime("%Y-%m-%d"),
                        "categoria": c,
                        "dispositivo": d,
                        "visualizacoes": views,
                        "add_carrinho": carrinho,
                        "checkout_iniciado": chk,
                        "compra_concluida": comp
                    })
            curr_dt += timedelta(days=1)
        pd.DataFrame(funil).to_csv(RAW_DIR / "funil_ecommerce.csv", index=False)

    # 8. concorrencia_precos.csv
    if not (RAW_DIR / "concorrencia_precos.csv").exists():
        print("  ⚙️ Gerando concorrencia_precos.csv...")
        conc = []
        prods_df = pd.read_csv(RAW_DIR / "produtos.csv")
        months = [(datetime(2022, 1, 1) + timedelta(days=30*m)).strftime("%Y-%m") for m in range(24)]
        for _, prod in prods_df.iterrows():
            p_base = float(prod["preco_tabela"])
            for m in months:
                conc.append({
                    "produto_id": int(prod["produto_id"]),
                    "mes_referencia": m,
                    "preco_casanova": p_base,
                    "preco_medio_mercado": round(p_base * random.uniform(0.85, 1.15), 2)
                })
        pd.DataFrame(conc).to_csv(RAW_DIR / "concorrencia_precos.csv", index=False)

    print("  ✅ Processamento de CSVs concluído.\n")

def run_diagnostics():
    """Valida o estado final de todos os arquivos em data/raw/."""
    print("--- [ 4. DIAGNÓSTICO FINAL DOS DADOS ] ---")
    csv_data = {}
    all_ok = True

    for file_name in EXPECTED_CSVS:
        file_path = RAW_DIR / file_name
        if not file_path.exists():
            print(f"  ❌ FALTANDO: {file_name}")
            all_ok = False
            continue

        df = pd.read_csv(file_path)
        csv_data[file_name] = df
        print(f"  ✅ {file_name:<25} | Linhas: {len(df):>7} | Colunas: {len(df.columns):>2}")

    print()
    if "pedidos.csv" in csv_data and "itens_pedido.csv" in csv_data:
        p_count = len(csv_data["pedidos.csv"])
        i_count = len(csv_data["itens_pedido.csv"])
        avg = i_count / p_count if p_count > 0 else 0
        print(f"  📊 Média de itens por pedido: {avg:.2f} (esperado ~1.8)")

    return all_ok

def main():
    print("==================================================")
    print("     CORREÇÃO E AUTOGERAÇÃO DO PROJETO CASANOVA   ")
    print("==================================================\n")

    ensure_directories()
    recover_misplaced_csvs()
    purge_corrupted_csvs()
    generate_missing_csvs()
    ok = run_diagnostics()

    print("==================================================")
    if ok:
        print("RESULTADO: ✅ PROJETO TOTALMENTE CORRIGIDO E PRONTO!")
    else:
        print("RESULTADO: ⚠️ Ainda existem inconsistências nos arquivos.")
    print("==================================================\n")

if __name__ == "__main__":
    main()