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

# CSS PERSONALIZADO (Design Mais Profissional e Limpo)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Fundo profissional neutro */
    .main { background-color: #F8FAFC; } 
    .block-container { padding-top: 2rem; }

    /* Sidebar moderna e escura */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] * { color: #F1F5F9 !important; }

    /* Estilização dos Cartões (Cards) */
    .stCard {
        background: white; 
        padding: 24px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        margin-top: 15px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #1E40AF; /* Azul corporativo */
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    h1 { color: #0F172A; font-weight: 700; font-size: 30px; }
    h3 { color: #1E293B; font-weight: 600; font-size: 18px; margin-bottom: 15px;}

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E2E8F0;
        border-radius: 6px;
        color: #475569;
        font-weight: 600;
        padding: 10px 24px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E40AF !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(30, 64, 175, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def process_data(vendas_file, clientes_file, produtos_file, vendedores_file, lojas_file):
    try:
        # Leitura dos 5 arquivos
        vendas = pd.read_csv(vendas_file)
        clientes = pd.read_csv(clientes_file)
        produtos = pd.read_csv(produtos_file)
        vendedores = pd.read_csv(vendedores_file) # Arquivo 4
        lojas = pd.read_csv(lojas_file)           # Arquivo 5

        # Mesclagem principal (ajuste as colunas de merge dos 2 novos arquivos conforme seu dataset)
        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')
        # Exemplo de merge com os novos arquivos (descomente se houver chaves):
        # df = df.merge(vendedores, on='VendedorID', how='left')
        # df = df.merge(lojas, on='LojaID', how='left')

        # Tratamento de dados monetários
        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

        # Tratamento de datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        df['MesNome'] = df['Mes'].apply(
            lambda x: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][x-1]
        )

        return df, None
    except Exception as e:
        return None, str(e)

# ==========================================
# SIDEBAR: UPLOAD DE 5 ARQUIVOS
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <div style='font-size: 40px;'>📈</div>
            <h2 style='margin: 10px 0 0 0; font-size: 22px; color: white;'>Comercial Analytics</h2>
            <p style='color: #94A3B8; font-size: 12px; margin-top: 5px;'>Versão Enterprise 2.1</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📤 INSERIR DADOS (5 Arquivos)")

    vendas_file = st.file_uploader("1. Vendas.csv", type=['csv'], key="vendas")
    clientes_file = st.file_uploader("2. Clientes.csv", type=['csv'], key="clientes")
    produtos_file = st.file_uploader("3. Produtos.csv", type=['csv'], key="produtos")
    vendedores_file = st.file_uploader("4. Vendedores.csv", type=['csv'], key="vendedores")
    lojas_file = st.file_uploader("5. Lojas.csv", type=['csv'], key="lojas")

    arquivos_ok = all([vendas_file, clientes_file, produtos_file, vendedores_file, lojas_file])

    if arquivos_ok:
        st.success("✅ Base de dados completa!")
    else:
        faltam = 5 - sum([bool(f) for f in [vendas_file, clientes_file, produtos_file, vendedores_file, lojas_file]])
        st.warning(f"⚠️ Aguardando {faltam} arquivo(s)...")

# Tela de Boas-Vindas se não houver arquivos
if not arquivos_ok:
    st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <div style='font-size: 72px; margin-bottom: 20px; color: #1E40AF;'>📊</div>
            <h1 style='font-size: 36px; color: #0F172A;'>Bem-vindo ao Dashboard</h1>
            <p style='font-size: 18px; color: #64748B;'>Por favor, faça o upload dos 5 arquivos CSV no menu lateral esquerdo.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==========================================
# PROCESSAMENTO DE DADOS
# ==========================================
with st.spinner('Consolidando base de dados...'):
    df, erro = process_data(vendas_file, clientes_file, produtos_file, vendedores_file, lojas_file)

if erro:
    st.error(f"❌ Erro ao processar dados: {erro}")
    st.stop()

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
if df is not None:

    # FILTROS NA SIDEBAR
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 FILTROS GERAIS")

        anos = sorted(df['Ano'].unique().tolist())
        ano_sel = st.selectbox("Selecione o Ano", anos, index=len(anos)-1)

        categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
        cat_sel = st.selectbox("Categoria de Produto", categorias)

        formas = ['Todas'] + sorted(df['FormaPagamento'].unique().tolist())
        forma_sel = st.selectbox("Forma Pagamento", formas)

        st.markdown("---")
        st.markdown(f"""
            <div style='padding: 15px; background: rgba(30, 64, 175, 0.1); border-radius: 8px; border: 1px solid rgba(30, 64, 175, 0.2);'>
                <p style='font-size: 12px; color: #94A3B8; margin: 0;'>PERÍODO DE ANÁLISE</p>
                <p style='font-size: 14px; font-weight: bold; color: white; margin: 5px 0 0 0;'>
                {df['DataVenda'].min().strftime('%d/%m/%Y')} a {df['DataVenda'].max().strftime('%d/%m/%Y')}</p>
            </div>
        """, unsafe_allow_html=True)

    # APLICAR FILTROS
    df_filtrado = df[df['Ano'] == ano_sel].copy()
    if cat_sel != 'Todas': df_filtrado = df_filtrado[df_filtrado['Categoria'] == cat_sel]
    if forma_sel != 'Todas': df_filtrado = df_filtrado[df_filtrado['FormaPagamento'] == forma_sel]

    # HEADER
    st.markdown(f"""
        <div style='margin-bottom: 25px;'>
            <h1>Resumo Executivo - {ano_sel}</h1>
            <p style='color: #64748B; font-size: 14px;'>Dados atualizados em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>
    """, unsafe_allow_html=True)

    # KPIS (Métricas Topo)
    col1, col2, col3, col4 = st.columns(4)

    faturamento = df_filtrado['ValorTotal'].sum()
    vendas_qtd = df_filtrado['VendaID'].nunique()
    ticket = faturamento / vendas_qtd if vendas_qtd > 0 else 0
    clientes = df_filtrado['ClienteID'].nunique()

    with col1:
        st.markdown(f"""<div class='stCard'><p style='color:#64748B; font-size:12px; font-weight:700;'>FATURAMENTO TOTAL</p><h2 style='color:#1E40AF; margin:0;'>R$ {faturamento:,.0f}</h2></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='stCard'><p style='color:#64748B; font-size:12px; font-weight:700;'>VOLUME DE VENDAS</p><h2 style='color:#1E40AF; margin:0;'>{vendas_qtd:,}</h2></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='stCard'><p style='color:#64748B; font-size:12px; font-weight:700;'>TICKET MÉDIO</p><h2 style='color:#1E40AF; margin:0;'>R$ {ticket:,.0f}</h2></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='stCard'><p style='color:#64748B; font-size:12px; font-weight:700;'>CLIENTES ATENDIDOS</p><h2 style='color:#1E40AF; margin:0;'>{clientes}</h2></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "📦 Performance de Produtos", "💳 Fluxo de Pagamentos"])

    with tab1:
        # Gráfico Faturamento Mensal
        st.markdown("<div class='stCard'><h3>Faturamento Mensal (Evolução)</h3>", unsafe_allow_html=True)
        fat_mensal = df_filtrado.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
        
        fig = px.bar(fat_mensal, x='MesNome', y='ValorTotal', text='ValorTotal', 
                     labels={'ValorTotal': 'Faturamento (R$)', 'MesNome': 'Mês'})
        fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside', 
                          marker_color='#3B82F6', marker_line_color='#2563EB', marker_line_width=1)
        fig.update_layout(height=350, plot_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        # GRÁFICO DE LINHAS CORRIGIDO (Mais Visível, com Dados e Legenda)
        with col_a:
            st.markdown("<div class='stCard'><h3>Volume de Vendas (Qtd)</h3>", unsafe_allow_html=True)
            qtd_mensal = df_filtrado.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

            fig2 = px.line(qtd_mensal, x='MesNome', y='VendaID', markers=True, text='VendaID',
                           labels={'VendaID': 'Qtd. de Vendas', 'MesNome': 'Mês'},
                           title='')
            
            # Formatação para dar destaque
            fig2.update_traces(
                line_color='#1E40AF', # Azul escuro forte
                line_width=4,
                marker=dict(size=10, color='#1E40AF', line=dict(width=2, color='white')),
                textposition='top center',
                textfont=dict(size=12, color='#1E40AF', weight='bold'),
                name='Vendas Realizadas'
            )
            
            fig2.update_layout(
                height=350, 
                plot_bgcolor='white',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(rangemode='tozero', showgrid=True, gridcolor='#F1F5F9'), # Força o gráfico a começar do 0
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("<div class='stCard'><h3>Share de Vendas por Categoria</h3>", unsafe_allow_html=True)
            fat_categoria = df_filtrado.groupby('Categoria')['ValorTotal'].sum().reset_index()
            fig3 = px.pie(fat_categoria, values='ValorTotal', names='Categoria', hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Prism)
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(height=350, showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='stCard'><h3>Top 10 Produtos (Curva A)</h3>", unsafe_allow_html=True)
        top_produtos = df_filtrado.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=False).head(10)
        fig_prod = px.bar(top_produtos, y='NomeProduto', x='ValorTotal', orientation='h', text='ValorTotal',
                          color='ValorTotal', color_continuous_scale='Blues')
        fig_prod.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_prod.update_layout(height=450, yaxis={'categoryorder':'total ascending'}, plot_bgcolor='white')
        st.plotly_chart(fig_prod, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='stCard'><h3>Distribuição por Forma de Pagamento</h3>", unsafe_allow_html=True)
        fat_pgto = df_filtrado.groupby('FormaPagamento')['ValorTotal'].sum().reset_index()
        fig_pizza = px.pie(fat_pgto, values='ValorTotal', names='FormaPagamento',
                           color_discrete_sequence=px.colors.qualitative.Safe)
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        fig_pizza.update_layout(height=450)
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # TABELA DE DETALHAMENTO
    st.markdown("---")
    st.markdown("### 📋 Transações Recentes")

    df_detalhes = df_filtrado[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
    df_detalhes['DataVenda'] = df_detalhes['DataVenda'].dt.strftime('%d/%m/%Y')
    
    # Formatação estilizada do DataFrame
    st.dataframe(
        df_detalhes.style.format({'ValorTotal': 'R$ {:,.2f}'}).background_gradient(subset=['ValorTotal'], cmap='Blues'),
        use_container_width=True, height=400
    )

    # FOOTER
    st.markdown("---")
    st.caption("🚀 Dashboard Enterprise | Desenvolvido com Python & Streamlit")
