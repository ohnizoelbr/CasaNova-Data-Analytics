"""
diagnostico_projeto.py

Raio-x do projeto inteiro até aqui: onde você está rodando o script, o que
já foi feito (Fases 0-2) e o que falta - antes de seguir pra Fase 4.

Uso:
    python diagnostico_projeto.py

Funciona de qualquer lugar dentro (ou perto) da pasta do projeto - o script
tenta localizar a raiz sozinho e avisa se você estiver no lugar errado
(esse foi exatamente o problema do KeyError: 'data_pedido' - rodar de uma
pasta que não é a raiz do projeto).
"""

import os

PASTAS_ESPERADAS = [
    "data/raw", "data/processed", "data/quality", "data/star_schema",
    "python/generation", "python/analysis", "python/data_quality",
    "python/etl", "python/sql_load",
    "sql/staging", "sql/dimensions", "sql/facts", "sql/analytics",
    "docs", "reports/images", "notebooks",
]

ARQUIVOS_FASE0_1 = [
    ".gitignore", "requirements.txt", "README.md",
    "docs/business_problem.md", "docs/business_rules.md",
    "docs/data_dictionary.md", "docs/data_model.md", "docs/data_quality.md",
    "docs/kpi_catalog.md", "docs/methodology.md", "docs/validation.md",
    "docs/phase_status.md",
]

COLUNAS_ESPERADAS = {
    "clientes.csv": ["cliente_id", "nome", "cpf", "email", "telefone", "cidade", "estado", "data_cadastro"],
    "lojas.csv": ["loja_id", "nome_loja", "cidade", "estado", "tipo_canal", "data_abertura"],
    "produtos.csv": ["produto_id", "nome_produto", "categoria", "preco_tabela", "custo", "ativo"],
    "pedidos.csv": ["pedido_id", "cliente_id", "loja_id", "canal", "data_pedido", "status"],
    "itens_pedido.csv": ["item_id", "pedido_id", "produto_id", "quantidade", "preco_unitario", "desconto"],
    "estoque.csv": ["produto_id", "loja_id", "data_snapshot", "quantidade_disponivel"],
    "funil_ecommerce.csv": ["data", "categoria", "dispositivo", "visualizacoes", "add_carrinho",
                             "checkout_iniciado", "compra_concluida"],
    "concorrencia_precos.csv": ["produto_id", "mes_referencia", "preco_casanova", "preco_medio_mercado"],
}


def parece_raiz_do_projeto(caminho):
    return os.path.isdir(os.path.join(caminho, "data")) and os.path.isdir(os.path.join(caminho, "python"))


def _completude(caminho):
    """Conta quantos dos itens esperados da Fase 0-1 existem em 'caminho'.
    Serve pra comparar duas pastas candidatas e decidir qual delas é a raiz
    de verdade - uma checagem binária (\"tem data/ e python/\") não pega o
    caso em que a pasta de fora TAMBÉM tem essas duas pastas, só que vazias
    ou incompletas."""
    pastas_ok = sum(1 for p in PASTAS_ESPERADAS if os.path.isdir(os.path.join(caminho, p)))
    arquivos_ok = sum(1 for a in ARQUIVOS_FASE0_1 if os.path.isfile(os.path.join(caminho, a)))
    return pastas_ok + arquivos_ok


def localizar_raiz():
    """Tenta achar a raiz do projeto a partir do diretório atual. Cobre o caso
    mais comum de confusão: uma pasta com o mesmo nome dentro dela mesma,
    inclusive quando a pasta de fora também parece (superficialmente) uma
    raiz válida."""
    atual = os.getcwd()
    nome_atual = os.path.basename(atual.rstrip(os.sep))
    candidata_aninhada = os.path.join(atual, nome_atual)

    pontos_atual = _completude(atual)
    pontos_aninhada = _completude(candidata_aninhada) if os.path.isdir(candidata_aninhada) else -1

    if pontos_aninhada > pontos_atual:
        total = len(PASTAS_ESPERADAS) + len(ARQUIVOS_FASE0_1)
        return candidata_aninhada, (
            f"Você rodou este script de:\n  {atual}\n"
            f"e encontrei uma pasta com o MESMO NOME dentro dela, com uma estrutura "
            f"de projeto mais completa:\n  {candidata_aninhada}\n"
            f"({pontos_aninhada} de {total} itens esperados ali, contra {pontos_atual} "
            f"na pasta atual)\n"
            f"Rode: cd \"{nome_atual}\"\ne depois rode este script de novo."
        )

    if parece_raiz_do_projeto(atual):
        return atual, None

    try:
        subpastas_validas = [
            item for item in sorted(os.listdir(atual))
            if os.path.isdir(os.path.join(atual, item)) and parece_raiz_do_projeto(os.path.join(atual, item))
        ]
    except PermissionError:
        subpastas_validas = []

    if subpastas_validas:
        sub = subpastas_validas[0]
        caminho_sub = os.path.join(atual, sub)
        return caminho_sub, (
            f"Você rodou este script de:\n  {atual}\n"
            f"que não parece a raiz do projeto (não tem 'data/' nem 'python/' aqui).\n"
            f"Encontrei a estrutura certa em:\n  {caminho_sub}\n"
            f"Rode: cd \"{sub}\"\ne depois rode este script de novo."
        )

    return None, (
        f"Não encontrei uma pasta com a estrutura do projeto ('data/' e 'python/') "
        f"em:\n  {atual}\nnem em nenhuma subpasta direta dela.\n"
        f"Navegue (cd) até a pasta correta do projeto e rode de novo."
    )


def secao(titulo):
    print(f"\n{'=' * 62}\n{titulo}\n{'=' * 62}")


def checar_fase01(raiz):
    secao("FASE 0-1: estrutura de pastas e documentação")
    faltando_pastas = [p for p in PASTAS_ESPERADAS if not os.path.isdir(os.path.join(raiz, p))]
    faltando_arquivos = [a for a in ARQUIVOS_FASE0_1 if not os.path.isfile(os.path.join(raiz, a))]
    if not faltando_pastas and not faltando_arquivos:
        print(f"OK - {len(PASTAS_ESPERADAS)} pastas e {len(ARQUIVOS_FASE0_1)} arquivos presentes.")
    else:
        if faltando_pastas:
            print(f"Faltando {len(faltando_pastas)} pasta(s): {faltando_pastas}")
        if faltando_arquivos:
            print(f"Faltando {len(faltando_arquivos)} arquivo(s): {faltando_arquivos}")
        print("-> Rode setup_project.py a partir desta pasta.")


def checar_fase2(raiz):
    secao("FASE 2: dados brutos (data/raw/)")
    raw_dir = os.path.join(raiz, "data", "raw")
    faltando = [c for c in COLUNAS_ESPERADAS if not os.path.isfile(os.path.join(raw_dir, c))]
    if faltando:
        print(f"Faltando {len(faltando)} arquivo(s) em data/raw/: {faltando}")
        print("-> Rode python/generation/generate_raw_data.py a partir desta pasta.")
        return

    try:
        import pandas as pd
    except ImportError:
        print("pandas não está instalado neste ambiente - não dá pra conferir "
              "linhas/colunas. Rode: pip install -r requirements.txt")
        return

    tudo_ok = True
    for nome, colunas_esperadas in COLUNAS_ESPERADAS.items():
        caminho = os.path.join(raw_dir, nome)
        try:
            df = pd.read_csv(caminho)
        except Exception as e:
            print(f"  {nome}: ERRO ao ler ({e})")
            tudo_ok = False
            continue
        faltando_cols = [c for c in colunas_esperadas if c not in df.columns]
        if faltando_cols:
            tudo_ok = False
            print(f"  {nome}: colunas faltando {faltando_cols}")
            print(f"    colunas encontradas: {list(df.columns)}")
            print(f"    -> Esse arquivo provavelmente NÃO é o gerado pelo "
                  f"generate_raw_data.py (pode ter sido sobrescrito ao abrir/salvar "
                  f"no Excel, ou é de outra pasta). Rode generate_raw_data.py de novo.")
        else:
            print(f"  {nome}: OK ({len(df):,} linhas, colunas corretas)")

    print("\nFase 2 parece completa e correta." if tudo_ok else
          "\nFase 2 tem pendência(s) acima - resolva antes da Fase 4.")


def checar_fase4(raiz):
    secao("FASE 4: EDA (prévia - ainda não é obrigatória)")
    images_dir = os.path.join(raiz, "reports", "images")
    if os.path.isdir(images_dir) and any(f.endswith(".png") for f in os.listdir(images_dir)):
        print("Já existem gráficos em reports/images/ - eda.py já rodou pelo menos uma vez.")
    else:
        print("Ainda não rodou eda.py - é o próximo passo depois deste diagnóstico.")


def main():
    print(f"Diretório atual: {os.getcwd()}")
    raiz, aviso = localizar_raiz()

    if aviso:
        secao("ATENÇÃO - possível problema de pasta")
        print(aviso)

    if raiz is None:
        print("\nNão dá pra continuar o diagnóstico sem localizar a raiz do projeto.")
        return

    if raiz != os.getcwd():
        print(f"\n(Rodando o restante do diagnóstico contra: {raiz})")

    checar_fase01(raiz)
    checar_fase2(raiz)
    checar_fase4(raiz)

    secao("RESUMO")
    print("Se tudo acima apareceu como OK, pode seguir pra Fase 4 (eda.py).")
    print("Se algo apareceu como falha/erro, resolve aquele item primeiro e rode este diagnóstico de novo.")


if __name__ == "__main__":
    main()