import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Dashboard Comercial", page_icon="📊", layout="wide")

# CSS personalizado (Estilos Visuais)
st.markdown("""
<style>
    /* Configuração Geral */
    .main { background-color: #f5f7fa; }
    h1 { margin: 0; padding: 0; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1f36, #0f1419); }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Métricas */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #2c5282; }
    
    /* BOTÕES DE ANO (Largos e Baixos) */
    .stButton > button {
        width: 100%;              /* Ocupa toda a largura da coluna */
        padding-top: 5px;         /* Reduz altura (mais baixo) */
        padding-bottom: 5px;      /* Reduz altura (mais baixo) */
        font-weight: 600;
        border-radius: 6px;
    }
    .stButton>button[kind="primary"] { background-color: #4299e1; color: white; border: none; }
    .stButton>button[kind="secondary"] { background-color: #e2e8f0; color: #1a202c; border: none; }
    
</style>
""", unsafe_allow_html=True)

# Função de processamento
@st.cache_data
def process(v, c, p):
    vendas = pd.read_csv(v)
    clientes = pd.read_csv(c)
    produtos = pd.read_csv(p)
    
    df = vendas.merge(clientes, on='ClienteID').merge(produtos, on='ProdutoID')
    
    # Tratamento de valores e datas
    df['ValorTotal'] = df['ValorTotal'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
    df['Ano'] = df['DataVenda'].dt.year
    df['Mes'] = df['DataVenda'].dt.month
    
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

if not all([v, c, p]):
    st.markdown("<div style='text-align:center;padding:80px;'><h1>📂 Carregue os arquivos na lateral</h1></div>", unsafe_allow_html=True)
    st.stop()

df = process(v, c, p)

# --- CABEÇALHO COM DEGRADÊ ---
# Fundo degrade do Azul Claro (#dbeafe) para o Verde Neon (#bef264)
st.markdown("""
    <div style="
        background: linear-gradient(90deg, #dbeafe 0%, #ccff33 100%); 
        padding: 25px; 
        border-radius: 12px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: #1e3a8a; font-family: sans-serif; font-weight: 800;">Performance Comercial</h1>
        <p style="color: #475569; margin: 5px 0 0 0; font-size: 14px;">Análise detalhada de vendas e produtos</p>
    </div>
""", unsafe_allow_html=True)

# --- FILTRO DE ANOS (BOTÕES LARGOS) ---
anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: st.session_state.ano = anos[-1]

st.write("### Selecione o Ano:")
# Ajuste das colunas para os botões ficarem alinhados
cols = st.columns([1] + [1]*len(anos) + [6]) 

with cols[0]:
    if st.button("Todos", type="primary" if st.session_state.ano == "Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()
        
for i, a in enumerate(anos):
    with cols[i+1]:
        if st.button(str(a), type="primary" if st.session_state.ano == a else "secondary", key=f"btn_{a}"):
            st.session_state.ano = a
            st.rerun()

st.markdown("---")

# Filtros Lógicos
with st.sidebar:
    st.markdown("---")
    cat = st.selectbox("Categoria", ['Todas'] + sorted(df['Categoria'].unique().tolist()))
    frm = st.selectbox("Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))

df_f = df.copy()
if st.session_state.ano != "Todos": df_f = df_f[df_f['Ano'] == st.session_state.ano]
if cat != 'Todas': df_f = df_f[df_f['Categoria'] == cat]
if frm != 'Todas': df_f = df_f[df_f['FormaPagamento'] == frm]

# --- KPIS ---
c1, c2, c3, c4 = st.columns(4)
fat = df_f['ValorTotal'].sum()
qtd = df_f['VendaID'].nunique()
tkt = fat / qtd if qtd > 0 else 0
c1.metric("💰 Faturamento", f"R$ {fat:,.0f}")
c2.metric("🛒 Vendas", f"{qtd}")
c3.metric("🎯 Ticket Médio", f"R$ {tkt:,.0f}")
c4.metric("👥 Clientes", f"{df_f['ClienteID'].nunique()}")

st.markdown("---")

# --- GRÁFICO 1: FATURAMENTO MENSAL ---
st.markdown("### 📈 Faturamento Mensal")
fm = df_f.groupby(['Mes', 'MesNome'])['ValorTotal'].sum().reset_index().sort_values('Mes')

fig = px.bar(fm, x='MesNome', y='ValorTotal', text='ValorTotal')
fig.update_traces(
    texttemplate='R$ %{text:,.0f}', 
    textposition='outside', 
    marker_color='#4299e1',
    showlegend=True,
    name="Valor Faturado"
)
fig.update_layout(height=400, plot_bgcolor='white', margin=dict(t=20))
st.plotly_chart(fig, use_container_width=True)

# --- GRÁFICO 2: VOLUME DE VENDAS (Legenda PRETA) ---
st.markdown("### 📊 Volume de Vendas")
qm = df_f.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=qm['MesNome'], 
    y=qm['VendaID'],
    mode='lines+markers+text',
    name='Qtd. Vendas',
    line=dict(color='#48bb78', width=4),
    marker=dict(size=12, color='white', line=dict(color='#48bb78', width=3)),
    text=qm['VendaID'],
    textposition='top center',
    # CONFIGURAÇÃO: Texto PRETO
    textfont=dict(size=14, color='black', weight='bold') 
))

fig2.update_layout(
    height=450,
    plot_bgcolor='#f7fafc',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False, title=None),
    yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
    showlegend=True,
    legend=dict(orientation="h", y=1.1, x=0)
)
st.plotly_chart(fig2, use_container_width=True)

# --- GRÁFICO 3: TOP 10 PRODUTOS (Decrescente + Legenda VERMELHA) ---
st.markdown("### 📦 Top 10 Produtos por Faturamento")
tp = df_f.groupby('NomeProduto')['ValorTotal'].sum().reset_index()

# Ordena do maior para o menor
tp = tp.sort_values('ValorTotal', ascending=False).head(10)

fig3 = px.bar(
    tp, 
    y='NomeProduto', 
    x='ValorTotal', 
    orientation='h', 
    text='ValorTotal', 
    color='ValorTotal', 
    color_continuous_scale='Blues'
)

# Inverte o eixo Y para o maior ficar no topo visualmente
fig3.update_layout(
    height=500, 
    yaxis=dict(autorange="reversed"), 
    plot_bgcolor='white',
    coloraxis_showscale=False
)

fig3.update_traces(
    texttemplate='R$ %{text:,.0f}', 
    textposition='outside',
    # CONFIGURAÇÃO: Texto VERMELHO
    textfont=dict(color='#d32f2f', size=12, weight='bold') 
)

st.plotly_chart(fig3, use_container_width=True)

# --- TABELA ---
st.markdown("---\n### 📋 Detalhamento")
det = df_f[['DataVenda', 'NomeCliente', 'NomeProduto', 'Quantidade', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(50)
det['DataVenda'] = det['DataVenda'].dt.strftime('%d/%m/%Y')
det['ValorTotal'] = det['ValorTotal'].apply(lambda x: f"R$ {x:,.2f}")
st.dataframe(det, use_container_width=True, height=400)
