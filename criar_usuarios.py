import sqlite3
from werkzeug.security import generate_password_hash

# Conectar ao banco de dados existente
conn = sqlite3.connect("painel.db")
cursor = conn.cursor()

# Criar a tabela de usuários, se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (  -- Corrigido para 'usuarios'
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL  -- Alterado para 'senha' para consistência
)
''')

# Função para criar um usuário (exemplo)
def criar_usuario(email, senha):
    senha_hash = generate_password_hash(senha)
    cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha_hash))
    conn.commit()

# Criar um usuário de exemplo (remova ou comente após o primeiro uso)
#criar_usuario("teste@email.com", "senha123")  # Crie um usuário inicial!

conn.commit()
conn.close()

print("Tabela 'usuarios' criada com sucesso!")