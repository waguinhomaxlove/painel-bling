import sqlite3

conn = sqlite3.connect('painel.db')
cursor = conn.cursor()

# Cria tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)
''')

# Cria tabela de produtos
cursor.execute('''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    nome TEXT NOT NULL,
    estoque INTEGER NOT NULL,
    preco REAL NOT NULL,
    preco_custo REAL NOT NULL
)
''')

conn.commit()
conn.close()

print("Banco de dados e tabelas criados com sucesso.")
