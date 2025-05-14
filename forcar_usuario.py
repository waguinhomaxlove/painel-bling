import sqlite3
conn = sqlite3.connect('painel.db')
cursor = conn.cursor()
cursor.execute("UPDATE usuarios SET senha = ? WHERE usuario = ?", ('nova_senha', 'admin'))
conn.commit()
conn.close()