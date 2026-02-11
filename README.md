# 💰 Price Tracker - Monitor de Preços de Produtos

Um aplicativo profissional e escalável para monitorar preços de produtos em e-commerce, com alertas inteligentes e visualização de histórico em tempo real.

## 📋 Características

✨ **Funcionalidades Principais:**
- 📊 Dashboard interativo com gráficos de preços
- 🔍 Scraping automático de preços em sites de e-commerce
- 🎯 Sistema de alertas quando preço atinge meta
- 📈 Histórico completo de variação de preços
- 💌 Notificações por email (SMTP ou SendGrid)
- 🌐 Interface web intuitiva com Streamlit
- 🐳 Containerização com Docker e Docker Compose
- 📱 Design responsivo e moderno

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11+** - Linguagem principal
- **SQLAlchemy** - ORM para gerenciamento do banco de dados
- **BeautifulSoup4** - Web scraping e parsing HTML
- **Requests** - Requisições HTTP

### Banco de Dados
- **PostgreSQL 16** - Banco de dados robusto e confiável

### Frontend
- **Streamlit** - Framework para interface web interativa
- **Plotly** - Visualizações gráficas dinâmicas
- **Pandas** - Manipulação e análise de dados

### Infraestrutura
- **Docker** - Containerização da aplicação
- **Docker Compose** - Orquestração de containers

### Integrações Opcionais
- **SendGrid** - Serviço de email em massa
- **SMTP (Gmail)** - Envio de notificações por email

## 📦 Pré-requisitos

### Instalação Local
- Python 3.11+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

### Com Docker
- Docker
- Docker Compose

## 🚀 Guia de Instalação

### Opção 1: Instalação com Docker (Recomendado)

1. **Clone ou baixe o projeto:**
```bash
cd price-tracker
```

2. **Inicie os containers:**
```bash
docker-compose up -d
```

3. **Acesse a aplicação:**
- Interface Web: [http://localhost:8501](http://localhost:8501)
- Banco de Dados: `localhost:5432`

Para parar a aplicação:
```bash
docker-compose down
```

### Opção 2: Instalação Local

1. **Crie um ambiente virtual:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o PostgreSQL:**
```bash
# Criar banco de dados
psql -U postgres -c "CREATE DATABASE price_tracker;"

# Executar script SQL
psql -U postgres -d price_tracker -f init.sql
```

4. **Configure as variáveis de ambiente:**
Crie um arquivo `.env`:
```
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=price_tracker
```

5. **Inicie a aplicação:**
```bash
streamlit run main.py
```

A aplicação estará disponível em [http://localhost:8501](http://localhost:8501)

## 📖 Como Usar

### 1. Adicionar Produto
1. Clique em **"➕ Adicionar Produto"**
2. Preenchea:
   - Nome do produto
   - URL do site
   - Preço meta (valor para alerta)
3. Clique em **"✅ Adicionar Produto"**

### 2. Monitorar Preços
1. Vá para **"👁️ Monitorar Preço"**
2. Selecione um ou mais produtos
3. Clique em **"🔄 Atualizar Preços"**
4. Sistema extrairá os preços automaticamente

### 3. Visualizar Dashboard
1. Acesse **"📊 Dashboard"**
2. Selecione um produto
3. Visualize:
   - Gráfico de evolução de preços
   - Estatísticas (mínimo, máximo, média)
   - Status de alerta

### 4. Gerenciar Produtos
1. Vá para **"📋 Gerenciar Produtos"**
2. Visualize todos os produtos cadastrados
3. Delete produtos conforme necessário

## 🔧 Configuração Avançada

### Integração com SendGrid

1. **Obter chave API:**
   - Acesse [SendGrid](https://sendgrid.com)
   - Crie uma conta e gere uma API Key

2. **Usar no código:**
```python
from notificador import NotificadorPreco

notificador = NotificadorPreco(sendgrid_api_key='sua-chave-api')
notificador.enviar_sendgrid(
    email_destino='seu@email.com',
    produto_nome='Samsung Galaxy S23',
    preco_atual=2499.99,
    preco_meta=2000.00
)
```

### Integração com Email (SMTP Gmail)

1. **Gerar App Password:**
   - Ative 2FA na sua conta Google
   - Gere uma "App Password" em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

2. **Usar no código:**
```python
from notificador import NotificadorPreco

notificador = NotificadorPreco()
notificador.enviar_email_smtp(
    email_origem='seu@gmail.com',
    senha='sua-app-password',
    email_destino='destinatario@email.com',
    produto_nome='Samsung Galaxy S23',
    preco_atual=2499.99,
    preco_meta=2000.00
)
```

### Customizar Seletores CSS

Alguns sites podem ter estrutura HTML diferentes. Para customizar o seletor de preço:

```python
tracker.monitorar_preco(
    produto_id=1,
    seletor_css='.product-price'  # Seletor customizado
)
```

Para encontrar o seletor correto:
1. Abra a página do produto
2. Pressione F12 (DevTools)
3. Inspecione o elemento de preço
4. Copie o seletor CSS

## 📊 Estrutura do Banco de Dados

### Tabela: `produtos`
```sql
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    preco_meta DECIMAL(10, 2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `historico_precos`
```sql
CREATE TABLE historico_precos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    preco DECIMAL(10, 2) NOT NULL,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🏗️ Estrutura de Arquivos

```
price-tracker/
├── main.py                 # Aplicação Streamlit (interface web)
├── tracker.py              # Classe PriceTracker e models SQLAlchemy
├── notificador.py          # Sistema de alertas e notificações
├── init.sql                # Script de inicialização do banco de dados
├── requirements.txt        # Dependências Python
├── Dockerfile              # Container Python
├── docker-compose.yml      # Orquestração de containers
├── README.md               # Este arquivo
└── .env                    # Variáveis de ambiente (não versionado)
```

## 🔐 Segurança

⚠️ **Importante:**
- Nunca compartilhe suas credenciais de banco de dados
- Use variáveis de ambiente para configurações sensíveis
- Altere as senhas padrão antes de usar em produção
- Use secrets management em ambientes corporativos

## 🐛 Troubleshooting

### Erro: "Connection refused"
**Solução:** Verifique se o PostgreSQL está rodando
```bash
# Docker
docker-compose logs postgres

# Local
sudo service postgresql status
```

### Erro: "Module not found"
**Solução:** Instale as dependências
```bash
pip install -r requirements.txt
```

### Erro: "No module named 'streamlit'"
**Solução:** Ative o ambiente virtual
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Preço não é extraído corretamente
**Solução:** Customize o seletor CSS:
1. Inspecione o código HTML da página
2. Encontre o seletor CSS do elemento de preço
3. Use o parâmetro `seletor_css` na função

## 📝 Exemplo de Uso Programático

```python
from tracker import PriceTracker
from notificador import NotificadorPreco

# Inicializar tracker
db_url = "postgresql://postgres:postgres@localhost:5432/price_tracker"
tracker = PriceTracker(db_url)
tracker.conectar()
tracker.criar_tabelas()

# Adicionar produto
produto = tracker.adicionar_produto(
    nome="iPhone 15 Pro",
    url="https://exemplo.com/iphone-15",
    preco_meta=7000.00
)

# Monitorar preço
historico = tracker.monitorar_preco(produto.id)

# Verificar alerta
notificador = NotificadorPreco()
if historico:
    preco_atual = float(historico.preco)
    preco_meta = float(produto.preco_meta)
    
    if notificador.verificar_alerta(
        produto_nome=produto.nome,
        preco_atual=preco_atual,
        preco_meta=preco_meta
    ):
        print("🎉 Alerta disparado!")
```

## 🚢 Deploy em Produção

### Opção 1: AWS EC2 com Docker
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clonar projeto e iniciar
git clone seu-repo
cd price-tracker
docker-compose up -d
```

### Opção 2: Heroku
```bash
heroku create sua-app
git push heroku main
```

### Opção 3: DigitalOcean
```bash
# Usar Docker com DigitalOcean App Platform
# Conectar repo do GitHub e deploy automático
```

## 📞 Suporte e Contribuições

Se encontrou um bug ou tem sugestões:
1. Abra uma issue no GitHub
2. Descreva o problema detalhadamente
3. Inclua exemplos de código se possível

## 📄 Licença

Este projeto é licenciado sob a MIT License - veja LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido como ferramenta de monitoramento de preços inteligente.

---

**Dúvidas?** Consulte a documentação ou abra uma issue! 🚀
