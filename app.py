import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

st.markdown("""
<style>
.main { background-color: #f5f7fa; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
section[data-testid="stSidebar"] * { color: white !important; }
div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #2c5282; }
h1 { color: #1a202c; }
.stButton>button[kind="primary"] { background-color: #4299e1; color: white; }
</style>
""", unsafe_allow_html=True)

def process(v,c,p):
    vendas = pd.read_csv(v)
    clientes = pd.read_csv(c)
    produtos = pd.read_csv(p)
    df = vendas.merge(clientes, on='ClienteID').merge(produtos, on='ProdutoID')
    df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.','').str.replace(',','.').astype(float)
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'], df['Mes'] = df['DataVenda'].dt.year, df['DataVenda'].dt.month
    df['MesNome'] = df['Mes'].apply(lambda x: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][x-1])
    return df

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px 0;'><div style='font-size:48px;'>📊</div><h2>Performance</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    v = st.file_uploader("Vendas.csv", type=['csv'])
    c = st.file_uploader("Clientes.csv", type=['csv'])
    p = st.file_uploader("Produtos.csv", type=['csv'])

if not all([v,c,p]):
    st.markdown("<div style='text-align:center;padding:80px;'><h1>Carregue os arquivos CSV</h1></div>", unsafe_allow_html=True)
    st.stop()

df = process(v,c,p)

st.markdown(f"<h1>Performance Comercial</h1>", unsafe_allow_html=True)

# BOTÕES DE ANO
anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: st.session_state.ano = anos[-1]

cols = st.columns([1]+[1]*len(anos))
with cols[0]:
    if st.button("Todos", type="primary" if st.session_state.ano=="Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()
for i,a in enumerate(anos):
    with cols[i+1]:
        if st.button(str(a), type="primary" if st.session_state.ano==a else "secondary", key=f"a{a}"):
            st.session_state.ano = a
            st.rerun()

st.markdown("---")

# FILTROS SIDEBAR
with st.sidebar:
    st.markdown("---")
    cat = st.selectbox("Categoria", ['Todas']+sorted(df['Categoria'].unique().tolist()))
    frm = st.selectbox("Pagamento", ['Todas']+sorted(df['FormaPagamento'].unique().tolist()))

df_f = df if st.session_state.ano=="Todos" else df[df['Ano']==st.session_state.ano].copy()
if cat!='Todas': df_f = df_f[df_f['Categoria']==cat]
if frm!='Todas': df_f = df_f[df_f['FormaPagamento']==frm]

# KPIS
c1,c2,c3,c4 = st.columns(4)
fat,qtd = df_f['ValorTotal'].sum(), df_f['VendaID'].nunique()
tkt = fat/qtd if qtd>0 else 0

c1.metric("💰 Faturamento", f"R$ {fat:,.0f}")
c2.metric("🛒 Vendas", f"{qtd}")
c3.metric("🎯 Ticket Médio", f"R$ {tkt:,.0f}")
c4.metric("👥 Clientes", f"{df_f['ClienteID'].nunique()}")

st.markdown("---")

# GRÁFICO MENSAL
st.markdown("### 📈 Faturamento Mensal")
fm = df_f.groupby(['Mes','MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
fig = px.bar(fm, x='MesNome', y='ValorTotal', text='ValorTotal')
fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside', marker_color='#4299e1')
fig.update_layout(height=400, plot_bgcolor='white')
st.plotly_chart(fig, use_container_width=True)

# SEGUNDA LINHA
ca,cb = st.columns(2)

with ca:
    st.markdown("### 📊 Volume de Vendas")
    qm = df_f.groupby(['Mes','MesNome'])['VendaID'].count().reset_index().sort_values('Mes')
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=qm['MesNome'], y=qm['VendaID'],
        mode='lines+markers+text',
        line=dict(color='#48bb78', width=4),
        marker=dict(size=14, color='#48bb78', line=dict(color='white', width=2)),
        text=qm['VendaID'],
        textposition='top center',
        textfont=dict(size=13, color='#1a365d', weight='bold')
    ))
    fig2.update_layout(
        height=400,
        plot_bgcolor='#fafafa',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, title='Mês'),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Qtd'),
        margin=dict(t=20,b=20,l=20,r=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

with cb:
    st.markdown("### 📦 Top 10 Produtos")
    tp = df_f.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=False).head(10)
    fig3 = px.bar(tp, y='NomeProduto', x='ValorTotal', orientation='h', text='ValorTotal', color='ValorTotal', color_continuous_scale='Blues')
    fig3.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# TABELA
st.markdown("---\n### 📋 Últimas 50 Vendas")
det = df_f[['DataVenda','NomeCliente','NomeProduto','Quantidade','ValorTotal','FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
det['DataVenda'] = det['DataVenda'].dt.strftime('%d/%m/%Y')
st.dataframe(det, use_container_width=True, height=400)

st.caption("Dashboard Python + Streamlit")
