import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO E CSS (ESTILO E-COMMERCE)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Store Manager Admin", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
    /* Importando fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fc;
    }

    /* Remove padding padrão do topo para criar um header fixo visual */
    .block-container { padding-top: 2rem; }

    /* ESTILO DOS CARDS (KPIs e PRODUTOS) */
    .ecommerce-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s;
        height: 100%;
    }
    .ecommerce-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        border-color: #e2e8f0;
    }

    /* Títulos dos Cards */
    .card-title {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Valores dos Cards */
    .card-metric {
        color: #1e293b;
        font-size: 24px;
        font-weight: 800;
    }

    /* Vitrine de Produto (Mini Card) */
    .product-box {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .product-icon {
        background: #eff6ff;
        color: #3b82f6;
        width: 50px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
    }

    /* Botões personalizados */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    /* Header Personalizado */
    .main-header {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PROCESSAMENTO (Mesma lógica robusta)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(v, c, p):
    try:
        vendas = pd.read_csv(v)
        clientes = pd.read_csv(c)
        produtos = pd.read_csv(p)
        
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        # Limpeza de moeda e datas
        df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        df['MesNome'] = df['Mes'].map(meses_map)
        
        return df
    except Exception:
        return None

# -----------------------------------------------------------------------------
# 3. INTERFACE (LAYOUT E-COMMERCE)
# -----------------------------------------------------------------------------

# --- SIDEBAR (Menu de Navegação) ---
with st.sidebar:
    st.markdown("### 🛍️ Painel da Loja")
    st.caption("Admin Dashboard v2.0")
    
    # Upload Compacto
    with st.expander("📂 Carregar Base de Dados", expanded=True):
        v_file = st.file_uploader("Vendas", type=['csv'])
        c_file = st.file_uploader("Clientes", type=['csv'])
        p_file = st.file_uploader("Produtos", type=['csv'])

if not all([v_file, c_file, p_file]):
    # Tela de "Login/Espera" bonita
    st.markdown("""
    <div style="text-align:center; margin-top: 100px;">
        <h1 style="color:#cbd5e0; font-size: 60px;">🏪</h1>
        <h3 style="color:#64748b;">Sua loja está fechada...</h3>
        <p style="color:#94a3b8;">Faça o upload dos arquivos na barra lateral para abrir o painel.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = load_data(v_file, c_file, p_file)

# --- HEADER (Estilo Barra de Topo de Site) ---
st.markdown(f"""
<div class="main-header">
    <div>
        <h1 style="margin:0; font-size: 24px; color: #1e293b;">Olá, Gestor! 👋</h1>
        <p style="margin:0; color: #64748b; font-size: 14px;">Aqui está o resumo da performance da sua loja.</p>
    </div>
    <div style="text-align: right;">
        <span style="background: #ecfdf5; color: #059669; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px;">● Loja Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- FILTROS HORIZONTAIS (Estilo Barra de Busca) ---
anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: st.session_state.ano = anos[-1]

c_filter, c_cat, c_pay = st.columns([2, 2, 2])

with c_filter:
    # Simulando abas de ano
    cols_ano = st.columns(len(anos) + 1)
    if cols_ano[0].button("Tudo", type="primary" if st.session_state.ano=="Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()
    for i, a in enumerate(anos):
        if cols_ano[i+1].button(str(a), type="primary" if st.session_state.ano==a else "secondary", key=f"b_{a}"):
            st.session_state.ano = a
            st.rerun()

# Aplica filtro de ano
df_f = df.copy()
if st.session_state.ano != "Todos": df_f = df_f[df_f['Ano'] == st.session_state.ano]

with c_cat:
    cat = st.selectbox("Filtrar Departamento", ['Todos'] + sorted(df['Categoria'].unique().tolist()))
with c_pay:
    pay = st.selectbox("Método de Pagamento", ['Todos'] + sorted(df['FormaPagamento'].unique().tolist()))

if cat != 'Todos': df_f = df_f[df_f['Categoria'] == cat]
if pay != 'Todos': df_f = df_f[df_f['FormaPagamento'] == pay]

st.markdown("<br>", unsafe_allow_html=True)

# --- CARDS DE MÉTRICAS (VISUAL CLEAN) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

def kpi_card(title, value, icon, color):
    return f"""
    <div class="ecommerce-card" style="border-left: 4px solid {color}">
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div class="card-title">{title}</div>
                <div class="card-metric">{value}</div>
            </div>
            <div style="font-size: 24px;">{icon}</div>
        </div>
    </div>
    """

fat = df_f['ValorTotal'].sum()
qtd = df_f['VendaID'].nunique()
tkt = fat/qtd if qtd > 0 else 0
cli = df_f['ClienteID'].nunique()

with kpi1: st.markdown(kpi_card("Receita Total", f"R$ {fat:,.0f}", "💰", "#3b82f6"), unsafe_allow_html=True)
with kpi2: st.markdown(kpi_card("Pedidos", f"{qtd}", "📦", "#10b981"), unsafe_allow_html=True)
with kpi3: st.markdown(kpi_card("Ticket Médio", f"R$ {tkt:,.0f}", "💳", "#f59e0b"), unsafe_allow_html=True)
with kpi4: st.markdown(kpi_card("Clientes Ativos", f"{cli}", "👥", "#8b5cf6"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- SEÇÃO CENTRAL: GRÁFICO + VITRINE DE TOP PRODUTOS ---
col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown("### 📈 Visão de Vendas")
    st.markdown("<div style='color: #64748b; margin-bottom: 10px;'>Fluxo de caixa mensal</div>", unsafe_allow_html=True)
    
    # Gráfico elegante e limpo
    fat_mensal = df_f.groupby(['Mes','MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fat_mensal['MesNome'], y=fat_mensal['ValorTotal'],
        mode='lines',
        fill='tozeroy', # Preenchimento embaixo da linha (estilo área)
        line=dict(color='#3b82f6', width=3),
        name='Receita'
    ))
    fig.update_layout(
        height=400,
        margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickprefix="R$ "),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("### 🔥 Mais Vendidos")
    st.markdown("<div style='color: #64748b; margin-bottom: 10px;'>Ranking de produtos</div>", unsafe_allow_html=True)
    
    # Lógica para criar "Cards de Produto"
    top_prods = df_f.groupby('NomeProduto').agg({'ValorTotal':'sum', 'Quantidade':'sum'}).reset_index()
    top_prods = top_prods.sort_values('ValorTotal', ascending=False).head(4)
    
    for index, row in top_prods.iterrows():
        st.markdown(f"""
        <div class="product-box">
            <div class="product-icon">{row['NomeProduto'][0]}</div>
            <div style="flex-grow: 1;">
                <div style="font-weight: 600; color: #1e293b;">{row['NomeProduto']}</div>
                <div style="font-size: 12px; color: #64748b;">{row['Quantidade']} unidades vendidas</div>
            </div>
            <div style="font-weight: 700; color: #059669;">R$ {row['ValorTotal']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

# --- PRATELEIRA DE PRODUTOS (GRID VIEW) ---
st.markdown("---")
st.markdown("### 🛍️ Detalhe do Inventário")
st.markdown("<div style='color: #64748b; margin-bottom: 20px;'>Performance detalhada por item do catálogo</div>", unsafe_allow_html=True)

# Agrupamento para a grade
grid_data = df_f.groupby('NomeProduto').agg({
    'ValorTotal': 'sum',
    'Quantidade': 'sum',
    'Categoria': 'first'
}).reset_index().sort_values('ValorTotal', ascending=False).head(8) # Top 8 para não poluir

# Criar grid de 4 colunas
cols = st.columns(4)
for i, (index, row) in enumerate(grid_data.iterrows()):
    col = cols[i % 4]
    with col:
        # Card estilo "Produto de E-commerce"
        st.markdown(f"""
        <div class="ecommerce-card" style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 40px; margin-bottom: 10px;">🏷️</div>
            <div style="font-weight: 600; height: 50px; display: flex; align-items: center; justify-content: center;">{row['NomeProduto']}</div>
            <div style="color: #64748b; font-size: 12px; margin-bottom: 10px;">{row['Categoria']}</div>
            <div style="font-size: 20px; font-weight: 800; color: #3b82f6;">R$ {row['ValorTotal']:,.0f}</div>
            <div style="background: #f1f5f9; border-radius: 4px; padding: 4px; margin-top: 10px; font-size: 12px;">
                ⭐ {row['Quantidade']} vendas
            </div>
        </div>
        """, unsafe_allow_html=True)

st.caption("Store Manager System • Desenvolvido com Streamlit")
