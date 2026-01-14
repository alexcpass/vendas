import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

@st.cache_data
def load_data():
    # Carregar os CSVs
    vendas = pd.read_csv('vendas.csv')
    clientes = pd.read_csv('clientes.csv')
    produtos = pd.read_csv('produtos.csv')
    
    # Merge das tabelas
    vendas_clientes = vendas.merge(clientes, on='ClienteID', how='left')
    vendas_completo = vendas_clientes.merge(produtos, on='ProdutoID', how='left')
    
    # Converter ValorTotal para float
    vendas_completo['ValorTotal'] = (
        vendas_completo['ValorTotal']
          .astype(str)
          .str.replace('.', '', regex=False)
          .str.replace(',', '.', regex=False)
          .astype(float)
    )
    
    # Converter DataVenda para datetime e extrair Ano e Mes
    vendas_completo['DataVenda'] = pd.to_datetime(vendas_completo['DataVenda'], dayfirst=True)
    vendas_completo['Ano'] = vendas_completo['DataVenda'].dt.year
    vendas_completo['Mes'] = vendas_completo['DataVenda'].dt.month
    
    return vendas_completo

# Carregar dados
df = load_data()

# Título principal
st.title('📊 Dashboard Financeiro - Vendas')

# Sidebar com filtros
st.sidebar.header('Filtros')
anos = sorted(df['Ano'].unique())
ano_selecionado = st.sidebar.selectbox('Selecione o Ano:', anos)

# Filtrar dados
df_filtrado = df[df['Ano'] == ano_selecionado]

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    faturamento_total = df_filtrado['ValorTotal'].sum()
    st.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")

with col2:
    qtd_vendas = df_filtrado['VendaID'].nunique()
    st.metric("Total de Vendas", f"{qtd_vendas:,}")

with col3:
    ticket_medio = faturamento_total / qtd_vendas if qtd_vendas > 0 else 0
    st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

with col4:
    qtd_clientes = df_filtrado['ClienteID'].nunique()
    st.metric("Clientes Únicos", f"{qtd_clientes:,}")

st.markdown("---")

# Gráfico de Faturamento Mensal
st.subheader(f'📈 Faturamento Mensal - {ano_selecionado}')

fat_mensal = (
    df_filtrado.groupby('Mes')['ValorTotal']
    .sum()
    .reset_index()
    .sort_values('Mes')
)

fat_mensal['MesNome'] = fat_mensal['Mes'].apply(
    lambda x: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][x-1]
)

sns.set_theme(style='whitegrid')
fig, ax = plt.subplots(figsize=(12, 4))
sns.barplot(
    data=fat_mensal,
    x='MesNome', y='ValorTotal',
    ax=ax, color='#1f77b4'
)
ax.set_xlabel('Mês')
ax.set_ylabel('Faturamento (R$)')
ax.set_title(f'Evolução Mensal de Faturamento - {ano_selecionado}')
plt.xticks(rotation=0)
st.pyplot(fig)

st.markdown("---")

# Duas colunas para análises
col_left, col_right = st.columns(2)

with col_left:
    st.subheader('🏆 Top 10 Produtos - Faturamento')
    fat_produto = (
        df_filtrado.groupby('NomeProduto')['ValorTotal']
        .sum()
        .reset_index()
        .sort_values('ValorTotal', ascending=False)
        .head(10)
    )
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=fat_produto,
        y='NomeProduto', x='ValorTotal',
        ax=ax2, palette='Blues_r'
    )
    ax2.set_xlabel('Faturamento (R$)')
    ax2.set_ylabel('Produto')
    st.pyplot(fig2)

with col_right:
    st.subheader('💳 Faturamento por Forma de Pagamento')
    fat_pagamento = (
        df_filtrado.groupby('FormaPagamento')['ValorTotal']
        .sum()
        .reset_index()
        .sort_values('ValorTotal', ascending=False)
    )
    
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.pie(
        fat_pagamento['ValorTotal'],
        labels=fat_pagamento['FormaPagamento'],
        autopct='%1.1f%%',
        startangle=90
    )
    ax3.set_title('Distribuição por Forma de Pagamento')
    st.pyplot(fig3)

st.markdown("---")

# Tabela de detalhes
st.subheader('📋 Detalhamento de Vendas')
df_detalhes = df_filtrado[[
    'DataVenda', 'NomeCliente', 'NomeProduto', 
    'Quantidade', 'ValorTotal', 'FormaPagamento'
]].sort_values('DataVenda', ascending=False).head(50)

st.dataframe(df_detalhes, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Dashboard criado com Python + Streamlit | Dados fictícios para demonstração")
