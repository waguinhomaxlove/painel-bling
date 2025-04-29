import sqlite3

conn = sqlite3.connect('painel.db')
cursor = conn.cursor()

# Insere usuário padrão (altere conforme necessário)
email = "admin@painel.com"
senha = "123456"

cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
conn.commit()
conn.close()

print(f"Usuário criado: {email}")
