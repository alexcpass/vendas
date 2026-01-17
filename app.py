import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Comercial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #f5f7fa; }
    .block-container { padding-top: 2rem; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f1419 100%);
    }
    section[data-testid="stSidebar"] * { color: white !important; }

    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #2c5282;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
    }

    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 28px;
    }

    .stButton>button {
        background-color: #4299e1;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
    }

    .stButton>button:hover {
        background-color: #3182ce;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e8ecf1;
        padding: 6px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #4a5568;
        font-weight: 600;
        padding: 8px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #2d3748 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def process_data(vendas_file, clientes_file, produtos_file):
    try:
        vendas = pd.read_csv(vendas_file)
        clientes = pd.read_csv(clientes_file)
        produtos = pd.read_csv(produtos_file)

        df = vendas.merge(clientes, on='ClienteID', how='left')
        df = df.merge(produtos, on='ProdutoID', how='left')

        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

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

# SIDEBAR
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 30px 0;'>
            <div style='font-size: 48px;'>📊</div>
            <h2 style='margin: 10px 0 0 0; font-size: 20px;'>Performance Comercial</h2>
            <p style='color: #a0aec0; font-size: 11px; margin-top: 5px;'>Dashboard v2.0</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📤 CARREGAR DADOS")

    vendas_file = st.file_uploader("Vendas.csv", type=['csv'], key="vendas")
    clientes_file = st.file_uploader("Clientes.csv", type=['csv'], key="clientes")
    produtos_file = st.file_uploader("Produtos.csv", type=['csv'], key="produtos")

    arquivos_ok = all([vendas_file, clientes_file, produtos_file])

    if arquivos_ok:
        st.success("✅ Todos os arquivos carregados")
    else:
        faltam = 3 - sum([bool(vendas_file), bool(clientes_file), bool(produtos_file)])
        st.warning(f"⚠️ Faltam {faltam} arquivo(s)")

if not arquivos_ok:
    st.markdown("""
        <div style='text-align: center; padding: 80px 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📊</div>
            <h1 style='font-size: 32px; margin-bottom: 10px;'>Bem-vindo ao Dashboard Comercial</h1>
            <p style='font-size: 16px; color: #718096;'>Carregue seus arquivos CSV na barra lateral para iniciar a análise</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# PROCESSAR
with st.spinner('Processando dados...'):
    df, erro = process_data(vendas_file, clientes_file, produtos_file)

if erro:
    st.error(f"❌ Erro: {erro}")
    st.stop()

# Ensure df is not None before proceeding with dashboard elements
if df is not None:

    # FILTROS NA SIDEBAR
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 FILTROS")

        anos = sorted(df['Ano'].unique().tolist())
        ano_sel = st.selectbox("Ano", anos, index=len(anos)-1)

        categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
        cat_sel = st.selectbox("Categoria", categorias)

        formas = ['Todas'] + sorted(df['FormaPagamento'].unique().tolist())
        forma_sel = st.selectbox("Forma Pagamento", formas)

        st.markdown("---")
        st.markdown(f"""
            <div style='padding: 15px; background: rgba(66, 153, 225, 0.1); border-radius: 8px;'>
                <p style='font-size: 11px; color: #a0aec0; margin: 0;'>PERÍODO</p>
                <p style='font-size: 13px; margin: 5px 0 0 0;'>{df['DataVenda'].min().strftime('%d/%m/%Y')} a {df['DataVenda'].max().strftime('%d/%m/%Y')}</p>
            </div>
        """, unsafe_allow_html=True)

    # APLICAR FILTROS
    df_filtrado = df[df['Ano'] == ano_sel].copy()

    if cat_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoria'] == cat_sel]

    if forma_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['FormaPagamento'] == forma_sel]

    # HEADER
    st.markdown(f"""
        <div style='margin-bottom: 30px;'>
            <h1>Performance Comercial - {ano_sel}</h1>
            <p style='color: #718096; font-size: 14px;'>Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>
    """, unsafe_allow_html=True)

    # KPIS
    col1, col2, col3, col4 = st.columns(4)

    faturamento = df_filtrado['ValorTotal'].sum()
    vendas_qtd = df_filtrado['VendaID'].nunique()
    ticket = faturamento / vendas_qtd if vendas_qtd > 0 else 0
    clientes = df_filtrado['ClienteID'].nunique()

    with col1:
        st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Total Vendas ($)</p>
                <p style='font-size: 28px; color: #2c5282; font-weight: 700; margin: 8px 0 0 0;'>R$ {faturamento:,.0f}</p>
            </div>
        """.format(faturamento=faturamento), unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Vendas (Qtd)</p>
                <p style='font-size: 28px; color: #2c5282; font-weight: 700; margin: 8px 0 0 0;'>{vendas_qtd:,}</p>
            </div>
        """.format(vendas_qtd=vendas_qtd), unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Ticket Médio</p>
                <p style='font-size: 28px; color: #2c5282; font-weight: 700; margin: 8px 0 0 0;'>R$ {ticket:,.0f}</p>
            </div>
        """.format(ticket=ticket), unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div style='background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <p style='font-size: 12px; color: #718096; font-weight: 600; margin: 0; text-transform: uppercase;'>Clientes Únicos</p>
                <p style='font-size: 28px; color: #2c5282; font-weight: 700; margin: 8px 0 0 0;'>{clientes}</p>
            </div>
        """.format(clientes=clientes), unsafe_allow_html=True)

    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "📦 Produtos", "💳 Pagamentos"])

    with tab1:
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)

        st.markdown("### Faturamento Mensal")

        fat_mensal = (
            df_filtrado.groupby(['Mes', 'MesNome'])['ValorTotal']
            .sum()
            .reset_index()
            .sort_values('Mes')
        )

        fig = px.bar(
            fat_mensal,
            x='MesNome',
            y='ValorTotal',
            text='ValorTotal',
            labels={'ValorTotal': 'Faturamento (R$)', 'MesNome': ''}
        )

        fig.update_traces(
            texttemplate='R$ %{text:,.0f}',
            textposition='outside',
            marker_color='#4299e1',
            marker_line_color='#3182ce',
            marker_line_width=1.5
        )

        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12, color='#4a5568'),
            xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
            yaxis=dict(showgrid=True, gridcolor='#f7fafc', showline=False),
            margin=dict(t=20, b=20, l=20, r=20),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # SEGUNDA LINHA
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("<div style='background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown("### Volume de Vendas")

            qtd_mensal = (
                df_filtrado.groupby(['Mes', 'MesNome'])['VendaID']
                .count()
                .reset_index()
                .sort_values('Mes')
            )

            fig2 = px.line(
                qtd_mensal,
                x='MesNome',
                y='VendaID',
                markers=True,
                labels={'VendaID': 'Quantidade', 'MesNome': ''}
            )

            fig2.update_traces(
                line_color='#48bb78',
                line_width=3,
                marker=dict(size=10, color='#48bb78')
            )
            fig2.update_layout(
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12, color='#4a5568'),
                xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f7fafc', showline=False),
                margin=dict(t=20, b=20, l=20, r=20),
                hovermode='x unified'
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("<div style='background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown("### Total de Vendas por Categoria")

            fat_categoria = (
                df_filtrado.groupby('Categoria')['ValorTotal']
                .sum()
                .reset_index()
                .sort_values('ValorTotal', ascending=False)
            )

            fig3 = px.pie(
                fat_categoria,
                values='ValorTotal',
                names='Categoria',
                title='Distribuição de Vendas por Categoria',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown("### Top 10 Produtos por Faturamento")

        top_produtos = (
            df_filtrado.groupby('NomeProduto')['ValorTotal']
            .sum()
            .reset_index()
            .sort_values('ValorTotal', ascending=False)
            .head(10)
        )

        fig_prod = px.bar(
            top_produtos,
            y='NomeProduto',
            x='ValorTotal',
            orientation='h',
            text='ValorTotal',
            color='ValorTotal',
            color_continuous_scale='Blues'
        )

        fig_prod.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_prod.update_layout(showlegend=False, height=400)

        st.plotly_chart(fig_prod, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown("### Distribuição por Forma de Pagamento")

        fat_pgto = (
            df_filtrado.groupby('FormaPagamento')['ValorTotal']
            .sum()
            .reset_index()
        )

        fig_pizza = px.pie(
            fat_pgto,
            values='ValorTotal',
            names='FormaPagamento',
            title='Distribuição por Pagamento',
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        fig_pizza.update_layout(height=400)

        st.plotly_chart(fig_pizza, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # TABELA DE DETALHAMENTO
    st.markdown("---")
    st.subheader("📋 Últimas 50 Vendas")

    df_detalhes = df_filtrado[[
        'DataVenda', 'NomeCliente', 'NomeProduto',
        'Quantidade', 'ValorTotal', 'FormaPagamento'
    ]].sort_values('DataVenda', ascending=False).head(50)

    df_detalhes['DataVenda'] = df_detalhes['DataVenda'].dt.strftime('%d/%m/%Y')
    df_detalhes['ValorTotal'] = df_detalhes['ValorTotal'].apply(lambda x: f'R$ {x:,.2f}')

    st.dataframe(df_detalhes, use_container_width=True, height=400)

    # FOOTER
    st.markdown("---")
    st.caption("Dashboard criado com Python + Streamlit | Dados carregados via upload")
