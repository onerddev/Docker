# Docker

Aplicação backend para monitoramento de preços de produtos em e-commerce, com armazenamento de histórico e sistema de alertas.

---

## 1. Visão Geral

O sistema permite:

- Cadastro de produtos para monitoramento
- Extração automática de preços via scraping
- Armazenamento de histórico de preços
- Disparo de alertas quando o valor atinge a meta definida
- Execução via Docker ou instalação local

A aplicação funciona como serviço backend e pode ser integrada a outros sistemas.

---

## 2. Tecnologias Utilizadas

### Backend
- Python 3.11+
- SQLAlchemy
- BeautifulSoup4
- Requests

### Banco de Dados
- PostgreSQL 16

### Infraestrutura
- Docker
- Docker Compose

### Integrações Opcionais
- SendGrid
- SMTP (Gmail)

---

## 3. Pré-requisitos

### Execução Local
- Python 3.11 ou superior
- PostgreSQL 12 ou superior
- pip

### Execução com Docker
- Docker
- Docker Compose

---

## 4. Instalação

### 4.1 Instalação com Docker (Recomendado)

1. Acesse o diretório do projeto:

```bash
cd docker
```

2. Inicie os containers:

```bash
docker-compose up -d
```

3. Verifique os logs:

```bash
docker-compose logs -f
```

Para parar:

```bash
docker-compose down
```

---

### 4.2 Instalação Local

#### 1. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

#### 3. Criar banco de dados

```bash
psql -U postgres -c "CREATE DATABASE docker;"
psql -U postgres -d docker -f init.sql
```

#### 4. Configurar variáveis de ambiente

Criar arquivo `.env`:

```
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=docker
```

#### 5. Executar aplicação

```bash
python main.py
```

---

## 5. Estrutura do Banco de Dados

### Tabela produtos

```sql
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    preco_meta DECIMAL(10,2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela historico_precos

```sql
CREATE TABLE historico_precos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    preco DECIMAL(10,2) NOT NULL,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Estrutura do Projeto

```
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
```

---

## 7. Exemplo de Uso Programático

```python
from tracker import PriceTracker
from notificador import NotificadorPreco

db_url = "postgresql://postgres:postgres@localhost:5432/docker"

tracker = PriceTracker(db_url)
tracker.conectar()
tracker.criar_tabelas()

produto = tracker.adicionar_produto(
    nome="Produto Teste",
    url="exemplo.com/produto",
    preco_meta=500.00
)

historico = tracker.monitorar_preco(produto.id)

notificador = NotificadorPreco()

if historico:
    preco_atual = float(historico.preco)
    preco_meta = float(produto.preco_meta)

    if notificador.verificar_alerta(
        produto_nome=produto.nome,
        preco_atual=preco_atual,
        preco_meta=preco_meta
    ):
        print("Alerta disparado")
```

---

## 8. Integração com Email

### SendGrid

Criar conta em:

sendgrid.com

Exemplo:

```python
from notificador import NotificadorPreco

notificador = NotificadorPreco(sendgrid_api_key='sua-chave-api')

notificador.enviar_sendgrid(
    email_destino='email@dominio.com',
    produto_nome='Produto',
    preco_atual=1000.00,
    preco_meta=800.00
)
```

### SMTP Gmail

Gerar App Password em:

myaccount.google.com/apppasswords

Exemplo:

```python
notificador.enviar_email_smtp(
    email_origem='email@gmail.com',
    senha='app-password',
    email_destino='destinatario@dominio.com',
    produto_nome='Produto',
    preco_atual=1000.00,
    preco_meta=800.00
)
```

---

## 9. Segurança

- Não versionar o arquivo .env
- Não compartilhar credenciais
- Alterar senhas padrão em produção
- Utilizar gerenciamento de secrets em ambiente corporativo

---

## 10. Licença

MIT License
