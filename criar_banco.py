import sqlite3

conn = sqlite3.connect('painel.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("Tabela 'usuarios' criada com sucesso.")
