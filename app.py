import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E TEMA SALESFORCE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Financial Analytics CRM", page_icon="☁️", layout="wide")

st.markdown("""
<style>
    /* Importando fonte estilo corporativo */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* FUNDO GERAL (Salesforce Light Gray) */
    .stApp {
        background-color: #F4F6F9;
        font-family: 'Roboto', sans-serif;
    }

    /* SIDEBAR (Branco limpo com borda) */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #D8DDE6;
    }
    
    /* TITULOS */
    h1, h2, h3 {
        color: #032D60; /* Salesforce Navy */
        font-weight: 400;
    }

    /* CARDS (CONTAINERS BRANCOS) */
    .crm-card {
        background-color: #FFFFFF;
        border: 1px solid #DDDBDA;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* KPI STYLE */
    .kpi-label {
        color: #54698D; /* Slate Gray */
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.0625rem;
    }
    .kpi-value {
        color: #032D60;
        font-size: 26px;
        font-weight: 300; /* Estilo Salesforce */
        margin-top: 4px;
    }

    /* BOTÕES (Salesforce Blue) */
    .stButton > button {
        background-color: #0070D2;
        color: white;
        border: 1px solid #0070D2;
        border-radius: 4px;
        font-weight: 400;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #005FB2;
        border-color: #005FB2;
    }
    /* Botão secundário (filtro inativo) */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: #0070D2;
        border: 1px solid #DDDBDA;
    }

    /* HEADER */
    .header-container {
        border-bottom: 2px solid #0070D2;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PROCESSAMENTO DE DADOS (ETL)
# -----------------------------------------------------------------------------
@st.cache_data
def load_crm_data(v, c, p):
    try:
        vendas = pd.read_csv(v)
        clientes = pd.read_csv(c)
        produtos = pd.read_csv(p)
        
        # Merge (Join de tabelas)
        df = vendas.merge(clientes, on='ClienteID', how='left').merge(produtos, on='ProdutoID', how='left')
        
        # Limpeza Numérica
        df['ValorTotal'] = (
            df['ValorTotal'].astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
        
        # Datas
        df['DataVenda'] = pd.to_datetime(df['DataVenda'], dayfirst=True)
        df['Ano'] = df['DataVenda'].dt.year
        df['Mes'] = df['DataVenda'].dt.month
        
        meses_map = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                     7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        df['MesNome'] = df['Mes'].map(meses_map)
        
        return df
    except Exception:
        return None

# -----------------------------------------------------------------------------
# 3. SIDEBAR (PAINEL DE IMPORTAÇÃO)
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo simulado
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="font-size: 40px;">☁️</div>
            <div>
                <h2 style="margin:0; font-size: 18px; font-weight:700;">Financial Cloud</h2>
                <p style="margin:0; font-size: 12px; color: #54698D;">Analytics Edition</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Data Import Wizard")
    st.caption("Carregue os arquivos .csv para atualizar os painéis.")
    
    v_file = st.file_uploader("Transactions (Vendas)", type=['csv'])
    c_file = st.file_uploader("Accounts (Clientes)", type=['csv'])
    p_file = st.file_uploader("Services/Products", type=['csv'])

if not all([v_file, c_file, p_file]):
    st.info("ℹ️ Aguardando importação de dados para gerar os relatórios.")
    st.stop()

df = load_crm_data(v_file, c_file, p_file)

# -----------------------------------------------------------------------------
# 4. HEADER E FILTROS DE CONTROLE
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="header-container">
        <h1 style="font-size: 24px; margin-bottom: 5px;">Painel Financeiro Executivo</h1>
        <p style="color: #54698D; font-size: 14px;">Visão consolidada de receitas e oportunidades fechadas.</p>
    </div>
""", unsafe_allow_html=True)

# --- FILTRO DE ANO (BOTOES ESTILO ABAS) ---
anos = sorted(df['Ano'].unique())
if 'ano' not in st.session_state: st.session_state.ano = anos[-1]

cols_ano = st.columns([1] + [1]*len(anos) + [6])
with cols_ano[0]:
    if st.button("Consolidado", type="primary" if st.session_state.ano=="Todos" else "secondary"):
        st.session_state.ano = "Todos"
        st.rerun()

for i, ano in enumerate(anos):
    with cols_ano[i+1]:
        if st.button(str(ano), type="primary" if st.session_state.ano==ano else "secondary", key=f"btn_{ano}"):
            st.session_state.ano = ano
            st.rerun()

# --- FILTROS LATERAIS (Contexto) ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### Filtros de Visualização")
    cat_sel = st.selectbox("Linha de Negócio (Categoria)", ['Todas'] + sorted(df['Categoria'].unique().tolist()))
    pay_sel = st.selectbox("Condição de Pagamento", ['Todas'] + sorted(df['FormaPagamento'].unique().tolist()))

# Filtragem do Dataset
df_filtered = df.copy()
if st.session_state.ano != "Todos": df_filtered = df_filtered[df_filtered['Ano'] == st.session_state.ano]
if cat_sel != 'Todas': df_filtered = df_filtered[df_filtered['Categoria'] == cat_sel]
if pay_sel != 'Todas': df_filtered = df_filtered[df_filtered['FormaPagamento'] == pay_sel]

# -----------------------------------------------------------------------------
# 5. CARDS DE MÉTRICAS (VISUAL SALESFORCE)
# -----------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total_receita = df_filtered['ValorTotal'].sum()
total_ops = df_filtered['VendaID'].nunique()
avg_deal = total_receita / total_ops if total_ops > 0 else 0
contas_ativas = df_filtered['ClienteID'].nunique()

def crm_metric(col, label, value, icon):
    with col:
        st.markdown(f"""
        <div class="crm-card">
            <div style="display:flex; justify-content: space-between;">
                <div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                <div style="font-size: 24px; opacity: 0.7;">{icon}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

crm_metric(c1, "Receita Total Fechada", f"R$ {total_receita:,.0f}", "💰")
crm_metric(c2, "Negócios Fechados", f"{total_ops}", "🤝")
crm_metric(c3, "Ticket Médio (Deal Size)", f"R$ {avg_deal:,.0f}", "📊")
crm_metric(c4, "Contas Ativas", f"{contas_ativas}", "🏢")

# -----------------------------------------------------------------------------
# 6. GRÁFICOS (VISUAL LIMPO E CORPORATIVO)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<div class="crm-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Tendência de Receita Mensal")
    
    # Dados combinados
    fin_data = df_filtered.groupby(['Mes', 'MesNome']).agg({'ValorTotal': 'sum', 'VendaID': 'count'}).reset_index().sort_values('Mes')

    fig = go.Figure()
    
    # Barras (Volume Financeiro)
    fig.add_trace(go.Bar(
        x=fin_data['MesNome'], 
        y=fin_data['ValorTotal'],
        name='Receita (R$)',
        marker_color='#0070D2', # Salesforce Blue
        opacity=0.8,
        text=fin_data['ValorTotal'],
        texttemplate='%{text:.2s}',
        textposition='outside'
    ))
    
    # Linha (Tendência)
    fig.add_trace(go.Scatter(
        x=fin_data['MesNome'],
        y=fin_data['ValorTotal'],
        mode='lines+markers',
        name='Tendência',
        line=dict(color='#032D60', width=2), # Navy Blue
        marker=dict(size=6, color='white', line=dict(color='#032D60', width=2))
    ))

    fig.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=False, linecolor='#DDDBDA'),
        yaxis=dict(showgrid=True, gridcolor='#F3F3F3', showline=False),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="crm-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Top Oportunidades (Produtos)")
    
    top_items = df_filtered.groupby('NomeProduto')['ValorTotal'].sum().reset_index().sort_values('ValorTotal', ascending=True).tail(8)
    
    fig2 = px.bar(
        top_items, 
        x='ValorTotal', 
        y='NomeProduto', 
        orientation='h',
        text='ValorTotal',
        color_discrete_sequence=['#4BC076'] # Salesforce Green (Success)
    )
    
    fig2.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
    fig2.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=True, gridcolor='#F3F3F3'),
        yaxis=dict(title=None),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. TABELA DE DETALHES (LIST VIEW CRM)
# -----------------------------------------------------------------------------
st.markdown('<div class="crm-card">', unsafe_allow_html=True)
st.markdown("### 📋 Transações Recentes")

# Preparar tabela estilo relatório
df_table = df_filtered[['DataVenda', 'NomeCliente', 'Categoria', 'NomeProduto', 'ValorTotal', 'FormaPagamento']].sort_values('DataVenda', ascending=False).head(100)
df_table.columns = ['Data', 'Conta (Cliente)', 'Linha de Negócio', 'Produto/Serviço', 'Valor (R$)', 'Status Pgto']

# Formatar
df_table['Data'] = df_table['Data'].dt.strftime('%d/%m/%Y')
df_table['Valor (R$)'] = df_table['Valor (R$)'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(
    df_table, 
    use_container_width=True, 
    height=400,
    hide_index=True
)
st.markdown('</div>', unsafe_allow_html=True)
