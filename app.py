# GRÁFICO 2: VOLUME (Dark Pearl & Soft Orange)
st.markdown("### 📊 Sazonalidade de Vendas")
df_vol = df_filtered.groupby(['Mes', 'MesNome'])['VendaID'].count().reset_index().sort_values('Mes')

fig_vol = go.Figure()

# Barras (Laranja Suave)
fig_vol.add_trace(go.Bar(
    x=df_vol['MesNome'], 
    y=df_vol['VendaID'],
    name='Volume',
    marker_color='#F6AD55',  # Laranja Suave
    opacity=0.9,
    text=df_vol['VendaID'],
    textposition='inside',
    # CORREÇÃO: Removido 'weight', mantido apenas color e size
    textfont=dict(color='black', size=14) 
))

# Linha (Roxo para complementar o laranja)
fig_vol.add_trace(go.Scatter(
    x=df_vol['MesNome'], 
    y=df_vol['VendaID'],
    mode='lines+markers', 
    name='Tendência',
    line=dict(color='#9F7AEA', width=4), # Roxo Claro
    marker=dict(size=10, color='#9F7AEA', line=dict(color='white', width=2))
))

fig_vol.update_layout(
    height=400,
    # Configuração "Dark Pearlescent" (Cinza Azulado Profundo)
    plot_bgcolor='#4A5568', 
    paper_bgcolor='#2D3748',
    font=dict(color='white'), # Todo texto global branco
    xaxis=dict(
        showgrid=False, 
        # CORREÇÃO: Removido 'weight'
        tickfont=dict(color='white', size=13),
        linecolor='#A0AEC0'
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#718096', 
        # CORREÇÃO: Sintaxe correta para título em dict
        title=dict(
            text='Quantidade',
            font=dict(color='white')
        ),
        tickfont=dict(color='white')
    ),
    legend=dict(
        orientation="h", y=1.1, x=0,
        font=dict(color='white'),
        bgcolor='rgba(0,0,0,0)'
    ),
    margin=dict(l=20, r=20, t=50, b=20)
)
st.plotly_chart(fig_vol, use_container_width=True)
