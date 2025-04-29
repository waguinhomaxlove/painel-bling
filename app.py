import os
import sqlite3
import requests
import uuid
from flask import Flask, render_template, request, redirect, session, url_for, make_response

app = Flask(__name__)
app.secret_key = 'chave-secreta'

CLIENT_ID = "c0588a73f49371b037d8bb333c059e29406c7850"
CLIENT_SECRET = "ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2"
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'
TOKEN_URL = 'https://www.bling.com.br/Api/v3/oauth/token'

def get_db_connection():
    conn = sqlite3.connect('painel.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
        if user:
            session['usuario'] = email
            return redirect(url_for('dashboard'))
        else:
            erro = 'Login falhou. Verifique o email e a senha.'
    return render_template('login.html', erro=erro)

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

@app.route('/adicionar', methods=['POST'])
def adicionar():
    sku = request.form.get('sku')
    nome = request.form.get('nome')
    estoque = request.form.get('estoque')
    preco = request.form.get('preco')
    preco_custo = request.form.get('preco_custo')
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, preco_custo) VALUES (?, ?, ?, ?, ?)',
                 (sku, nome, estoque, preco, preco_custo))
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
        conn.execute('UPDATE produtos SET nome=?, estoque=?, preco=?, preco_custo=? WHERE sku=?',
                     (nome, estoque, preco, preco_custo, sku))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    produto = conn.execute('SELECT * FROM produtos WHERE sku=?', (sku,)).fetchone()
    conn.close()
    return render_template('editar.html', produto=produto)

@app.route('/excluir/<sku>')
def excluir(sku):
    conn = get_db_connection()
    conn.execute('DELETE FROM produtos WHERE sku = ?', (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    if request.method == 'POST':
        try:
            valor_dolar = float(request.form.get('valor_dolar', 0))
            dolar = 5.90
            importador = 0.15
            imposto = 0.10
            mktplace = 0.18
            lucro = 0.15
            custo_total = valor_dolar * dolar * (1 + importador + imposto)
            preco_final = custo_total / (1 - mktplace - lucro)
            resultado = round(preco_final, 2)
        except Exception as e:
            resultado = f'Erro no cálculo: {e}'
    return render_template("calculadora.html", resultado=resultado)

@app.route('/auth')
def auth():
    state = str(uuid.uuid4())
    session['auth_state'] = state
    url = (
        "https://www.bling.com.br/Api/v3/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code or not state:
        return "Erro: código de autorização ou estado ausente."

    if state != session.get('auth_state'):
        return "Erro: parâmetro de estado inválido."

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        session['bling_token'] = token_data.get('access_token')
        return redirect(url_for('produtos_bling'))

    return f"""
        <h2>Erro ao obter token Bling</h2>
        <p>Status: {response.status_code}</p>
        <pre>{response.text}</pre>
    """

@app.route('/produtos-bling')
def produtos_bling():
    token = session.get('bling_token')
    if not token:
        return redirect(url_for('auth'))
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)
    if response.status_code != 200:
        return "Erro ao buscar produtos do Bling: " + response.text
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

@app.route('/exportar')
def exportar():
    import pandas as pd
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    df = pd.DataFrame(produtos, columns=['sku', 'nome', 'estoque', 'preco', 'preco_custo', 'ultima_atualizacao'])
    output = make_response(df.to_csv(index=False))
    output.headers["Content-Disposition"] = "attachment; filename=produtos.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
