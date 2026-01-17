import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { background-color: #f5f7fa; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
section[data-testid="stSidebar"] * { color: white !important; }
div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; color: #2c5282; }
h1 { color: #1a202c; font-weight: 700; font-size: 28px; }
.stButton>button { background-color: #e2e8f0; color: #2d3748; border-radius: 6px; padding: 8px 20px; font-weight: 600; border: 1px solid #cbd5e0; }
.stButton>button:hover { background-color: #cbd5e0; }
.stButton>button[kind="primary"] { background-color: #4299e1 !important; color: white !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #e8ecf1; padding: 6px; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 6px; color: #4a5568; font-weight: 600; padding: 8px 20px; }
.stTabs [aria-selected="true"] { background-color: white !important; color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)

def process_data(v, c, p, vend=None, reg=None):
    try:
        vendas = pd.read_csv(v)
        clientes = pd.read_csv(c)
        produtos = pd.read_csv(p)
        
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        if vend:
            vendedores = pd.read_csv(vend)
            df = df.merge(vendedores, on='VendedorID', how='left', suffixes=('', '_v'))
            if 'Nome' in df.columns:
                df = df.rename(columns={'Nome': 'NomeVendedor'})
        
        df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.','').str.replace(',','.').astype(float)
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        df['MesNome'] = df['Mes'].apply(lambda x: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][x-1])
        return df, None
    except Exception as e:
        return None, str(e)

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px 0 30px;'><div style='font-size:48px;'>📊</div><h2 style='margin:10px 0 0;font-size:20px;'>Performance Comercial</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📤 CARREGAR DADOS")
    st.markdown("**Obrigatórios:**")
    v = st.file_uploader("Vendas.csv", type=['csv'], key="v")
    c = st.file_uploader("Clientes.csv", type=['csv'], key="c")
    p = st.file_uploader("Produtos.csv", type=['csv'], key="p")
    st.markdown("**Opcionais:**")
    vend = st.file_uploader("Vendedores.csv", type=['csv'], key="vend")
    reg = st.file_uploader("Regiões.csv", type=['csv'], key="reg")
    
    if all([v,c,p]):
        st.success(f"✅ {3+sum([bool(vend),bool(reg)])}/5 arquivos")
    else:
        st.warning(f"⚠️ Faltam {3-sum([bool(v),bool(c),bool(p)])} arquivo(s)")

if not all([v,c,p]):
    st.markdown("<div style='text-align:center;padding:80px;'><div style='font-size:64px;'>📊</div><h1>Bem-vindo</h1><p style='color:#718096;'>Carregue os arquivos CSV</p></div>", unsafe_allow_html=True)
    st.stop()

with st.spinner('Processando...'):
    df, erro = process_data(v,c,p,vend,reg)

if erro:
    st.error(f"❌ {erro}")
    st.stop()

st.markdown(f"<h1>Performance Comercial</h1><p style='color:#718096;font-size:14px;'>Atualizado {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

# FILTRO DE ANO COM BOTÕES
st.markdown("<p style='font-size:12px;color:#718096;font-weight:600;margin:15px 0 10px;'>DASHBOARDS</p>", unsafe_allow_html=True)

anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state:
    st.session_state.ano = anos[-1]

cols = st.columns([1.2] + [1]*len(anos) + [1]*2)

with cols[0]:
    if st.button("Selecionar tudo", use_container_width=True, type="primary" if st.session_state.ano=="Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()

for i, ano in enumerate(anos):
    with cols[i+1]:
        if st.button(str(ano), use_container_width=True, type="primary" if st.session_state.ano==ano else "secondary", key=f"a{ano}"):
            st.session_state.ano = ano
            st.rerun()

cats = sorted(df['Categoria'].unique())
for i, cat in enumerate(cats):
    with cols[len(anos)+1+i]:
        st.button(cat, use_container_width=True, key=f"c{cat}")

st.markdown("---")

# FILTROS SIDEBAR
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 FILTROS")
    cat_sel = st.selectbox("Categoria", ['Todas'] + cats)
    forma_sel = st.selectbox("Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))
    st.markdown("---")
    st.markdown(f"<div style='padding:15px;background:rgba(66,153,225,0.1);border-radius:8px;'><p style='font-size:11px;color:#a0aec0;margin:0;'>PERÍODO</p><p style='font-size:13px;margin:5px 0 0;'>{df['DataVenda'].min().strftime('%d/%m/%Y')} a {df['DataVenda'].max().strftime('%d/%m/%Y')}</p></div>", unsafe_allow_html=True)

# APLICAR FILTROS
df_f = df if st.session_state.ano=="Todos" else df[df['Ano']==st.session_state.ano].copy()
if cat_sel!='Todas': df_f = df_f[df_f['Categoria']==cat_sel]
if forma_sel!='Todas': df_f = df_f[df_f['FormaPagamento']==forma_sel]

# KPIS
col1,col2,col3,col4 = st.columns(4)
fat = df_f['ValorTotal'].sum()
qtd = df_f['VendaID'].nunique()
tkt = fat/qtd if qtd>0 else 0
cli = df_f['ClienteID'].nunique()

with col1:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Total Vendas ($)</p><p style='font-size:28px;color:#2c5282;font-weight:700;margin:8px 0 0;'>R$ {fat:,.2f}</p></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Vendas (Qtd)</p><p style='font-size:28px;color:#16a34a;font-weight:700;margin:8px 0 0;'>{qtd:,}</p></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Ticket Médio</p><p style='font-size:28px;color:#9333ea;font-weight:700;margin:8px 0 0;'>R$ {tkt:,.2f}</p></div>", unsafe_allow_html=True)

with col4:
    top = df_f.groupby('NomeProduto')['ValorTotal'].sum().idxmax() if len(df_f)>0 else "N/A"
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Produto Top</p><p style='font-size:18px;color:#ea580c;font-weight:700;margin:8px 0 0;'>{top}</p></div>", unsafe_allow_html=True)

st.markdown("<div style='margin:30px 0;'></div>", unsafe_allow_html=True)

# TABS
tab1,tab2,tab3 = st.tabs(["📈 Visão Geral","📦 Produtos","💳 Pagamentos"])

with tab1:
    st.markdown("<div style='background:white;padding:30px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:20px;'>", unsafe_allow_html=True)
    st.markdown("### Faturamento Mensal")
    
    fm = df_f.groupby(['Mes','MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
    fig = px.bar(fm, x='MesNome', y='ValorTotal', text='ValorTotal')
    fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside', marker_color='#4299e1')
    fig.update_layout(height=400, plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f7fafc'), margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    cola, colb = st.columns(2)
    
    with cola:
        st.markdown("<div style='background:white;padding:25px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown("### Volume de Vendas")
        
        qm = df_f.groupby(['Mes','MesNome'])['VendaID'].count().reset_index().sort_values('Mes')
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=qm['MesNome'],
            y=qm['VendaID'],
            mode='lines+markers+text',
            line=dict(color='#48bb78', width=4),
            marker=dict(size=12, color='#48bb78', line=dict(color='#2d7a4f', width=2)),
            text=qm['VendaID'],
            textposition='top center',
            textfont=dict(size=13, color='#1a202c', family='Inter'),
            name='Vendas',
            hovertemplate='<b>%{x}</b><br>Vendas: %{y}<extra></extra>'
        ))
        
        fig2.update_layout(
            height=400,
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            font=dict(size=12, color='#4a5568'),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#e2e8f0',
                title='Mês',
                titlefont=dict(size=13, color='#4a5568')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#e
