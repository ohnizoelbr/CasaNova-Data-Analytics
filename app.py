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
    base_dir / "sql_views",
    base_dir / "reports" / "sql_views",
    base_dir / "CasaNova-Data-Analytics" / "reports" / "sql_views",
    base_dir.parent / "reports" / "sql_views",
]

views_dir = next((p for p in possible_paths if p.exists()), None)

if views_dir is None:
    found = list(base_dir.rglob("sql_views"))
    if found:
        views_dir = found[0]

@st.cache_data
def load_data(filename):
    if views_dir is None:
        return pd.DataFrame()
        
    path = views_dir / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

df_receita = load_data("vw_receita_mensal.csv")
df_produtos = load_data("vw_performance_produto.csv")
df_rfm = load_data("vw_rfm_clientes.csv")
df_funil = load_data("vw_funil_ecommerce.csv")
df_comp = load_data("vw_competitividade.csv")

# -----------------------------------------------------------------------------
# Barra Lateral - Filtros Globais
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏠 Filtros de Análise")
    st.markdown("---")

    if not df_receita.empty and "ano_mes" in df_receita.columns:
        df_receita = df_receita.sort_values("ano_mes")
        periodos = df_receita["ano_mes"].unique().tolist()
        
        if len(periodos) > 1:
            periodo_selecionado = st.select_slider(
                "🗓️ Selecione o Intervalo de Tempo:",
                options=periodos,
                value=(periodos[0], periodos[-1])
            )
            inicio, fim = periodo_selecionado
            df_receita_filtered = df_receita[
                (df_receita["ano_mes"] >= inicio) & (df_receita["ano_mes"] <= fim)
            ]
        else:
            df_receita_filtered = df_receita.copy()
    else:
        df_receita_filtered = df_receita.copy()

    if not df_produtos.empty and "categoria" in df_produtos.columns:
        categorias_disponiveis = ["Todas"] + sorted(df_produtos["categoria"].dropna().unique().tolist())
        categoria_filtro = st.selectbox("🏷️ Filtrar por Categoria:", categorias_disponiveis)
    else:
        categoria_filtro = "Todas"

    st.markdown("---")
    st.caption("CasaNova Analytics v2.0 | Atualizado em Real-Time")

# -----------------------------------------------------------------------------
# Cabeçalho Principal
# -----------------------------------------------------------------------------
st.markdown("""
    <div style="background-color:#1E40AF;padding:20px;border-radius:10px;margin-bottom:20px">
    <h1 style="color:white;text-align:center;margin:0;font-size:2.5rem;">🏠 CasaNova Analytics — Painel de Desempenho</h1>
    <p style="color:#E0E7FF;text-align:center;margin-top:10px;font-size:1.1rem;">Visão executiva integrada de vendas, catálogo, funil de conversão e segmentação de clientes.</p>
    </div>
    """, unsafe_allow_html=True)

if views_dir is None:
    st.warning("⚠️ **Aviso:** A pasta `sql_views` não foi encontrada. Certifique-se de que os arquivos de dados estão na estrutura correta.")

# -----------------------------------------------------------------------------
# Métricas e KPIs
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

if not df_receita_filtered.empty:
    receita_total = df_receita_filtered["receita_total"].sum()
    pedidos_totais = df_receita_filtered["total_pedidos"].sum()
    ticket_medio_geral = receita_total / pedidos_totais if pedidos_totais > 0 else 0
    total_clientes = len(df_rfm) if not df_rfm.empty else 0

    delta_rec, delta_ped = None, None
    if len(df_receita_filtered) >= 2:
        ult_mes_rec = df_receita_filtered["receita_total"].iloc[-1]
        penult_mes_rec = df_receita_filtered["receita_total"].iloc[-2]
        delta_rec = ((ult_mes_rec - penult_mes_rec) / penult_mes_rec) * 100 if penult_mes_rec > 0 else 0

        ult_mes_ped = df_receita_filtered["total_pedidos"].iloc[-1]
        penult_mes_ped = df_receita_filtered["total_pedidos"].iloc[-2]
        delta_ped = ((ult_mes_ped - penult_mes_ped) / penult_mes_ped) * 100 if penult_mes_ped > 0 else 0

    col1.metric("Receita Total", formata_brl(receita_total), delta=f"{delta_rec:+.1f}% no último mês" if delta_rec is not None else None)
    col2.metric("Total de Pedidos", f"{pedidos_totais:,}".replace(",", "."), delta=f"{delta_ped:+.1f}% no último mês" if delta_ped is not None else None)
    col3.metric("Ticket Médio Geral", formata_brl(ticket_medio_geral))
    col4.metric("Base de Clientes (RFM)", f"{total_clientes:,}".replace(",", "."))
else:
    col1.metric("Receita Total", "R$ 0,00")
    col2.metric("Total de Pedidos", "0")
    col3.metric("Ticket Médio Geral", "R$ 0,00")
    col4.metric("Base de Clientes", "0")

st.divider()

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

with tab1:
    st.subheader("Evolução Mensal da Receita")
    if not df_receita_filtered.empty:
        fig_rec = px.line(
            df_receita_filtered, 
            x="ano_mes", 
            y="receita_total", 
            markers=True,
            title="Evolução do Faturamento no Período Selecionado",
            labels={"ano_mes": "Mês/Ano", "receita_total": "Receita (R$)"},
            template="plotly_white"
        )
        fig_rec.update_traces(line_color="#1E40AF", line_width=3, marker=dict(size=8))
        fig_rec.update_layout(hovermode="x unified")
        st.plotly_chart(fig_rec, width="stretch")
    else:
        st.info("Aguardando dados de receita para exibição.")

with tab2:
    st.subheader("Performance do Catálogo de Produtos")
    if not df_produtos.empty:
        df_prod_view = df_produtos.copy()
        if categoria_filtro != "Todas":
            df_prod_view = df_prod_view[df_prod_view["categoria"] == categoria_filtro]
            
        df_cat = df_prod_view.sort_values("receita_total", ascending=False).head(10)
        
        fig_prod = px.bar(
            df_cat, 
            x="receita_total", 
            y="nome_produto", 
            text_auto=".2s",
            orientation='h',
            color="receita_total",
            color_continuous_scale="Blues",
            title=f"Top 10 Produtos por Receita ({categoria_filtro})",
            labels={"nome_produto": "", "receita_total": "Receita (R$)"},
            template="plotly_white"
        )
        fig_prod.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_prod, width="stretch")
    else:
        st.info("Aguardando dados de produtos para exibição.")

with tab3:
    st.subheader("Desempenho do Funil de E-commerce")
    if not df_funil.empty:
        df_funil_view = df_funil.copy()
        if categoria_filtro != "Todas":
            df_funil_view = df_funil_view[df_funil_view["categoria"] == categoria_filtro]

        total_vis = df_funil_view["total_visualizacoes"].sum()
        total_chk = df_funil_view["total_checkouts"].sum()
        total_com = df_funil_view["total_compras"].sum()

        dados_funil = pd.DataFrame({
            "Etapa": ["Visualizações", "Checkouts", "Compras"],
            "Quantidade": [total_vis, total_chk, total_com]
        })

        fig_funil = px.funnel(
            dados_funil, 
            y="Etapa", 
            x="Quantidade",
            title=f"Taxa de Conversão - Categoria: {categoria_filtro}",
            template="plotly_white"
        )
        fig_funil.update_traces(marker=dict(color=["#93C5FD", "#3B82F6", "#1E40AF"]))
        st.plotly_chart(fig_funil, width="stretch")
        
        st.caption("Detalhamento por Categoria:")
        st.dataframe(df_funil_view, width="stretch")
    else:
        st.info("Aguardando dados de funil para exibição.")

with tab4:
    st.subheader("Matriz: Monetário x Recência (Clientes)")
    if not df_rfm.empty:
        fig_rfm = px.scatter(
            df_rfm, 
            x="recencia_dias", 
            y="monetario", 
            color="frequencia",
            size="monetario",
            hover_name="id_cliente" if "id_cliente" in df_rfm.columns else None,
            title="Matriz Recência vs Monetário (Bolhas maiores = Maior valor gasto)",
            labels={"recencia_dias": "Dias sem Comprar (Recência)", "monetario": "Valor Total Gasto (R$)", "frequencia": "Frequência"},
            template="plotly_white",
            color_continuous_scale="Viridis"
        )
        fig_rfm.update_xaxes(autorange="reversed")
        st.plotly_chart(fig_rfm, width="stretch")
    else:
        st.info("Aguardando dados de RFM para exibição.")

with tab5:
    st.subheader("Análise de Competitividade de Preços")
    if not df_comp.empty:
        if "diferenca_preco" in df_comp.columns and "nome_produto" in df_comp.columns:
            df_comp_sorted = df_comp.sort_values("diferenca_preco").head(15)
            
            fig_comp = px.bar(
                df_comp_sorted,
                x="nome_produto",
                y="diferenca_preco",
                title="Comparativo de Preço x Concorrência (Top 15 mais competitivos)",
                labels={"diferenca_preco": "Diferença R$ (Negativo = Nosso preço é menor)", "nome_produto": ""},
                color="diferenca_preco",
                color_continuous_scale="RdYlGn_r",
                template="plotly_white"
            )
            st.plotly_chart(fig_comp, width="stretch")
            
        st.caption("Base de Dados Completa de Competitividade:")
        st.dataframe(df_comp, width="stretch")
    else:
        st.info("Dados de competitividade não disponíveis.")