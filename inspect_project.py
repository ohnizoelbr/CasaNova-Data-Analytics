from pathlib import Path
import os
import pandas as pd


# ============================================================
# CASANOVA DATA ANALYTICS
# INSPEÇÃO COMPLETA DO PROJETO
# NÃO ALTERA NENHUM ARQUIVO
# ============================================================

ROOT = Path(__file__).resolve().parent

print("=" * 80)
print("CASANOVA DATA ANALYTICS — INSPEÇÃO COMPLETA DO PROJETO")
print("=" * 80)

print(f"\nRAIZ DO PROJETO:")
print(ROOT)


# ============================================================
# 1. ESTRUTURA DE PASTAS
# ============================================================

print("\n" + "=" * 80)
print("1. ESTRUTURA DE PASTAS")
print("=" * 80)

expected_dirs = [
    "data",
    "data/raw",
    "data/processed",
    "data/quality",
    "data/star_schema",
    "docs",
    "python",
    "python/analysis",
    "python/data_quality",
    "python/etl",
    "python/generation",
    "python/sql_load",
    "sql",
    "sql/staging",
    "sql/dimensions",
    "sql/facts",
    "sql/analytics",
    "reports",
    "reports/images",
    "notebooks",
]

for directory in expected_dirs:
    path = ROOT / directory

    if path.exists():
        print(f"[OK]    {directory}")
    else:
        print(f"[AUSENTE] {directory}")


# ============================================================
# 2. ARQUIVOS DE PYTHON
# ============================================================

print("\n" + "=" * 80)
print("2. ARQUIVOS PYTHON")
print("=" * 80)

py_files = sorted(ROOT.rglob("*.py"))

# Ignorar possíveis caches
py_files = [
    p for p in py_files
    if "__pycache__" not in p.parts
]

if not py_files:
    print("Nenhum arquivo Python encontrado.")
else:
    for path in py_files:
        print(
            f"[PY] {path.relative_to(ROOT)} "
            f"({path.stat().st_size:,} bytes)"
        )


# ============================================================
# 3. ARQUIVOS DE DOCUMENTAÇÃO
# ============================================================

print("\n" + "=" * 80)
print("3. DOCUMENTAÇÃO")
print("=" * 80)

docs_files = []

for pattern in [
    "*.md",
    "*.txt",
]:

    docs_files.extend(ROOT.rglob(pattern))

docs_files = sorted(
    set(docs_files)
)

if not docs_files:
    print("Nenhum documento encontrado.")
else:
    for path in docs_files:
        if "__pycache__" not in path.parts:
            print(
                f"[DOC] {path.relative_to(ROOT)} "
                f"({path.stat().st_size:,} bytes)"
            )


# ============================================================
# 4. CSVs
# ============================================================

print("\n" + "=" * 80)
print("4. CSVs ENCONTRADOS")
print("=" * 80)

csv_files = sorted(ROOT.rglob("*.csv"))

if not csv_files:
    print("Nenhum CSV encontrado.")

else:

    for path in csv_files:

        if "__pycache__" in path.parts:
            continue

        try:
            df = pd.read_csv(
                path,
                encoding="utf-8-sig"
            )

            relative = path.relative_to(ROOT)

            print("\n----------------------------------------")
            print(relative)
            print(f"Tamanho: {path.stat().st_size:,} bytes")
            print(f"Linhas: {len(df):,}")
            print(f"Colunas: {len(df.columns)}")

            print(
                "Colunas: "
                + ", ".join(str(c) for c in df.columns)
            )

        except Exception as exc:

            print("\n----------------------------------------")
            print(path.relative_to(ROOT))
            print(f"[ERRO AO LER] {exc}")


# ============================================================
# 5. DETALHAMENTO DA DATA/RAW
# ============================================================

print("\n" + "=" * 80)
print("5. DATA/RAW")
print("=" * 80)

raw_dir = ROOT / "data" / "raw"

if not raw_dir.exists():

    print("[ERRO] data/raw não existe.")

else:

    raw_csvs = sorted(
        raw_dir.glob("*.csv")
    )

    print(
        f"Arquivos CSV em data/raw: "
        f"{len(raw_csvs)}"
    )

    for path in raw_csvs:

        try:

            df = pd.read_csv(
                path,
                encoding="utf-8-sig"
            )

            print(
                f"[OK] {path.name:<30} "
                f"{len(df):>10,} linhas | "
                f"{len(df.columns):>2} colunas"
            )

        except Exception as exc:

            print(
                f"[ERRO] {path.name}: {exc}"
            )


# ============================================================
# 6. DUPLICIDADES BÁSICAS
# ============================================================

print("\n" + "=" * 80)
print("6. DUPLICIDADES BÁSICAS")
print("=" * 80)

checks = {
    "clientes.csv": "cliente_id",
    "lojas.csv": "loja_id",
    "produtos.csv": "produto_id",
    "pedidos.csv": "pedido_id",
    "itens_pedido.csv": "item_id",
}

for filename, key in checks.items():

    path = raw_dir / filename

    if not path.exists():
        print(
            f"[AUSENTE] {filename}"
        )
        continue

    try:

        df = pd.read_csv(
            path,
            encoding="utf-8-sig"
        )

        if key not in df.columns:

            print(
                f"[ERRO] {filename}: "
                f"coluna {key} não encontrada."
            )

            continue

        duplicated = df[key].duplicated().sum()

        print(
            f"{filename:<25} "
            f"duplicados em {key}: "
            f"{duplicated:,}"
        )

    except Exception as exc:

        print(
            f"[ERRO] {filename}: {exc}"
        )


# ============================================================
# 7. NULOS
# ============================================================

print("\n" + "=" * 80)
print("7. NULOS NAS PRINCIPAIS TABELAS")
print("=" * 80)

for filename in [
    "clientes.csv",
    "produtos.csv",
    "pedidos.csv",
    "itens_pedido.csv",
]:

    path = raw_dir / filename

    if not path.exists():
        continue

    try:

        df = pd.read_csv(
            path,
            encoding="utf-8-sig"
        )

        nulls = df.isna().sum()

        print(f"\n{filename}")

        for col, qty in nulls.items():

            if qty > 0:

                pct = qty / len(df) * 100

                print(
                    f"  {col}: "
                    f"{qty:,} "
                    f"({pct:.2f}%)"
                )

    except Exception as exc:

        print(
            f"[ERRO] {filename}: {exc}"
        )


# ============================================================
# 8. ITENS POR PEDIDO
# ============================================================

print("\n" + "=" * 80)
print("8. ITENS POR PEDIDO")
print("=" * 80)

itens_path = raw_dir / "itens_pedido.csv"

if itens_path.exists():

    try:

        itens = pd.read_csv(
            itens_path,
            encoding="utf-8-sig"
        )

        if {
            "pedido_id",
            "produto_id",
            "quantidade",
            "preco_unitario",
        }.issubset(itens.columns):

            pedidos_distintos = (
                itens["pedido_id"]
                .nunique()
            )

            media = (
                len(itens)
                / pedidos_distintos
                if pedidos_distintos
                else 0
            )

            print(
                f"Itens: {len(itens):,}"
            )

            print(
                f"Pedidos distintos: "
                f"{pedidos_distintos:,}"
            )

            print(
                f"Média itens/pedido: "
                f"{media:.2f}"
            )

            print("\nDistribuição:")

            dist = (
                itens.groupby("pedido_id")
                .size()
                .value_counts()
                .sort_index()
            )

            print(
                dist.to_string()
            )

    except Exception as exc:

        print(
            f"[ERRO] {exc}"
        )


# ============================================================
# 9. DATAS DE PEDIDOS
# ============================================================

print("\n" + "=" * 80)
print("9. DATAS DE PEDIDOS")
print("=" * 80)

pedidos_path = raw_dir / "pedidos.csv"

if pedidos_path.exists():

    try:

        pedidos = pd.read_csv(
            pedidos_path,
            encoding="utf-8-sig"
        )

        if "data_pedido" in pedidos.columns:

            datas = pd.to_datetime(
                pedidos["data_pedido"],
                errors="coerce"
            )

            invalidas = datas.isna().sum()

            print(
                f"Datas inválidas: "
                f"{invalidas:,}"
            )

            print(
                f"Menor data válida: "
                f"{datas.min()}"
            )

            print(
                f"Maior data válida: "
                f"{datas.max()}"
            )

            print("\nPedidos por ano:")

            print(
                datas.dt.year
                .value_counts()
                .sort_index()
                .to_string()
            )

    except Exception as exc:

        print(
            f"[ERRO] {exc}"
        )


# ============================================================
# 10. POSSÍVEIS ARQUIVOS/PASTAS DUPLICADOS
# ============================================================

print("\n" + "=" * 80)
print("10. POSSÍVEIS DUPLICAÇÕES DE ESTRUTURA")
print("=" * 80)

duplicated_names = [
    "CasaNova-Data-Analytics",
    "generation",
    "python",
]

for name in duplicated_names:

    matches = [
        p
        for p in ROOT.rglob(name)
        if p != ROOT
    ]

    if matches:

        print(f"\n{name} encontrado em:")

        for match in matches:

            print(
                f"  {match.relative_to(ROOT)}"
            )


# ============================================================
# 11. GIT
# ============================================================

print("\n" + "=" * 80)
print("11. GIT")
print("=" * 80)

git_dir = ROOT / ".git"

if git_dir.exists():

    print("[OK] Repositório Git inicializado.")

    head = git_dir / "HEAD"

    if head.exists():

        print(
            "HEAD:",
            head.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()
        )

else:

    print(
        "[AVISO] Git ainda não foi inicializado."
    )


# ============================================================
# 12. ARQUIVOS IMPORTANTES
# ============================================================

print("\n" + "=" * 80)
print("12. ARQUIVOS IMPORTANTES")
print("=" * 80)

important = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "ROADMAP.md",
    "verify_phase3.py",
]

for filename in important:

    path = ROOT / filename

    if path.exists():

        print(
            f"[OK] {filename} "
            f"({path.stat().st_size:,} bytes)"
        )

    else:

        print(
            f"[AUSENTE] {filename}"
        )


# ============================================================
# 13. RESUMO
# ============================================================

print("\n" + "=" * 80)
print("13. RESUMO")
print("=" * 80)

print(
    f"Total de arquivos Python : {len(py_files)}"
)

print(
    f"Total de documentos      : {len(docs_files)}"
)

print(
    f"Total de CSVs            : {len(csv_files)}"
)

print(
    f"CSV em data/raw          : "
    f"{len(list(raw_dir.glob('*.csv'))) if raw_dir.exists() else 0}"
)

print()
print(
    "IMPORTANTE: este script é SOMENTE diagnóstico."
)

print(
    "Nenhum arquivo foi criado, alterado, "
    "apagado ou sobrescrito."
)

print("=" * 80)
print("FIM DA INSPEÇÃO")
print("=" * 80)