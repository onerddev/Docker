import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from decimal import Decimal

from tracker import PriceTracker

# Configuração da página Streamlit
st.set_page_config(
    page_title="Price Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
        .metric-container {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .alert-box {
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar sessão
if 'tracker' not in st.session_state:
    # Configurar banco de dados
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'price_tracker')
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    st.session_state.tracker = PriceTracker(db_url)
    if not st.session_state.tracker.conectar():
        st.error("❌ Erro ao conectar ao banco de dados. Verifique as configurações.")
        st.stop()
    
    st.session_state.tracker.criar_tabelas()

tracker = st.session_state.tracker

# Barra lateral
with st.sidebar:
    st.title("⚙️ Configurações")
    opcao = st.radio(
        "Selecione uma opção:",
        ["📊 Dashboard", "➕ Adicionar Produto", "👁️ Monitorar Preço", "📋 Gerenciar Produtos"]
    )

# ============ PÁGINA: Dashboard ============
if opcao == "📊 Dashboard":
    st.title("💰 Price Tracker - Dashboard")
    
    produtos = tracker.obter_produtos()
    
    if not produtos:
        st.info("📌 Nenhum produto cadastrado ainda. Comece adicionando um novo produto!")
    else:
        # Métricas gerais
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Produtos", len(produtos))
        with col2:
            total_registros = sum(len(tracker.obter_historico(p.id)) for p in produtos)
            st.metric("Registros de Preço", total_registros)
        with col3:
            st.metric("Data Atual", datetime.now().strftime("%d/%m/%Y"))
        
        st.divider()
        
        # Selecionador de produto
        st.subheader("📈 Histórico de Preços")
        produto_selecionado = st.selectbox(
            "Selecione um produto:",
            produtos,
            format_func=lambda p: f"{p.nome} (ID: {p.id})"
        )
        
        if produto_selecionado:
            historico = tracker.obter_historico(produto_selecionado.id, limitar=100)
            
            if historico:
                # Preparar dados para gráfico
                df = pd.DataFrame([
                    {
                        'Data': h.data_consulta.strftime("%d/%m/%Y %H:%M"),
                        'Preço': float(h.preco),
                        'Timestamp': h.data_consulta
                    }
                    for h in reversed(historico)
                ])
                
                # Gráfico de linha
                fig = px.line(
                    df,
                    x='Data',
                    y='Preço',
                    title=f"Histórico de Preços - {produto_selecionado.nome}",
                    markers=True,
                    labels={'Preço': 'Preço (R$)', 'Data': 'Data e Hora'}
                )
                fig.add_hline(
                    y=float(produto_selecionado.preco_meta),
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Meta: R$ {produto_selecionado.preco_meta:.2f}"
                )
                fig.update_layout(
                    hovermode='x unified',
                    height=500,
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de dados
                with st.expander("📋 Ver Dados Brutos"):
                    st.dataframe(df[['Data', 'Preço']], use_container_width=True)
                
                # Estatísticas
                st.subheader("📊 Estatísticas")
                col1, col2, col3, col4 = st.columns(4)
                
                precos = df['Preço'].values
                with col1:
                    st.metric("Preço Atual", f"R$ {precos[-1]:.2f}")
                with col2:
                    st.metric("Preço Mínimo", f"R$ {precos.min():.2f}")
                with col3:
                    st.metric("Preço Máximo", f"R$ {precos.max():.2f}")
                with col4:
                    media = precos.mean()
                    st.metric("Preço Médio", f"R$ {media:.2f}")
                
                # Verificar alerta
                preco_atual = float(historico[0].preco)
                preco_meta = float(produto_selecionado.preco_meta)
                
                if preco_atual <= preco_meta:
                    economia = preco_meta - preco_atual
                    percentual = (economia / preco_meta * 100)
                    st.markdown(
                        f'<div class="alert-box alert-success">'
                        f'✅ Preço atingiu a meta! Você economiza R$ {economia:.2f} ({percentual:.1f}%)'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    diferenca = preco_atual - preco_meta
                    percentual = (diferenca / preco_meta * 100)
                    st.markdown(
                        f'<div class="alert-box alert-warning">'
                        f'⏳ Preço ainda não atingiu a meta. Faltam R$ {diferenca:.2f} ({percentual:.1f}%)'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("📌 Nenhum registro de preço para este produto ainda.")

# ============ PÁGINA: Adicionar Produto ============
elif opcao == "➕ Adicionar Produto":
    st.title("➕ Adicionar Novo Produto")
    
    with st.form("form_novo_produto"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome do Produto",
                placeholder="Ex: Samsung Galaxy S23"
            )
        
        with col2:
            preco_meta = st.number_input(
                "Preço Meta (R$)",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
        
        url = st.text_input(
            "URL do Produto",
            placeholder="Ex: https://www.exemplo.com/produto"
        )
        
        submitted = st.form_submit_button("✅ Adicionar Produto", use_container_width=True)
        
        if submitted:
            if nome and url and preco_meta:
                produto = tracker.adicionar_produto(nome, url, preco_meta)
                if produto:
                    st.success(f"✅ Produto '{nome}' adicionado com sucesso! (ID: {produto.id})")
                else:
                    st.error("❌ Erro ao adicionar produto.")
            else:
                st.error("❌ Preenchea todos os campos obrigatórios.")

# ============ PÁGINA: Monitorar Preço ============
elif opcao == "👁️ Monitorar Preço":
    st.title("👁️ Monitorar Preço de Produtos")
    
    produtos = tracker.obter_produtos()
    
    if not produtos:
        st.warning("⚠️ Nenhum produto cadastrado para monitorar.")
    else:
        st.subheader("Selecione produtos para monitorar:")
        
        produtos_selecionados = st.multiselect(
            "Produtos:",
            produtos,
            format_func=lambda p: f"{p.nome} (Meta: R$ {p.preco_meta:.2f})"
        )
        
        if produtos_selecionados:
            if st.button("🔄 Atualizar Preços", use_container_width=True):
                progresso = st.progress(0)
                status_text = st.empty()
                resultados = []
                
                for idx, produto in enumerate(produtos_selecionados):
                    status_text.text(f"Monitorando: {produto.nome}...")
                    
                    historico = tracker.monitorar_preco(produto.id)
                    preco_atual = float(historico.preco) if historico else None
                    
                    if preco_atual:
                        preco_meta = float(produto.preco_meta)
                        alerta = "🎉 ALERTA!" if preco_atual <= preco_meta else "⏳ Aguardando"
                        resultados.append({
                            'Produto': produto.nome,
                            'Preço Atual': f"R$ {preco_atual:.2f}",
                            'Meta': f"R$ {preco_meta:.2f}",
                            'Status': alerta
                        })
                    
                    progresso.progress((idx + 1) / len(produtos_selecionados))
                
                st.divider()
                
                # Exibir resultados
                if resultados:
                    df_resultados = pd.DataFrame(resultados)
                    st.dataframe(df_resultados, use_container_width=True)
                    
                    st.success("✅ Monitoramento concluído com sucesso!")
                else:
                    st.error("❌ Erro ao monitorar preços.")

# ============ PÁGINA: Gerenciar Produtos ============
elif opcao == "📋 Gerenciar Produtos":
    st.title("📋 Gerenciar Produtos")
    
    produtos = tracker.obter_produtos()
    
    if not produtos:
        st.info("📌 Nenhum produto cadastrado.")
    else:
        # Tabela de produtos
        dados_produtos = []
        for p in produtos:
            historico = tracker.obter_historico(p.id, limitar=1)
            preco_atual = float(historico[0].preco) if historico else "N/A"
            dados_produtos.append({
                'ID': p.id,
                'Nome': p.nome,
                'URL': p.url,
                'Meta (R$)': f"{p.preco_meta:.2f}",
                'Preço Atual': f"R$ {preco_atual:.2f}" if isinstance(preco_atual, float) else preco_atual,
            })
        
        df_produtos = pd.DataFrame(dados_produtos)
        st.dataframe(df_produtos, use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Deletar Produto")
        
        produto_deletar = st.selectbox(
            "Selecione um produto para deletar:",
            produtos,
            format_func=lambda p: f"{p.nome} (ID: {p.id})"
        )
        
        if st.button("🗑️ Deletar Produto", use_container_width=True, type="secondary"):
            if tracker.deletar_produto(produto_deletar.id):
                st.success(f"✅ Produto '{produto_deletar.nome}' deletado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao deletar produto.")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 Price Tracker v1.0")
with col2:
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
with col3:
    st.caption("💡 Monitore seus produtos favoritos!")
