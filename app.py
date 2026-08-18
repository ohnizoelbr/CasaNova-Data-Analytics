import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CasaNova Analytics — Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Função Auxiliar de Formatação
# -----------------------------------------------------------------------------
def formata_brl(valor):
    """Formata valores numéricos para o padrão BRL (R$ 1.234,56)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------------------------------------------------------
# Carregamento Dinâmico de Dados
# -----------------------------------------------------------------------------
base_dir = Path(__file__).resolve().parent

possible_paths = [
    base_dir / "reports" / "sql_views",
    base_dir / "CasaNova-Data-Analytics" / "reports" / "sql_views",
    base_dir.parent / "reports" / "sql_views",
    base_dir.parent / "CasaNova-Data-Analytics" / "reports" / "sql_views",
]

views_dir = next((p for p in possible_paths if p.exists()), None)

if views_dir is None:
    found = list(base_dir.parent.rglob("sql_views"))
    if found:
        views_dir = found[0]

@st.cache_data
def load_data(filename):
    if views_dir is None:
        st.error("Pasta 'sql_views' não foi encontrada no projeto.")
        return pd.DataFrame()
        
    path = views_dir / filename
    if path.exists():
        return pd.read_csv(path)
    st.error(f"Arquivo não encontrado no caminho: {path}")
    return pd.DataFrame()

df_receita = load_data("vw_receita_mensal.csv")
df_produtos = load_data("vw_performance_produto.csv")
df_rfm = load_data("vw_rfm_clientes.csv")
df_funil = load_data("vw_funil_ecommerce.csv")
df_comp = load_data("vw_competitividade.csv")

# -----------------------------------------------------------------------------
# Barra Lateral - Filtros Globais
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/home.png", width=60)
st.sidebar.title("Filtros de Análise")

# Filtro de Período (Ano/Mês)
if not df_receita.empty and "ano_mes" in df_receita.columns:
    df_receita = df_receita.sort_values("ano_mes")
    periodos = df_receita["ano_mes"].unique().tolist()
    periodo_selecionado = st.sidebar.select_slider(
        "Selecione o Intervalo de Tempo:",
        options=periodos,
        value=(periodos[0], periodos[-1])
    )
    # Filtrar dataframe de receita pelo período
    inicio, fim = periodo_selecionado
    df_receita_filtered = df_receita[
        (df_receita["ano_mes"] >= inicio) & (df_receita["ano_mes"] <= fim)
    ]
else:
    df_receita_filtered = df_receita.copy()

# Filtro de Categoria
if not df_produtos.empty and "categoria" in df_produtos.columns:
    categorias_disponiveis = ["Todas"] + sorted(df_produtos["categoria"].dropna().unique().tolist())
    categoria_filtro = st.sidebar.selectbox("Filtrar por Categoria:", categorias_disponiveis)
else:
    categoria_filtro = "Todas"

st.sidebar.markdown("---")
st.sidebar.caption("CasaNova Analytics v2.0 | Atualizado em Real-Time")

# -----------------------------------------------------------------------------
# Cabeçalho Principal
# -----------------------------------------------------------------------------
st.title("🏠 CasaNova Analytics — Painel de Desempenho")
st.caption("Visão executiva integrada de vendas, catálogo, funil de conversão e segmentação de clientes.")
st.markdown("---")

# -----------------------------------------------------------------------------
# Métricas e KPIs com Indicador de Tendência (MoM)
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

if not df_receita_filtered.empty:
    receita_total = df_receita_filtered["receita_total"].sum()
    pedidos_totais = df_receita_filtered["total_pedidos"].sum()
    ticket_medio_geral = receita_total / pedidos_totais if pedidos_totais > 0 else 0
    total_clientes = len(df_rfm) if not df_rfm.empty else 0

    # Cálculo da variação em relação ao mês anterior (MoM) se houver dados suficientes
    if len(df_receita_filtered) >= 2:
        ult_mes_rec = df_receita_filtered["receita_total"].iloc[-1]
        penult_mes_rec = df_receita_filtered["receita_total"].iloc[-2]
        delta_rec = ((ult_mes_rec - penult_mes_rec) / penult_mes_rec) * 100 if penult_mes_rec > 0 else 0

        ult_mes_ped = df_receita_filtered["total_pedidos"].iloc[-1]
        penult_mes_ped = df_receita_filtered["total_pedidos"].iloc[-2]
        delta_ped = ((ult_mes_ped - penult_mes_ped) / penult_mes_ped) * 100 if penult_mes_ped > 0 else 0
    else:
        delta_rec = None
        delta_ped = None

    col1.metric(
        "Receita Total", 
        formata_brl(receita_total), 
        delta=f"{delta_rec:+.1f}% no último mês" if delta_rec is not None else None
    )
    col2.metric(
        "Total de Pedidos", 
        f"{pedidos_totais:,}".replace(",", "."), 
        delta=f"{delta_ped:+.1f}% no último mês" if delta_ped is not None else None
    )
    col3.metric("Ticket Médio Geral", formata_brl(ticket_medio_geral))
    col4.metric("Base de Clientes (RFM)", f"{total_clientes:,}".replace(",", "."))

st.markdown("---")

# -----------------------------------------------------------------------------
# Abas de Navegação
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Vendas & Receita", 
    "📦 Produtos & Categorias", 
    "🎯 Funil E-commerce", 
    "👥 Segmentação RFM",
    "⚔️ Competitividade"
])

# Tab 1: Evolução Temporal
with tab1:
    st.subheader("Evolução Mensal da Receita e Pedidos")
    if not df_receita_filtered.empty:
        fig_rec = px.line(
            df_receita_filtered, 
            x="ano_mes", 
            y="receita_total", 
            markers=True,
            title="Evolução do Faturamento no Período Selecionado",
            labels={"ano_mes": "Mês/Ano", "receita_total": "Receita (R$)"}
        )
        fig_rec.update_traces(line_color="#1f77b4", line_width=3)
        st.plotly_chart(fig_rec, width="stretch")

# Tab 2: Performance de Produtos
with tab2:
    st.subheader("Performance do Catálogo de Produtos")
    if not df_produtos.empty:
        df_prod_view = df_produtos.copy()
        if categoria_filtro != "Todas":
            df_prod_view = df_prod_view[df_prod_view["categoria"] == categoria_filtro]
            
        df_cat = df_prod_view.sort_values("receita_total", ascending=False)
        
        fig_prod = px.bar(
            df_cat.head(10), 
            x="nome_produto", 
            y="receita_total", 
            text_auto=".2s",
            color="receita_total",
            color_continuous_scale="Blues",
            title=f"Top 10 Produtos por Receita ({categoria_filtro})",
            labels={"nome_produto": "Produto", "receita_total": "Receita (R$)"}
        )
        st.plotly_chart(fig_prod, width="stretch")

# Tab 3: Funil de E-commerce
with tab3:
    st.subheader("Desempenho do Funil de E-commerce por Categoria")
    if not df_funil.empty:
        df_funil_view = df_funil.copy()
        if categoria_filtro != "Todas":
            df_funil_view = df_funil_view[df_funil_view["categoria"] == categoria_filtro]

        fig_funil = px.bar(
            df_funil_view, 
            x="categoria", 
            y=["total_visualizacoes", "total_checkouts", "total_compras"],
            barmode="group",
            title="Conversão por Etapas e Categorias",
            labels={"value": "Quantidade", "variable": "Etapa do Funil"}
        )
        st.plotly_chart(fig_funil, width="stretch")
        st.dataframe(df_funil_view, width="stretch")

# Tab 4: Segmentação RFM
with tab4:
    st.subheader("Distribuição do Monetário x Recência (Clientes)")
    if not df_rfm.empty:
        fig_rfm = px.scatter(
            df_rfm, 
            x="recencia_dias", 
            y="monetario", 
            color="frequencia",
            size="monetario",
            hover_name="id_cliente" if "id_cliente" in df_rfm.columns else None,
            title="Matriz Recência vs Monetário (Colorido por Frequência)",
            labels={"recencia_dias": "Dias sem Comprar", "monetario": "Valor Total Gasto (R$)"}
        )
        st.plotly_chart(fig_rfm, width="stretch")

# Tab 5: Competitividade
with tab5:
    st.subheader("Análise de Competitividade de Preços")
    if not df_comp.empty:
        st.dataframe(df_comp, width="stretch")
        if "diferenca_preco" in df_comp.columns and "nome_produto" in df_comp.columns:
            fig_comp = px.bar(
                df_comp.sort_values("diferenca_preco").head(15),
                x="nome_produto",
                y="diferenca_preco",
                title="Comparativo de Preço x Concorrência",
                labels={"diferenca_preco": "Diferença R$", "nome_produto": "Produto"}
            )
            st.plotly_chart(fig_comp, width="stretch")
    else:
        st.info("Dados de competitividade não disponíveis.")