import sqlite3

# Conectar ao banco de dados existente
conn = sqlite3.connect("painel.db")
cursor = conn.cursor()

# Criar a tabela de usuários, se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Tabela 'users' criada com sucesso!")
