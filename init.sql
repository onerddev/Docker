-- Criar tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    preco_meta DECIMAL(10, 2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de histórico de preços
CREATE TABLE IF NOT EXISTS historico_precos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

-- Criar índice para melhor performance nas consultas
CREATE INDEX IF NOT EXISTS idx_historico_produto_data 
ON historico_precos(produto_id, data_consulta DESC);
