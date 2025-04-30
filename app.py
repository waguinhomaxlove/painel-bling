
import os
import sqlite3
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect, session, url_for, send_file
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'chave-secreta'

# CREDENCIAIS BLING FIXAS
CLIENT_ID = "c0588a73f49371b037d8bb333c059e29406c7850"
CLIENT_SECRET = "ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2"
REDIRECT_URI = "https://painel-bling.onrender.com/callback"

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
    busca = request.args.get("busca", "")
    conn = get_db_connection()
    if busca:
        produtos = conn.execute("SELECT * FROM produtos WHERE sku LIKE ? OR nome LIKE ?", 
                                (f"%{busca}%", f"%{busca}%")).fetchall()
    else:
        produtos = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return render_template("dashboard.html", produtos=produtos, busca=busca)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    sku = request.form['sku']
    nome = request.form['nome']
    estoque = request.form['estoque']
    preco = request.form['preco']
    preco_custo = request.form['custo']
    ultima_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, preco_custo, ultima_atualizacao) VALUES (?, ?, ?, ?, ?, ?)',
                 (sku, nome, estoque, preco, preco_custo, ultima_atualizacao))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/editar/<sku>', methods=['GET', 'POST'])
def editar(sku):
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        estoque = request.form['estoque']
        preco = request.form['preco']
        preco_custo = request.form['preco_custo']
        ultima_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("UPDATE produtos SET nome = ?, estoque = ?, preco = ?, preco_custo = ?, ultima_atualizacao = ? WHERE sku = ?",
                     (nome, estoque, preco, preco_custo, ultima_atualizacao, sku))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    produto = conn.execute("SELECT * FROM produtos WHERE sku = ?", (sku,)).fetchone()
    conn.close()
    return render_template("editar.html", produto=produto)

@app.route('/excluir/<sku>')
def excluir(sku):
    conn = get_db_connection()
    conn.execute("DELETE FROM produtos WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    if request.method == 'POST':
        try:
            valor_dolar = float(request.form['valor_dolar'])
            dolar = 5.90
            importador = 0.15
            imposto = 0.10
            mktplace = 0.18
            lucro = 0.15
            custo_total = valor_dolar * dolar * (1 + importador + imposto)
            preco_final = custo_total / (1 - mktplace - lucro)
            resultado = round(preco_final, 2)
        except:
            resultado = 'Erro no cálculo'
    return render_template("calculadora.html", resultado=resultado)

@app.route('/exportar')
def exportar():
    conn = get_db_connection()
    produtos = conn.execute('SELECT sku, nome, estoque, preco, preco_custo, ultima_atualizacao FROM produtos').fetchall()
    conn.close()
    df = pd.DataFrame(produtos, columns=['sku', 'nome', 'estoque', 'preco', 'preco_custo', 'ultima_atualizacao'])
    caminho = "produtos_exportados.xlsx"
    df.to_excel(caminho, index=False)
    return send_file(caminho, as_attachment=True)

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)', (email, senha))
        conn.commit()
    usuarios = conn.execute('SELECT id, email FROM usuarios').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/auth')
def auth():
    state = str(uuid.uuid4())
    session['bling_auth_state'] = state
    url = f"https://www.bling.com.br/autorizar-app?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&state={state}"
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state or state != session.get('bling_auth_state'):
        return "Erro: código de autorização ou estado inválido."

    url = "https://www.bling.com.br/Api/v3/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        return f"Erro ao obter token Bling.<br><br>Status: {response.status_code}<br><br>{response.text}"

    token = response.json().get("access_token")
    session["bling_token"] = token
    return redirect(url_for("produtos_bling"))

@app.route('/produtos-bling')
def produtos_bling():
    token = session.get('bling_token')
    if not token:
        return redirect(url_for('auth'))

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)
    if response.status_code != 200:
        return f"Erro ao buscar produtos do Bling: <br><br>{response.text}"

    data = response.json()
    produtos = []
    if 'data' in data:
        for item in data['data']:
            produto = item.get('produto', {})
            produtos.append({
                'codigo': produto.get('codigo', ''),
                'nome': produto.get('nome', ''),
                'estoqueAtual': produto.get('estoqueAtual', 0),
                'preco': produto.get('preco', '0.00')
            })
    return render_template("produtos_bling.html", produtos=produtos)

port = int(os.environ.get('PORT', 10000))
app.run(debug=True, host='0.0.0.0', port=port)
