"""
Script de teste e exemplo de uso do Price Tracker
Demonstra como usar a biblioteca sem a interface Streamlit
"""

import logging
from tracker import PriceTracker
from notificador import NotificadorPreco, criar_callback_log_arquivo

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def exemplo_basico():
    """Exemplo básico de uso do Price Tracker"""
    
    print("\n" + "="*60)
    print("EXEMPLO 1: Uso Básico do Price Tracker")
    print("="*60 + "\n")
    
    # Configuração do banco de dados
    db_url = "postgresql://postgres:postgres@localhost:5432/price_tracker"
    
    # Inicializar o tracker
    tracker = PriceTracker(db_url)
    
    # Conectar ao banco de dados
    if not tracker.conectar():
        print("❌ Falha ao conectar. Verifique as credenciais.")
        return
    
    # Criar tabelas
    tracker.criar_tabelas()
    
    # Adicionar alguns produtos
    print("\n📦 Adicionando produtos...")
    produtos = [
        ("Samsung Galaxy S23", "https://exemplo.com/samsung", 2500.00),
        ("iPhone 15 Pro", "https://exemplo.com/iphone", 7000.00),
        ("MacBook Air M2", "https://exemplo.com/macbook", 8000.00),
    ]
    
    for nome, url, preco_meta in produtos:
        tracker.adicionar_produto(nome, url, preco_meta)
    
    # Listar produtos
    print("\n📋 Produtos cadastrados:")
    todos_produtos = tracker.obter_produtos()
    for p in todos_produtos:
        print(f"  ID: {p.id} | {p.nome} | Meta: R$ {p.preco_meta:.2f}")


def exemplo_notificacoes():
    """Exemplo de sistema de notificações"""
    
    print("\n" + "="*60)
    print("EXEMPLO 2: Sistema de Notificações")
    print("="*60 + "\n")
    
    # Criar notificador
    notificador = NotificadorPreco()
    
    # Registrar callback para salvar em arquivo
    callback_log = criar_callback_log_arquivo('alertas_preco.log')
    notificador.registrar_callback(callback_log)
    
    # Simular verificação de preço
    produto_nome = "iPhone 15 Pro"
    preco_atual = 6500.00
    preco_meta = 7000.00
    
    print(f"\n🔍 Verificando preço de {produto_nome}...")
    print(f"   Preço atual: R$ {preco_atual:.2f}")
    print(f"   Preço meta: R$ {preco_meta:.2f}")
    
    # Disparar alerta (como o preço está abaixo da meta)
    if notificador.verificar_alerta(produto_nome, preco_atual, preco_meta):
        print("\n✅ Alerta disparado com sucesso!")
        print("📁 Alerta também foi salvo em 'alertas_preco.log'")
    else:
        print("\n⏳ Preço não atingiu a meta.")


def exemplo_email():
    """Exemplo de envio de email (requer configuração)"""
    
    print("\n" + "="*60)
    print("EXEMPLO 3: Envio de Email (Requer Configuração)")
    print("="*60 + "\n")
    
    # ⚠️ CONFIGURE SEUS DADOS ANTES DE EXECUTAR
    email_origem = "seu@gmail.com"
    app_password = "sua-app-password"  # Gere em myaccount.google.com/apppasswords
    email_destino = "destinatario@email.com"
    
    if email_origem == "seu@gmail.com":
        print("⚠️  Configure suas credenciais de email antes de executar este exemplo.")
        print("📖 Instruções:")
        print("   1. Acesse https://myaccount.google.com/apppasswords")
        print("   2. Gere uma 'App Password' para sua conta Gmail")
        print("   3. Substitua os valores acima")
        return
    
    notificador = NotificadorPreco()
    
    print("\n📧 Enviando email de notificação...")
    
    try:
        notificador.enviar_email_smtp(
            email_origem=email_origem,
            senha=app_password,
            email_destino=email_destino,
            produto_nome="Samsung Galaxy S23",
            preco_atual=2000.00,
            preco_meta=2500.00
        )
        print("✅ Email enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")


def exemplo_historico():
    """Exemplo de visualização de histórico"""
    
    print("\n" + "="*60)
    print("EXEMPLO 4: Histórico de Preços")
    print("="*60 + "\n")
    
    db_url = "postgresql://postgres:postgres@localhost:5432/price_tracker"
    tracker = PriceTracker(db_url)
    
    if not tracker.conectar():
        print("❌ Falha ao conectar.")
        return
    
    # Obter todos os produtos
    produtos = tracker.obter_produtos()
    
    if not produtos:
        print("📌 Nenhum produto cadastrado.")
        return
    
    # Mostrar histórico do primeiro produto
    produto = produtos[0]
    print(f"\n📊 Histórico de preços para: {produto.nome}")
    print("-" * 60)
    
    historico = tracker.obter_historico(produto.id, limitar=10)
    
    if historico:
        for h in reversed(historico):
            print(f"  {h.data_consulta.strftime('%d/%m/%Y %H:%M:%S')} - R$ {h.preco:.2f}")
    else:
        print("  Nenhum registro de preço encontrado.")


def main():
    """Executar todos os exemplos"""
    
    print("\n" + "🚀 "*30)
    print("EXEMPLOS DE USO - PRICE TRACKER")
    print("🚀 "*30)
    
    try:
        # Exemplo 1: Uso básico
        exemplo_basico()
        
        # Exemplo 2: Notificações
        exemplo_notificacoes()
        
        # Exemplo 3: Email (comentado por padrão)
        # exemplo_email()
        
        # Exemplo 4: Histórico
        exemplo_historico()
        
        print("\n" + "="*60)
        print("✅ EXEMPLOS CONCLUÍDOS COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        logger.error(f"Erro: {e}", exc_info=True)


if __name__ == "__main__":
    main()
