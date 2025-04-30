
import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'chave-secreta'

def get_db_connection():
    conn = sqlite3.connect('painel.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
        if user:
            session['usuario'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Login falhou. Verifique o email e a senha.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template("dashboard.html", produtos=produtos)

@app.route('/produtos-calculo', methods=['GET'])
def produtos_calculo():
    token = session.get('bling_token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)

    if response.status_code != 200:
        return f"Erro ao buscar produtos do Bling: {response.status_code} - {response.text}"

    data = response.json()
    produtos = []

    if 'data' in data:
        for item in data['data']:
            produto = item.get('produto', {})
            produtos.append({
                'codigo': produto.get('codigo', ''),
                'nome': produto.get('nome', ''),
                'estoqueAtual': produto.get('estoqueAtual', 0),
                'preco': produto.get('preco', 0.0)
            })

    return render_template("produtos_bling_calculo.html", produtos=produtos)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
