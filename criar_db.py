import sqlite3
conn = sqlite3.connect('painel.db')
cursor = conn.cursor()
# Criação de tabela exemplo
cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT)')
conn.commit()
conn.close()