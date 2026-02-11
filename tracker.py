import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Definição das models
Base = declarative_base()


class Produto(Base):
    """Model para tabela de produtos"""
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    preco_meta = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com histórico
    historicos = relationship('HistoricoPreco', back_populates='produto', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}', preco_meta={self.preco_meta})>"


class HistoricoPreco(Base):
    """Model para tabela de histórico de preços"""
    __tablename__ = 'historico_precos'

    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id', ondelete='CASCADE'), nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)
    data_consulta = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com produto
    produto = relationship('Produto', back_populates='historicos')

    def __repr__(self):
        return f"<HistoricoPreco(id={self.id}, produto_id={self.produto_id}, preco={self.preco})>"


class PriceTracker:
    """Classe para rastrear preços de produtos em e-commerce"""

    def __init__(self, db_url: str):
        """
        Inicializar o tracker com a URL do banco de dados
        
        Args:
            db_url: URL de conexão PostgreSQL (ex: postgresql://user:password@localhost/dbname)
        """
        self.db_url = db_url
        self.engine = None
        self.Session = None
        logger.info("PriceTracker inicializado")

    def conectar(self) -> bool:
        """
        Estabelecer conexão com o banco de dados PostgreSQL
        
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        try:
            self.engine = create_engine(self.db_url, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Testar a conexão
            with self.engine.connect() as connection:
                logger.info("✓ Conectado ao banco de dados PostgreSQL com sucesso")
                return True
        except Exception as e:
            logger.error(f"✗ Erro ao conectar ao banco de dados: {e}")
            return False

    def criar_tabelas(self):
        """Criar as tabelas no banco de dados se não existirem"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✓ Tabelas criadas/verificadas com sucesso")
        except Exception as e:
            logger.error(f"✗ Erro ao criar tabelas: {e}")

    def adicionar_produto(self, nome: str, url: str, preco_meta: float) -> Optional[Produto]:
        """
        Adicionar novo produto ao banco de dados
        
        Args:
            nome: Nome do produto
            url: URL do produto
            preco_meta: Preço meta para alerta
            
        Returns:
            Produto: Objeto do produto criado, ou None se falhar
        """
        session = self.Session()
        try:
            produto = Produto(
                nome=nome,
                url=url,
                preco_meta=Decimal(str(preco_meta))
            )
            session.add(produto)
            session.commit()
            logger.info(f"✓ Produto '{nome}' adicionado com sucesso (ID: {produto.id})")
            return produto
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Erro ao adicionar produto: {e}")
            return None
        finally:
            session.close()

    def obter_produtos(self) -> List[Produto]:
        """
        Obter todos os produtos cadastrados
        
        Returns:
            List[Produto]: Lista de todos os produtos
        """
        session = self.Session()
        try:
            produtos = session.query(Produto).all()
            return produtos
        except Exception as e:
            logger.error(f"✗ Erro ao obter produtos: {e}")
            return []
        finally:
            session.close()

    def obter_produto_por_id(self, produto_id: int) -> Optional[Produto]:
        """
        Obter produto específico por ID
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Produto: Objeto do produto ou None
        """
        session = self.Session()
        try:
            produto = session.query(Produto).filter(Produto.id == produto_id).first()
            return produto
        except Exception as e:
            logger.error(f"✗ Erro ao obter produto: {e}")
            return None
        finally:
            session.close()

    def extrair_preco(self, url: str, seletor_css: str = None) -> Optional[float]:
        """
        Extrair preço de um URL usando BeautifulSoup
        
        Args:
            url: URL do produto
            seletor_css: Seletor CSS para encontrar o preço (ex: '.price', '#current-price')
                        Se None, tenta detectar automaticamente
            
        Returns:
            float: Preço encontrado, ou None se não conseguir extrair
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Se um seletor foi fornecido, usar esse
            if seletor_css:
                elemento = soup.select_one(seletor_css)
                if elemento:
                    preco_text = elemento.get_text(strip=True)
                    return self._extrair_valor_numerico(preco_text)
            
            # Tentar encontrar automaticamente elementos de preço comuns
            seletores_comuns = [
                '.price', '.current-price', '#current-price',
                '[data-price]', '.product-price', '.preco',
                'span[class*="price"]', 'div[class*="price"]'
            ]
            
            for seletor in seletores_comuns:
                elemento = soup.select_one(seletor)
                if elemento:
                    preco_text = elemento.get_text(strip=True)
                    preco = self._extrair_valor_numerico(preco_text)
                    if preco:
                        logger.info(f"✓ Preço extraído: R$ {preco}")
                        return preco
            
            logger.warning(f"⚠ Não foi possível extrair o preço de {url}")
            return None
            
        except Exception as e:
            logger.error(f"✗ Erro ao extrair preço de {url}: {e}")
            return None

    @staticmethod
    def _extrair_valor_numerico(texto: str) -> Optional[float]:
        """
        Extrair valor numérico de uma string contendo preço
        
        Args:
            texto: String com preço (ex: "R$ 49,99", "$99.99", "99.99")
            
        Returns:
            float: Valor numérico encontrado
        """
        import re
        
        # Remove moedas e caracteres não numéricos exceto . e ,
        limpo = re.sub(r'[^\d.,]', '', texto)
        
        # Determinar se usa vírgula ou ponto como separador decimal
        if ',' in limpo and '.' in limpo:
            # Ambos existem - usar o último como decimal
            if limpo.rfind(',') > limpo.rfind('.'):
                limpo = limpo.replace('.', '').replace(',', '.')
            else:
                limpo = limpo.replace(',', '')
        elif ',' in limpo:
            # Apenas vírgula - converter para ponto
            limpo = limpo.replace(',', '.')
        
        try:
            return float(limpo)
        except ValueError:
            return None

    def monitorar_preco(self, produto_id: int, seletor_css: str = None) -> Optional[HistoricoPreco]:
        """
        Monitorar o preço atual de um produto e salvar no banco de dados
        
        Args:
            produto_id: ID do produto a monitorar
            seletor_css: Seletor CSS customizado para extrair o preço
            
        Returns:
            HistoricoPreco: Registro criado, ou None se falhar
        """
        session = self.Session()
        try:
            produto = session.query(Produto).filter(Produto.id == produto_id).first()
            
            if not produto:
                logger.error(f"✗ Produto com ID {produto_id} não encontrado")
                return None
            
            logger.info(f"📊 Monitorando preço de: {produto.nome}")
            preco_atual = self.extrair_preco(produto.url, seletor_css)
            
            if preco_atual is None:
                logger.warning(f"⚠ Não foi possível extrair preço para {produto.nome}")
                return None
            
            # Criar registro no histórico
            historico = HistoricoPreco(
                produto_id=produto_id,
                preco=Decimal(str(preco_atual))
            )
            session.add(historico)
            session.commit()
            
            logger.info(f"✓ Preço salvo: R$ {preco_atual} para {produto.nome}")
            return historico
            
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Erro ao monitorar preço: {e}")
            return None
        finally:
            session.close()

    def obter_historico(self, produto_id: int, limitar: int = None) -> List[HistoricoPreco]:
        """
        Obter histórico de preços de um produto
        
        Args:
            produto_id: ID do produto
            limitar: Número máximo de registros a retornar
            
        Returns:
            List[HistoricoPreco]: Lista de registros históricos
        """
        session = self.Session()
        try:
            query = session.query(HistoricoPreco).filter(
                HistoricoPreco.produto_id == produto_id
            ).order_by(HistoricoPreco.data_consulta.desc())
            
            if limitar:
                query = query.limit(limitar)
            
            return query.all()
        except Exception as e:
            logger.error(f"✗ Erro ao obter histórico: {e}")
            return []
        finally:
            session.close()

    def deletar_produto(self, produto_id: int) -> bool:
        """
        Deletar um produto e seu histórico
        
        Args:
            produto_id: ID do produto a deletar
            
        Returns:
            bool: True se deletado com sucesso
        """
        session = self.Session()
        try:
            produto = session.query(Produto).filter(Produto.id == produto_id).first()
            if produto:
                session.delete(produto)
                session.commit()
                logger.info(f"✓ Produto {produto_id} deletado com sucesso")
                return True
            else:
                logger.warning(f"⚠ Produto {produto_id} não encontrado")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Erro ao deletar produto: {e}")
            return False
        finally:
            session.close()
