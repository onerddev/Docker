import logging
from decimal import Decimal
from typing import Optional, Callable
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificadorPreco:
    """Gerenciador de notificações de alerta de preço"""

    def __init__(self, sendgrid_api_key: Optional[str] = None):
        """
        Inicializar o notificador
        
        Args:
            sendgrid_api_key: Chave API do SendGrid (opcional)
        """
        self.sendgrid_api_key = sendgrid_api_key
        self.callbacks = []

    def registrar_callback(self, funcao: Callable):
        """
        Registrar uma função callback para ser chamada em alertas
        
        Args:
            funcao: Função que será chamada com (produto, preco, preco_meta)
        """
        self.callbacks.append(funcao)

    def verificar_alerta(self, produto_nome: str, preco_atual: float, 
                         preco_meta: float, produto_id: int = None) -> bool:
        """
        Verificar se o preço está abaixo da meta e disparar alerta
        
        Args:
            produto_nome: Nome do produto
            preco_atual: Preço atual
            preco_meta: Preço meta (alerta se <= preco_meta)
            produto_id: ID do produto (opcional)
            
        Returns:
            bool: True se alerta foi disparado, False caso contrário
        """
        if preco_atual <= preco_meta:
            self._disparar_alerta(produto_nome, preco_atual, preco_meta, produto_id)
            return True
        return False

    def _disparar_alerta(self, produto_nome: str, preco_atual: float, 
                         preco_meta: float, produto_id: int = None):
        """Disparar todos os tipos de alerta registrados"""
        
        # Alerta no console
        self._alerta_console(produto_nome, preco_atual, preco_meta)
        
        # Executar callbacks registrados
        for callback in self.callbacks:
            try:
                callback(produto_nome, preco_atual, preco_meta, produto_id)
            except Exception as e:
                logger.error(f"✗ Erro ao executar callback: {e}")

    @staticmethod
    def _alerta_console(produto_nome: str, preco_atual: float, preco_meta: float):
        """Exibir alerta no console"""
        diferenca = preco_meta - preco_atual
        percentual = (diferenca / preco_meta * 100) if preco_meta > 0 else 0
        
        alerta = f"""
╔════════════════════════════════════════════════════════════╗
║                    🎉 ALERTA DE PREÇO! 🎉                 ║
╠════════════════════════════════════════════════════════════╣
║  Produto: {produto_nome:<48}║
║  Preço Meta: R$ {preco_meta:<42} ║
║  Preço Atual: R$ {preco_atual:<41} ║
║  Economia: R$ {diferenca:.2f} ({percentual:.1f}%)         ║
║  Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S'):<36} ║
╚════════════════════════════════════════════════════════════╝
        """
        print(alerta)
        logger.warning(f"ALERTA: {produto_nome} atingiu o preço meta! R$ {preco_atual}")

    def enviar_email_smtp(self, email_origem: str, senha: str, 
                          email_destino: str, produto_nome: str, 
                          preco_atual: float, preco_meta: float,
                          smtp_server: str = 'smtp.gmail.com', 
                          smtp_port: int = 587):
        """
        Enviar notificação por email usando SMTP (Gmail)
        
        Args:
            email_origem: Email de origem (ex: seu_email@gmail.com)
            senha: Senha do email ou app password
            email_destino: Email de destino
            produto_nome: Nome do produto
            preco_atual: Preço atual
            preco_meta: Preço meta
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 Alerta de Preço: {produto_nome}"
            msg['From'] = email_origem
            msg['To'] = email_destino

            # Corpo do email em HTML
            corpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="background-color: white; border-radius: 8px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #27ae60; text-align: center;">🎉 Alerta de Preço Ativado!</h2>
                        
                        <div style="background-color: #ecf0f1; padding: 15px; border-radius: 4px; margin: 20px 0;">
                            <p><strong>Produto:</strong> {produto_nome}</p>
                            <p><strong>Preço Meta:</strong> <span style="color: #e74c3c; font-size: 18px;">R$ {preco_meta:.2f}</span></p>
                            <p><strong>Preço Atual:</strong> <span style="color: #27ae60; font-size: 18px;">R$ {preco_atual:.2f}</span></p>
                            <p><strong>Economia:</strong> R$ {preco_meta - preco_atual:.2f}</p>
                        </div>
                        
                        <p style="color: #7f8c8d; text-align: center; font-size: 12px;">
                            Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                        </p>
                    </div>
                </body>
            </html>
            """

            msg.attach(MIMEText(corpo_html, 'html'))

            # Conectar ao servidor SMTP e enviar
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_origem, senha)
                server.send_message(msg)

            logger.info(f"✓ Email enviado para {email_destino}")

        except Exception as e:
            logger.error(f"✗ Erro ao enviar email: {e}")

    def enviar_sendgrid(self, email_destino: str, produto_nome: str, 
                        preco_atual: float, preco_meta: float,
                        email_origem: str = 'noreply@pricetracker.com'):
        """
        Enviar notificação via SendGrid API
        
        Args:
            email_destino: Email de destino
            produto_nome: Nome do produto
            preco_atual: Preço atual
            preco_meta: Preço meta
            email_origem: Email de origem
        """
        if not self.sendgrid_api_key:
            logger.error("✗ Chave SendGrid não configurada")
            return False

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            msg = Mail(
                from_email=email_origem,
                to_emails=email_destino,
                subject=f"🎉 Alerta de Preço: {produto_nome}",
                html_content=f"""
                <html>
                    <body>
                        <h2>Alerta de Preço Ativado!</h2>
                        <p><strong>Produto:</strong> {produto_nome}</p>
                        <p><strong>Preço Meta:</strong> R$ {preco_meta:.2f}</p>
                        <p><strong>Preço Atual:</strong> R$ {preco_atual:.2f}</p>
                        <p><strong>Você está economizando:</strong> R$ {preco_meta - preco_atual:.2f}</p>
                    </body>
                </html>
                """
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(msg)
            logger.info(f"✓ Email SendGrid enviado para {email_destino}")
            return True

        except ImportError:
            logger.error("✗ Biblioteca sendgrid não instalada. Instale com: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"✗ Erro ao enviar email SendGrid: {e}")
            return False


# Funções auxiliares para callbacks
def criar_callback_email_smtp(email_origem: str, senha: str, email_destino: str):
    """Criar função callback para enviar email SMTP"""
    notificador = NotificadorPreco()
    
    def callback(produto_nome, preco_atual, preco_meta, produto_id=None):
        notificador.enviar_email_smtp(
            email_origem=email_origem,
            senha=senha,
            email_destino=email_destino,
            produto_nome=produto_nome,
            preco_atual=preco_atual,
            preco_meta=preco_meta
        )
    
    return callback


def criar_callback_log_arquivo(caminho_arquivo: str = 'alertas.log'):
    """Criar função callback para registrar alertas em arquivo"""
    
    def callback(produto_nome, preco_atual, preco_meta, produto_id=None):
        with open(caminho_arquivo, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {produto_nome} - "
                   f"Preço: R$ {preco_atual:.2f} (Meta: R$ {preco_meta:.2f})\n")
    
    return callback
