import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('painel.db')
cursor = conn.cursor()

# Criar um usuário admin
email = "admin@painel.com"
senha = "123456"
nome = "Admin"

# Inserir o usuário
cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
conn.commit()
conn.close()

print("✅ Usuário admin criado com sucesso!")
