Docker

Aplicação para monitoramento de preços de produtos em e-commerce, com alertas inteligentes e visualização de histórico em tempo real.

Características

Funcionalidades principais:

Dashboard com gráficos de preços

Scraping automático de preços em sites de e-commerce

Sistema de alertas quando o preço atinge a meta

Histórico completo de variação de preços

Notificações por email (SMTP ou SendGrid)

Interface web com Streamlit

Containerização com Docker e Docker Compose

Design responsivo

Tecnologias Utilizadas
Backend

Python 3.11+

SQLAlchemy

BeautifulSoup4

Requests

Banco de Dados

PostgreSQL 16

Frontend

Streamlit

Plotly

Pandas

Infraestrutura

Docker

Docker Compose

Integrações Opcionais

SendGrid

SMTP (Gmail)

Pré-requisitos
Instalação Local

Python 3.11+

PostgreSQL 12+

pip

Com Docker

Docker

Docker Compose

Guia de Instalação
Opção 1: Docker (Recomendado)

Acesse a pasta do projeto:

cd docker


Inicie os containers:

docker-compose up -d


Acesse a aplicação:

Interface Web: http://localhost:8501

Banco de Dados: localhost:5432

Para parar:

docker-compose down

Opção 2: Instalação Local

Criar ambiente virtual:

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate


Instalar dependências:

pip install -r requirements.txt


Configurar PostgreSQL:

psql -U postgres -c "CREATE DATABASE docker;"

psql -U postgres -d docker -f init.sql


Criar arquivo .env:

DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=docker


Iniciar aplicação:

streamlit run main.py


Como Usar
Adicionar Produto

Clique em "Adicionar Produto"

Informe:

Nome do produto

URL do site

Preço meta

Confirme

Monitorar Preços

Acesse "Monitorar Preço"

Selecione produtos

Clique em atualizar

Dashboard

Acesse "Dashboard"

Selecione produto

Visualize:

Evolução de preços

Estatísticas

Status de alerta

Gerenciar Produtos

Acesse "Gerenciar Produtos"

Visualize ou exclua produtos

Integração SendGrid

Criar conta em:

sendgrid.com

Gerar API Key e usar:

from notificador import NotificadorPreco

notificador = NotificadorPreco(sendgrid_api_key='sua-chave-api')
notificador.enviar_sendgrid(
    email_destino='email@dominio.com',
    produto_nome='Produto',
    preco_atual=1000.00,
    preco_meta=800.00
)

Integração SMTP Gmail

Gerar App Password em:

myaccount.google.com/apppasswords

Exemplo:

from notificador import NotificadorPreco

notificador = NotificadorPreco()
notificador.enviar_email_smtp(
    email_origem='email@gmail.com',
    senha='app-password',
    email_destino='destinatario@dominio.com',
    produto_nome='Produto',
    preco_atual=1000.00,
    preco_meta=800.00
)

Estrutura do Banco de Dados
Tabela produtos
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    preco_meta DECIMAL(10,2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Tabela historico_precos
CREATE TABLE historico_precos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    preco DECIMAL(10,2) NOT NULL,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Estrutura de Arquivos
docker/
├── main.py
├── tracker.py
├── notificador.py
├── init.sql
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env

Segurança

Não compartilhe credenciais

Use variáveis de ambiente

Altere senhas padrão em produção

Utilize gerenciamento de secrets em ambiente corporativo

Troubleshooting
Connection refused
docker-compose logs postgres


ou

sudo service postgresql status

Module not found
pip install -r requirements.txt

Streamlit não encontrado

Ative o ambiente virtual antes de executar.

Exemplo Programático
from tracker import PriceTracker

db_url = "postgresql://postgres:postgres@localhost:5432/docker"

tracker = PriceTracker(db_url)
tracker.conectar()
tracker.criar_tabelas()

produto = tracker.adicionar_produto(
    nome="Produto Teste",
    url="exemplo.com/produto",
    preco_meta=500.00
)

tracker.monitorar_preco(produto.id)

Deploy
AWS EC2
sudo apt update && sudo apt upgrade -y

curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh

git clone seu-repositorio
cd docker
docker-compose up -d

Heroku
heroku create sua-app
git push heroku main

Licença

MIT License





