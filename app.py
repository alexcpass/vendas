import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard Comercial Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILIZAÇÃO CSS PROFISSIONAL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Configuração Global */
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0f2f6; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Cards (Container Branco) */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #e1e4e8;
    }
    
    /* Métricas */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1f2937;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #111827;
        font-weight: 700;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #6b7280;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# FUNÇÃO DE PROCESSAMENTO (ATUALIZADA PARA 5 ARQUIVOS)
@st.cache_data
def process_data(vendas_file, clientes_file, produtos_file, vendedores_file, metas_file):
    try:
        # Carregamento
        vendas = pd.read_csv(vendas_file)
        clientes = pd.read_csv(clientes_file)
        produtos = pd.read_csv(produtos_file)
        # Arquivos extras (carregados para cumprir requisito, merge opcional)
        vendedores = pd.read_csv(vendedores_file)
        metas = pd.read_csv(metas_file)

        # Merges principais
        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')
        
        # Tenta merge com vendedores se a coluna existir (Opcional)
        if 'VendedorID' in df.columns and 'VendedorID' in vendedores.columns:
            df = df.merge(vendedores, on='VendedorID', how='left')

        # Tratamento de Valor Monetário (Híbrido BR/US)
        if df['ValorTotal'].dtype == 'object':
            df['ValorTotal'] = (
                df['ValorTotal'].astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False) # Remove separador de milhar BR
                .str.replace(',', '.', regex=False) # Troca vírgula decimal por ponto
                .astype(float)
            )

        # Tratamento de Datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['DataVenda']) # Remove datas inválidas
        
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df['MesNome'] = df['Mes'].apply(lambda x: meses_ordem[x-1])

        return df, None
    except Exception as e:
        return None, str(e)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/11523/11523992.png", width=60)
    st.title("Comercial Analytics")
    st.caption("v.3.1 | Enterprise Edition")
    st.markdown("---")
    
    st.subheader("📤 Upload de Dados")
    with st.expander("Carregar Arquivos CSV", expanded=True):
        vendas_file = st.file_uploader("1. Vendas", type=['csv'])
        clientes_file = st.file_uploader("2. Clientes", type=['csv'])
        produtos_file = st.file_uploader("3. Produtos", type=['csv'])
        vendedores_file = st.file_uploader("4. Vendedores", type=['csv'])
        metas_file = st.file_uploader("5. Metas", type=['csv'])

    arquivos = [vendas_file, clientes_file, produtos_file, vendedores_file, metas_file]
    arquivos_ok = all(arquivos)
    
    if arquivos_ok:
        st.success("Sistema Pronto", icon="✅")
    else:
        restantes = 5 - sum(bool(a) for a in arquivos)
        st.warning(f"Aguardando {restantes} arquivos", icon="⚠️")

# TELA INICIAL (SEM DADOS)
if not arquivos_ok:
    st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <h2>👋 Bem-vindo ao Dashboard Comercial</h2>
            <p style='color: #6b7280;'>Faça o upload dos 5 arquivos CSV obrigatórios na barra lateral para liberar a visualização.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# PROCESSAMENTO
with st.spinner('Consolidando bases de dados...'):
    df, erro = process_data(vendas_file, clientes_file, produtos_file, vendedores_file, metas_file)

if erro:
    st.error(f"Erro crítico ao processar dados: {erro}")
    st.stop()

# --- LÓGICA DO DASHBOARD ---
if df is not None:
    
    # FILTROS LATERAIS
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔍 Filtros Globais")
        
        # Filtro de Ano (Requisitado)
        anos_disponiveis = sorted(df['Ano'].unique().tolist())
        ano_sel = st.selectbox("Selecione o Ano", anos_disponiveis, index=len(anos_disponiveis)-1)
        
        # Filtros Secundários
        categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
        cat_sel = st.selectbox("Categoria", categorias)
        
        formas = ['Todas'] + sorted(df['FormaPagamento'].unique().tolist())
        forma_sel = st.selectbox("Forma de Pagamento", formas)

    # APLICAÇÃO DOS FILTROS
    df_filtrado = df[df['Ano'] == ano_sel].copy()
    if cat_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoria'] == cat_sel]
    if forma_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['FormaPagamento'] == forma_sel]

    # --- MAIN CONTENT ---
    
    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title(f"Performance {ano_sel}")
        st.markdown(f"**Período:** {df_filtrado['DataVenda'].min().strftime('%d/%m/%Y')} a {df_filtrado['DataVenda'].max().strftime('%d/%m/%Y')}")
    with col_h2:
        st.markdown("") 

    # KPIs
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    faturamento = df_filtrado['ValorTotal'].sum()
    vendas_qtd = df_filtrado.shape[0] # Mais rápido que nunique de ID se cada linha for uma venda
    ticket = faturamento / vendas_qtd if vendas_qtd > 0 else 0
    clientes_unicos = df_filtrado['ClienteID'].nunique()

    kpi1.metric("Faturamento Total", f"R$ {faturamento:,.2f}", delta_color="normal")
    kpi2.metric("Volume de Vendas", f"{vendas_qtd}", delta_color="normal")
    kpi3.metric("Ticket Médio", f"R$ {ticket:,.2f}", delta_color="normal")
    kpi4.metric("Clientes Ativos", f"{clientes_unicos}", delta_color="normal")

    st.markdown("---")

    # ABAS
    tab1, tab2, tab3 = st.tabs(["📈 Visão Estratégica", "📦 Produtos & Estoque", "💳 Financeiro"])

    with tab1:
        # Primeira Linha de Gráficos
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.markdown("<div class='css-card'>", unsafe_allow_html=True)
            st.markdown("##### 💵 Faturamento Mensal")
            
            fat_mensal = df_filtrado.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
            
            fig = px.bar(fat_mensal, x='MesNome', y='ValorTotal', text='ValorTotal', 
                         color_discrete_sequence=['#3b82f6'])
            fig.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='css-card'>", unsafe_allow_html=True)
            st.markdown("##### 📈 Tendência de Vendas (Correção de Visibilidade)")
            
            qtd_mensal = df_filtrado.groupby(['Mes', 'MesNome'])['ProdutoID'].count().reset_index().sort_values('Mes')
            
            # Gráfico de Linha Melhorado
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=qtd_mensal['MesNome'], 
                y=qtd_mensal['ProdutoID'],
                mode='lines+markers+text', # Exibe linha, bolinha e texto
                name='Vendas',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#059669'),
                text=qtd_mensal['ProdutoID'],
                textposition="top center"
            ))
            
            fig2.update_layout(
                height=350,
                showlegend=True, # Legenda ativada
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='css-card'>", unsafe_allow_html=True)
        st.markdown("##### 🏆 Top 10 Produtos")
        
        top_produtos = df_filtrado.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=False).head(10)
        
        fig_prod = px.bar(top_produtos, y='NomeProduto', x='ValorTotal', orientation='h', 
                          text='ValorTotal', color='ValorTotal', color_continuous_scale='Blues')
        fig_prod.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
        fig_prod.update_layout(height=500, yaxis={'categoryorder':'total ascending'}, 
                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_prod, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        col_pay1, col_pay2 = st.columns([2, 1])
        with col_pay1:
            st.markdown("<div class='css-card'>", unsafe_allow_html=True)
            st.markdown("##### Distribuição por Pagamento")
            
            fat_pgto = df_filtrado.groupby('FormaPagamento')['ValorTotal'].sum().reset_index()
            fig_pizza = px.donut(fat_pgto, values='ValorTotal', names='FormaPagamento', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Prism)
            fig_pizza.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pizza, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # RODAPÉ TABELA
    st.markdown("### 📋 Detalhamento das Vendas")
    st.dataframe(
        df_filtrado[['DataVenda', 'NomeCliente', 'NomeProduto', 'Categoria', 'ValorTotal', 'FormaPagamento']]
        .sort_values('DataVenda', ascending=False)
        .head(100)
        .style.format({'ValorTotal': 'R$ {:,.2f}'}),
        use_container_width=True,
        height=300
    )
