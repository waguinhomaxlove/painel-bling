import sqlite3

conn = sqlite3.connect('painel.db')
cursor = conn.cursor()

# Substitua pelos dados desejados
nome = 'Admin'
email = 'admin@email.com'
senha = '123456'

cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
conn.commit()
conn.close()

print("Usuário inserido com sucesso!")
