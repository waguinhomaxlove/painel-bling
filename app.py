from flask import Flask, render_template, request, redirect, session, url_for
import requests
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'chave-secreta'

CLIENT_ID = 'c0588a73f49371b037d8bb333c059e29406c7850'
CLIENT_SECRET = 'ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2'
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'

# Conexão com o banco de dados SQLite
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
            return 'Login falhou. Verifique o email e a senha.'
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

@app.route('/adicionar', methods=['POST'])
def adicionar():
    sku = request.form['sku']
    nome = request.form['nome']
    estoque = request.form['estoque']
    preco = request.form['preco']
    preco_custo = request.form['custo']
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, preco_custo) VALUES (?, ?, ?, ?, ?)',
                 (sku, nome, estoque, preco, preco_custo))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/auth')
def auth():
    state = str(uuid.uuid4())
    session['state'] = state
    return redirect(
        f"https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}"
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        return "Erro: código de autorização não encontrado."

    if state != session.get('state'):
        return "Erro: state token inválido."

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    token_response = requests.post("https://www.bling.com.br/Api/v3/oauth/token", headers=headers, data=data)
    if token_response.status_code != 200:
        return f"Erro ao obter token Bling.\nStatus: {token_response.status_code}\n\n{token_response.text}"

    session['bling_token'] = token_response.json().get('access_token')
    return redirect(url_for('produtos_bling'))

@app.route('/produtos-bling')
def produtos_bling():
    token = session.get('bling_token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = "https://api.bling.com.br/v3/produtos?expand=produtos.produto"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Erro ao buscar produtos do Bling: {response.text}"

    data = response.json()
    produtos = []

    try:
        for item in data.get("data", []):
            produto_data = item.get("produto", {})
            produtos.append({
                "codigo": produto_data.get("codigo", ""),
                "nome": produto_data.get("nome", ""),
                "estoqueAtual": produto_data.get("estoqueAtual", 0),
                "preco": produto_data.get("preco", 0.0)
            })
    except Exception as e:
        return f"Erro ao processar produtos: {str(e)}"

    return render_template("produtos_bling.html", produtos=produtos)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)


@app.route('/excluir/<sku>')
def excluir(sku):
    conn = get_db_connection()
    conn.execute('DELETE FROM produtos WHERE sku = ?', (sku,))
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
