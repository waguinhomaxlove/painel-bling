import sqlite3

conn = sqlite3.connect('painel.db')

conn.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        nome TEXT NOT NULL,
        estoque INTEGER,
        preco NUMERIC,
        preco_custo NUMERIC,
        ultima_atualizacao TEXT
    );
''')

conn.commit()
conn.close()

print("✅ Banco e tabela criados com sucesso!")
