import streamlit as st
import pandas as pd
import plotly.express as px
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
div[data-testid="stMetricLabel"] { font-size: 13px; font-weight: 600; color: #718096; text-transform: uppercase; }
h1 { color: #1a202c; font-weight: 700; font-size: 28px; }
.stButton>button { background-color: #4299e1; color: white; border-radius: 6px; padding: 0.5rem 1.5rem; font-weight: 600; border: none; }
.stButton>button:hover { background-color: #3182ce; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #e8ecf1; padding: 6px; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 6px; color: #4a5568; font-weight: 600; }
.stTabs [aria-selected="true"] { background-color: white !important; color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)

def process_data(v, c, p):
    df = pd.read_csv(v).merge(pd.read_csv(c), on='ClienteID').merge(pd.read_csv(p), on='ProdutoID')
    df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.','').str.replace(',','.').astype(float)
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'] = df['DataVenda'].dt.year
    df['Mes'] = df['DataVenda'].dt.month
    df['MesNome'] = df['Mes'].apply(lambda x: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][x-1])
    return df

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px 0;'><div style='font-size:48px;'>📊</div><h2 style='margin:10px 0 0;font-size:20px;'>Performance Comercial</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📤 CARREGAR DADOS")
    v = st.file_uploader("Vendas.csv", type=['csv'])
    c = st.file_uploader("Clientes.csv", type=['csv'])
    p = st.file_uploader("Produtos.csv", type=['csv'])
    
    if all([v,c,p]):
        st.success("✅ Arquivos carregados")
    else:
        st.warning(f"⚠️ Faltam {3-sum([bool(v),bool(c),bool(p)])} arquivo(s)")

if not all([v,c,p]):
    st.markdown("<div style='text-align:center;padding:80px;'><div style='font-size:64px;'>📊</div><h1>Bem-vindo</h1><p style='color:#718096;'>Carregue os arquivos CSV na barra lateral</p></div>", unsafe_allow_html=True)
    st.stop()

df = process_data(v,c,p)

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 FILTROS")
    anos = sorted(df['Ano'].unique())
    ano = st.selectbox("Ano", anos, index=len(anos)-1)
    cat = st.selectbox("Categoria", ['Todas'] + sorted(df['Categoria'].unique().tolist()))
    forma = st.selectbox("Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))

df_f = df[df['Ano']==ano].copy()
if cat!='Todas': df_f = df_f[df_f['Categoria']==cat]
if forma!='Todas': df_f = df_f[df_f['FormaPagamento']==forma]

st.markdown(f"<h1>Performance Comercial - {ano}</h1><p style='color:#718096;'>Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

col1,col2,col3,col4 = st.columns(4)
fat = df_f['ValorTotal'].sum()
vnd = df_f['VendaID'].nunique()
tkt = fat/vnd if vnd>0 else 0
cli = df_f['ClienteID'].nunique()

with col1:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Total Vendas ($)</p><p style='font-size:28px;color:#2c5282;font-weight:700;margin:8px 0 0;'>R$ {fat:,.2f}</p></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Vendas (Qtd)</p><p style='font-size:28px;color:#16a34a;font-weight:700;margin:8px 0 0;'>{vnd:,}</p></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Ticket Médio</p><p style='font-size:28px;color:#9333ea;font-weight:700;margin:8px 0 0;'>R$ {tkt:,.2f}</p></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div style='background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08);'><p style='font-size:12px;color:#718096;font-weight:600;margin:0;text-transform:uppercase;'>Produto Top</p><p style='font-size:20px;color:#ea580c;font-weight:700;margin:8px 0 0;'>{df_f.groupby('NomeProduto')['ValorTotal'].sum().idxmax()}</p></div>", unsafe_allow_html=True)

st.markdown("<div style='margin:30px 0;'></div>", unsafe_allow_html=True)

tab1,tab2,tab3 = st.tabs(["📈 Visão Geral","📦 Produtos","💳 Pagamentos"])

with tab1:
    st.markdown("<div style='background:white;padding:30px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:20px;'>", unsafe_allow_html=True)
    
    fm = df_f.groupby(['Mes','MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')
    
    fig = px.bar(fm, x='MesNome', y='ValorTotal', text='ValorTotal')
    fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside', marker_color='#4299e1')
    fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f7fafc'), margin=dict(t=20,b=20,l=20,r=20))
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div style='background:white;padding:30px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:20px;'>", unsafe_allow_html=True)
    
    top = df_f.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal',ascending=False).head(10)
    
    fig2 = px.bar(top, y='NomeProduto', x='ValorTotal', orientation='h', text='ValorTotal', color='ValorTotal', color_continuous_scale='Blues')
    fig2.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
    fig2.update_layout(height=450, showlegend=False, plot_bgcolor='white', margin=dict(t=20,b=20,l=20,r=20))
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div style='background:white;padding:30px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:20px;'>", unsafe_allow_html=True)
    
    pgto = df_f.groupby('FormaPagamento')['ValorTotal'].sum().reset_index()
    
    fig3 = px.pie(pgto, values='ValorTotal', names='FormaPagamento', color_discrete_sequence=['#4299e1','#48bb78','#ed8936'])
    fig3.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
    fig3.update_layout(height=400, margin=dict(t=20,b=20,l=20,r=20))
    
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='background:white;padding:25px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-top:30px;'>", unsafe_allow_html=True)
st.markdown("### Detalhamento de Vendas")

det = df_f[['DataVenda','NomeCliente','NomeProduto','Quantidade','ValorTotal','FormaPagamento']].sort_values('DataVenda',ascending=False).head(50)
det['DataVenda'] = det['DataVenda'].dt.strftime('%d/%m/%Y')

st.dataframe(det, use_container_width=True, height=400)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#a0aec0;font-size:12px;margin-top:40px;'>Dashboard criado com Python + Streamlit | © 2026</p>", unsafe_allow_html=True)
