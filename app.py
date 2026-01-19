import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

# CSS personalizado para visual profissional
st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
    section[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #2c5282; }
    h1 { color: #1a202c; font-family: 'Arial', sans-serif; }
    .stButton>button[kind="primary"] { background-color: #4299e1; color: white; border: none; }
    .stButton>button[kind="secondary"] { background-color: #e2e8f0; color: #1a202c; border: none; }
</style>
""", unsafe_allow_html=True)

# Função de processamento de dados
@st.cache_data
def process(v, c, p):
    vendas = pd.read_csv(v)
    clientes = pd.read_csv(c)
    produtos = pd.read_csv(p)
    
    # Merge das tabelas
    df = vendas.merge(clientes, on='ClienteID').merge(produtos, on='ProdutoID')
    
    # Tratamento do ValorTotal (conversão padrão BR -> US)
    df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    
    # Tratamento de Datas
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'] = df['DataVenda'].dt.year
    df['Mes'] = df['DataVenda'].dt.month
    
    # Nomes dos meses ordenados
    meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    df['MesNome'] = df['Mes'].apply(lambda x: meses[x-1])
    
    return df

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:20px 0;'><div style='font-size:48px;'>📊</div><h2>Performance</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Upload de Arquivos")
    v = st.file_uploader("Vendas.csv", type=['csv'])
    c = st.file_uploader("Clientes.csv", type=['csv'])
    p = st.file_uploader("Produtos.csv", type=['csv'])

# Verifica se os arquivos foram carregados
if not all([v, c, p]):
    st.markdown("<div style='text-align:center;padding:80px;'><h1>📂 Por favor, carregue os arquivos CSV na barra lateral.</h1></div>", unsafe_allow_html=True)
    st.stop()

# Processa os dados
df = process(v, c, p)

# --- CABEÇALHO E FILTRO DE ANO ---
st.markdown(f"<h1>Performance Comercial</h1>", unsafe_allow_html=True)

anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: 
    st.session_state.ano = anos[-1] # Começa com o ano mais recente

# Botões de filtro de ano
st.write("### Filtrar por Ano:")
cols = st.columns([1] + [1]*len(anos) + [8]) # Colunas para botões ficarem compactos
with cols[0]:
    if st.button("Todos", type="primary" if st.session_state.ano == "Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()
        
for i, a in enumerate(anos):
    with cols[i+1]:
        if st.button(str(a), type="primary" if st.session_state.ano == a else "secondary", key=f"btn_ano_{a}"):
            st.session_state.ano = a
            st.rerun()

st.markdown("---")

# --- FILTROS SIDEBAR ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### Filtros Adicionais")
    cat = st.selectbox("Categoria", ['Todas'] + sorted(df['Categoria'].unique().tolist()))
    frm = st.selectbox("Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))

# --- APLICAÇÃO DOS FILTROS ---
df_f = df.copy()
if st.session_state.ano != "Todos":
    df_f = df_f[df_f['Ano'] == st.session_state.ano]

if cat != 'Todas': 
    df_f = df_f[df_f['Categoria'] == cat]

if frm != 'Todas': 
    df_f = df_f[df_f['FormaPagamento'] == frm]

# --- KPIS ---
c1, c2, c3, c4 = st.columns(4)
fat = df_f['ValorTotal'].sum()
qtd = df_f['VendaID'].nunique() # Supondo VendaID único por venda
tkt = fat / qtd if qtd > 0 else 0
clientes = df_f['ClienteID'].nunique()

c1.metric("💰 Faturamento", f"R$ {fat:,.0f}")
c2.metric("🛒 Vendas (Qtd)", f"{qtd}")
c3.metric("🎯 Ticket Médio", f"R$ {tkt:,.0f}")
c4.metric("👥 Clientes Únicos", f"{clientes}")

st.markdown("---")

# --- GRÁFICO 1: FATURAMENTO MENSAL ---
st.markdown("### 📈 Faturamento Mensal")
fm = df_f.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')

fig = px.bar(
    fm, 
    x='MesNome', 
    y='ValorTotal', 
    text='ValorTotal',
    title="Evolução Financeira"
)
fig.update_traces(
    texttemplate='R$ %{text:,.0f}', 
    textposition='outside', 
    marker_color='#4299e1',
    name="Faturamento", # Nome para a legenda
    showlegend=True
)
fig.update_layout(height=400, plot_bgcolor='white', showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# --- GRÁFICO 2: VOLUME DE VENDAS (MODIFICADO: Mais largo e visível) ---
st.markdown("### 📊 Volume de Vendas")
qm = df_f.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=qm['MesNome'], 
    y=qm['VendaID'],
    mode='lines+markers+text',
    name='Qtd. Vendas', # Legenda
    line=dict(color='#48bb78', width=5), # Linha mais grossa
    marker=dict(size=12, color='white', line=dict(color='#48bb78', width=3)), # Marcadores visíveis
    text=qm['VendaID'], # Rótulos de dados
    textposition='top center',
    textfont=dict(size=14, color='#2f855a', weight='bold')
))

fig2.update_layout(
    height=450, # Um pouco mais alto
    plot_bgcolor='#f7fafc',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False, title=None),
    yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Quantidade'),
    margin=dict(t=40, b=40, l=40, r=40),
    showlegend=True, # Legenda ativada
    legend=dict(orientation="h", y=1.1, x=0) # Legenda no topo
)
st.plotly_chart(fig2, use_container_width=True)

# --- GRÁFICO 3: TOP 10 PRODUTOS (MODIFICADO: Movido para baixo) ---
st.markdown("### 📦 Top 10 Produtos por Faturamento")
tp = df_f.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=False).head(10)

fig3 = px.bar(
    tp, 
    y='NomeProduto', 
    x='ValorTotal', 
    orientation='h', 
    text='ValorTotal', 
    color='ValorTotal', 
    color_continuous_scale='Blues'
)
fig3.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
fig3.update_layout(height=500, showlegend=False, plot_bgcolor='white') # Altura ajustada
st.plotly_chart(fig3, use_container_width=True)

# --- TABELA DE DADOS ---
st.markdown("---\n### 📋 Detalhamento das Últimas Vendas")
det = df_f[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
det['DataVenda'] = det['DataVenda'].dt.strftime('%d/%m/%Y')
det['ValorTotal'] = det['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}") # Formatação na tabela
st.dataframe(det, use_container_width=True, height=400)

st.caption("Dashboard Python + Streamlit | Atualizado")
