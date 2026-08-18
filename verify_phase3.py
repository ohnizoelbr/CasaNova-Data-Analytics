from pathlib import Path
import sys
import pandas as pd


# ============================================================
# CASA NOVA DATA ANALYTICS
# VALIDADOR COMPLETO — FASE 2 + FASE 3
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent


# ============================================================
# LOCALIZAR RAIZ DO PROJETO
# ============================================================

def find_project_root(start: Path) -> Path:
    """
    Procura uma pasta contendo:
        data/raw
        docs
        python
    """

    current = start

    for _ in range(6):
        if (
            (current / "data" / "raw").exists()
            and (current / "docs").exists()
            and (current / "python").exists()
        ):
            return current

        current = current.parent

    raise RuntimeError(
        "Não foi possível localizar a raiz do projeto."
    )


BASE_DIR = find_project_root(SCRIPT_DIR)

RAW_DIR = BASE_DIR / "data" / "raw"
DOCS_DIR = BASE_DIR / "docs"
BACKUP_DIR = BASE_DIR / "data" / "raw_backup_fase3"


# ============================================================
# CONFIGURAÇÕES ESPERADAS
# ============================================================

EXPECTED_FILES = {
    "clientes.csv": {
        "min_rows": 11_000,
        "expected_rows": 12_000,
        "columns": [
            "cliente_id",
            "nome",
            "cpf",
            "email",
            "telefone",
            "cidade",
            "estado",
            "data_cadastro",
        ],
    },
    "lojas.csv": {
        "min_rows": 7,
        "expected_rows": 7,
        "columns": [
            "loja_id",
            "nome_loja",
            "cidade",
            "estado",
            "tipo_canal",
            "data_abertura",
        ],
    },
    "produtos.csv": {
        "min_rows": 140,
        "expected_rows": 150,
        "columns": [
            "produto_id",
            "nome_produto",
            "categoria",
            "preco_tabela",
            "custo",
            "ativo",
        ],
    },
    "pedidos.csv": {
        "min_rows": 40_000,
        "expected_rows": 45_450,
        "columns": [
            "pedido_id",
            "cliente_id",
            "loja_id",
            "canal",
            "data_pedido",
            "status",
        ],
    },
    "itens_pedido.csv": {
        "min_rows": 75_000,
        "expected_rows": 80_000,
        "columns": [
            "item_id",
            "pedido_id",
            "produto_id",
            "quantidade",
            "preco_unitario",
            "desconto",
        ],
    },
    "estoque.csv": {
        "min_rows": 1,
        "expected_rows": None,
        "columns": [
            "produto_id",
            "loja_id",
            "data_snapshot",
            "quantidade_disponivel",
        ],
    },
    "funil_ecommerce.csv": {
        "min_rows": 1,
        "expected_rows": None,
        "columns": [
            "data",
            "categoria",
            "dispositivo",
            "visualizacoes",
            "add_carrinho",
            "checkout_iniciado",
            "compra_concluida",
        ],
    },
    "concorrencia_precos.csv": {
        "min_rows": 1,
        "expected_rows": None,
        "columns": [
            "produto_id",
            "mes_referencia",
            "preco_casanova",
            "preco_medio_mercado",
        ],
    },
}


# ============================================================
# CONTADORES
# ============================================================

errors = []
warnings = []
oks = []


# ============================================================
# FUNÇÕES
# ============================================================

def header(text: str):
    print()
    print("=" * 75)
    print(text)
    print("=" * 75)


def ok(message: str):
    oks.append(message)
    print(f"[OK] {message}")


def warning(message: str):
    warnings.append(message)
    print(f"[AVISO] {message}")


def error(message: str):
    errors.append(message)
    print(f"[ERRO] {message}")


def detect_delimiter(path: Path):
    """
    Tenta identificar o delimitador.
    """

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        errors="replace",
    ) as file:

        first_line = file.readline()

    candidates = {
        ",": first_line.count(","),
        ";": first_line.count(";"),
        "\t": first_line.count("\t"),
        "|": first_line.count("|"),
    }

    delimiter = max(
        candidates,
        key=candidates.get,
    )

    if candidates[delimiter] == 0:
        return ","

    return delimiter


def load_csv(path: Path):
    delimiter = detect_delimiter(path)

    try:
        df = pd.read_csv(
            path,
            sep=delimiter,
            encoding="utf-8-sig",
        )

        return df, delimiter

    except Exception as exc:

        error(
            f"Falha ao ler {path.name}: {exc}"
        )

        return None, delimiter


def normalize_columns(columns):
    return [
        str(col)
        .strip()
        .lower()
        for col in columns
    ]


def is_excel_pivot(df: pd.DataFrame):
    """
    Identifica o padrão que apareceu nos arquivos alterados:
        Rótulos de Linha;Contagem de ...
    """

    if len(df.columns) != 1:
        return False

    column = str(df.columns[0]).lower()

    suspicious = [
        "rótulos de linha",
        "rotulos de linha",
        "contagem de",
        "soma de",
    ]

    return any(
        item in column
        for item in suspicious
    )


def show_dataframe_preview(df):
    print("Primeiras linhas:")

    print(
        df.head(3).to_string(
            index=False
        )
    )


# ============================================================
# INÍCIO
# ============================================================

header(
    "CASANOVA DATA ANALYTICS — VALIDAÇÃO FASE 2 + FASE 3"
)

print(f"Projeto : {BASE_DIR}")
print(f"Raw     : {RAW_DIR}")
print(f"Docs    : {DOCS_DIR}")
print(f"Backup  : {BACKUP_DIR}")


# ============================================================
# 1. ESTRUTURA
# ============================================================

header("1. ESTRUTURA DO PROJETO")

for directory in [
    RAW_DIR,
    DOCS_DIR,
    BASE_DIR / "python",
    BASE_DIR / "sql",
]:
    if directory.exists():
        ok(
            f"Pasta encontrada: "
            f"{directory.relative_to(BASE_DIR)}"
        )
    else:
        error(
            f"Pasta não encontrada: "
            f"{directory}"
        )


# ============================================================
# 2. ARQUIVOS RAW
# ============================================================

header("2. VERIFICAÇÃO DOS 8 ARQUIVOS RAW")

dataframes = {}


for filename, config in EXPECTED_FILES.items():

    path = RAW_DIR / filename

    print()
    print(f"--- {filename} ---")

    if not path.exists():

        error(
            f"{filename} não existe."
        )

        continue

    ok(
        f"{filename} encontrado "
        f"({path.stat().st_size:,} bytes)"
    )

    df, delimiter = load_csv(path)

    if df is None:
        continue

    dataframes[filename] = df

    print(
        f"Delimitador detectado: "
        f"{repr(delimiter)}"
    )

    print(
        f"Linhas: {len(df):,}"
    )

    print(
        f"Colunas: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # DETECTAR TABELA DINÂMICA
    # --------------------------------------------------------

    if is_excel_pivot(df):

        error(
            f"{filename} parece ter sido sobrescrito "
            f"por uma tabela dinâmica do Excel."
        )

        print(
            f"Coluna encontrada: "
            f"{df.columns[0]}"
        )

        continue

    # --------------------------------------------------------
    # LINHAS
    # --------------------------------------------------------

    min_rows = config["min_rows"]

    if len(df) < min_rows:

        error(
            f"{filename} possui apenas "
            f"{len(df):,} linhas. "
            f"Esperado pelo menos {min_rows:,}."
        )

    else:

        ok(
            f"{filename} possui volume suficiente: "
            f"{len(df):,} linhas."
        )

    # --------------------------------------------------------
    # VOLUME ESPERADO
    # --------------------------------------------------------

    expected_rows = config["expected_rows"]

    if expected_rows is not None:

        if len(df) == expected_rows:

            ok(
                f"{filename}: volume exato "
                f"esperado ({expected_rows:,})."
            )

        else:

            warning(
                f"{filename}: {len(df):,} linhas. "
                f"Referência esperada: "
                f"{expected_rows:,}."
            )

    # --------------------------------------------------------
    # COLUNAS
    # --------------------------------------------------------

    actual_columns = normalize_columns(
        df.columns
    )

    expected_columns = normalize_columns(
        config["columns"]
    )

    missing_columns = [
        col
        for col in expected_columns
        if col not in actual_columns
    ]

    if missing_columns:

        error(
            f"{filename}: colunas faltando: "
            f"{missing_columns}"
        )

    else:

        ok(
            f"{filename}: estrutura de colunas OK."
        )

    show_dataframe_preview(df)


# ============================================================
# 3. STATUS INDIVIDUAL
# ============================================================

header("3. SITUAÇÃO DE CADA ARQUIVO")

for filename in EXPECTED_FILES:

    df = dataframes.get(filename)

    if df is None:

        error(
            f"{filename}: NÃO ESTÁ APTO PARA ANÁLISE."
        )

    elif is_excel_pivot(df):

        error(
            f"{filename}: TABELA DINÂMICA DETECTADA."
        )

    else:

        ok(
            f"{filename}: disponível para análise."
        )


# ============================================================
# 4. FASE 3 — CIDADE
# ============================================================

header("4. FASE 3 — ANÁLISE DE CIDADE")

clientes = dataframes.get(
    "clientes.csv"
)

if clientes is not None:

    columns = normalize_columns(
        clientes.columns
    )

    if "cidade" in columns:

        cidade_col = clientes.columns[
            columns.index("cidade")
        ]

        cidades = (
            clientes[cidade_col]
            .dropna()
            .astype(str)
            .str.strip()
        )

        print(
            f"Valores distintos: "
            f"{cidades.nunique()}"
        )

        print("\nTop cidades:")

        print(
            cidades.value_counts()
            .head(15)
            .to_string()
        )

        ok(
            "Análise de cidade disponível."
        )

    else:

        error(
            "clientes.csv não possui coluna cidade."
        )

else:

    error(
        "Não foi possível analisar cidade "
        "porque clientes.csv está inválido."
    )


# ============================================================
# 5. FASE 3 — CATEGORIA
# ============================================================

header("5. FASE 3 — ANÁLISE DE CATEGORIA")

produtos = dataframes.get(
    "produtos.csv"
)

if produtos is not None:

    columns = normalize_columns(
        produtos.columns
    )

    if "categoria" in columns:

        categoria_col = produtos.columns[
            columns.index("categoria")
        ]

        categorias = (
            produtos[categoria_col]
            .dropna()
            .astype(str)
            .str.strip()
        )

        print(
            f"Valores distintos: "
            f"{categorias.nunique()}"
        )

        print("\nCategorias:")

        print(
            categorias.value_counts()
            .to_string()
        )

        ok(
            "Análise de categoria disponível."
        )

    else:

        error(
            "produtos.csv não possui coluna categoria."
        )

else:

    error(
        "Não foi possível analisar categoria "
        "porque produtos.csv está inválido."
    )


# ============================================================
# 6. FASE 3 — PEDIDOS POR MÊS
# ============================================================

header("6. FASE 3 — PEDIDOS POR MÊS")

pedidos = dataframes.get(
    "pedidos.csv"
)

if pedidos is not None:

    columns = normalize_columns(
        pedidos.columns
    )

    required = [
        "pedido_id",
        "data_pedido",
    ]

    missing = [
        col
        for col in required
        if col not in columns
    ]

    if missing:

        error(
            "pedidos.csv não permite análise mensal. "
            f"Faltando: {missing}"
        )

    else:

        pedido_id_col = pedidos.columns[
            columns.index("pedido_id")
        ]

        data_pedido_col = pedidos.columns[
            columns.index("data_pedido")
        ]

        temp = pedidos.copy()

        temp[data_pedido_col] = pd.to_datetime(
            temp[data_pedido_col],
            errors="coerce",
        )

        invalid_dates = (
            temp[data_pedido_col]
            .isna()
            .sum()
        )

        print(
            f"Datas inválidas: "
            f"{invalid_dates:,}"
        )

        valid = temp.dropna(
            subset=[data_pedido_col]
        ).copy()

        valid["mes"] = (
            valid[data_pedido_col]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            valid
            .groupby("mes")[pedido_id_col]
            .nunique()
        )

        print("\nPedidos por mês:")

        print(
            monthly.to_string()
        )

        ok(
            "Pedidos por mês calculados."
        )

else:

    error(
        "pedidos.csv inválido."
    )


# ============================================================
# 7. FASE 3 — RECEITA POR LOJA
# ============================================================

header("7. FASE 3 — RECEITA BRUTA APROXIMADA POR LOJA")

itens = dataframes.get(
    "itens_pedido.csv"
)

if pedidos is not None and itens is not None:

    pedidos_cols = normalize_columns(
        pedidos.columns
    )

    itens_cols = normalize_columns(
        itens.columns
    )

    required_pedidos = [
        "pedido_id",
        "loja_id",
    ]

    required_itens = [
        "pedido_id",
        "quantidade",
        "preco_unitario",
    ]

    missing_pedidos = [
        col
        for col in required_pedidos
        if col not in pedidos_cols
    ]

    missing_itens = [
        col
        for col in required_itens
        if col not in itens_cols
    ]

    if missing_pedidos:

        error(
            "Não é possível calcular receita por loja. "
            f"Faltando em pedidos.csv: {missing_pedidos}"
        )

    elif missing_itens:

        error(
            "Não é possível calcular receita por loja. "
            f"Faltando em itens_pedido.csv: {missing_itens}"
        )

    else:

        pedido_id_pedidos = pedidos.columns[
            pedidos_cols.index("pedido_id")
        ]

        loja_id_col = pedidos.columns[
            pedidos_cols.index("loja_id")
        ]

        pedido_id_itens = itens.columns[
            itens_cols.index("pedido_id")
        ]

        quantidade_col = itens.columns[
            itens_cols.index("quantidade")
        ]

        preco_col = itens.columns[
            itens_cols.index("preco_unitario")
        ]

        calc = itens.copy()

        calc[quantidade_col] = pd.to_numeric(
            calc[quantidade_col],
            errors="coerce",
        )

        calc[preco_col] = pd.to_numeric(
            calc[preco_col],
            errors="coerce",
        )

        calc["receita_bruta"] = (
            calc[quantidade_col]
            * calc[preco_col]
        )

        mapa = pedidos[
            [
                pedido_id_pedidos,
                loja_id_col,
            ]
        ].copy()

        merged = calc.merge(
            mapa,
            left_on=pedido_id_itens,
            right_on=pedido_id_pedidos,
            how="left",
        )

        receita = (
            merged
            .groupby(loja_id_col)["receita_bruta"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        print(
            receita.to_string(
                float_format=lambda x:
                f"R$ {x:,.2f}"
            )
        )

        print(
            f"\nReceita total aproximada: "
            f"R$ {receita.sum():,.2f}"
        )

        ok(
            "Receita bruta aproximada por loja calculada."
        )

else:

    error(
        "Não foi possível calcular receita."
    )


# ============================================================
# 8. BACKUP
# ============================================================

header("8. BACKUP")

if BACKUP_DIR.exists():

    backup_files = list(
        BACKUP_DIR.glob("*.csv")
    )

    print(
        f"Arquivos CSV no backup: "
        f"{len(backup_files)}"
    )

    if len(backup_files) >= 8:

        ok(
            "Backup dos 8 CSVs encontrado."
        )

    else:

        warning(
            "Backup existe, mas não contém 8 CSVs."
        )

else:

    warning(
        "Pasta de backup não encontrada."
    )


# ============================================================
# 9. DOCUMENTAÇÃO
# ============================================================

header("9. DOCUMENTAÇÃO DA FASE 3")

fase3_doc = DOCS_DIR / "fase_3_excel.md"

if fase3_doc.exists():

    ok(
        "docs/fase_3_excel.md encontrado."
    )

else:

    warning(
        "docs/fase_3_excel.md ainda não existe."
    )


# ============================================================
# 10. RESULTADO FINAL
# ============================================================

header("10. RESULTADO FINAL")

print(
    f"OK       : {len(oks)}"
)

print(
    f"AVISOS   : {len(warnings)}"
)

print(
    f"ERROS    : {len(errors)}"
)

print()

if errors:

    print(
        "🔴 FASE 3 NÃO ESTÁ APROVADA."
    )

    print(
        "\nPrincipais problemas:"
    )

    for item in errors:
        print(f"- {item}")

    print(
        "\nNão avance para a Fase 4 ainda."
    )

elif warnings:

    print(
        "🟡 FASE 3 TEM AVISOS."
    )

    print(
        "Revise os avisos antes de avançar."
    )

else:

    print(
        "🟢 FASE 3 APROVADA."
    )

    print(
        "Pode avançar para a Fase 4."
    )

print()
print("=" * 75)
print("FIM DA VALIDAÇÃO")
print("=" * 75)