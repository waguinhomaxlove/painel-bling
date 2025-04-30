
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
            return render_template("login.html", erro="Login falhou. Verifique o email e a senha.")
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

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    detalhes = {}
    if request.method == 'POST':
        try:
            valor_dolar = float(request.form['valor_dolar'])
            dolar = 5.90
            fornecedor = 0.15
            imposto = 0.10
            mktplace = 0.18
            lucro = 0.15

            custo_total = valor_dolar * dolar * (1 + fornecedor + imposto)
            preco_final = custo_total / (1 - mktplace - lucro)
            resultado = round(preco_final, 2)

            detalhes = {
                "valor_dolar": valor_dolar,
                "custo_total": round(custo_total, 2),
                "preco_final": resultado,
                "cotacao": dolar,
                "fornecedor": fornecedor,
                "imposto": imposto,
                "marketplace": mktplace,
                "lucro": lucro
            }

        except Exception as e:
            resultado = 'Erro no cálculo'
    return render_template("calculadora.html", resultado=resultado, detalhes=detalhes)

@app.route('/usuarios')
def usuarios():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT id, nome, email FROM usuarios').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

