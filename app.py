import os
import sqlite3
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect, session, url_for, send_file
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'chave-secreta'
app.permanent_session_lifetime = timedelta(days=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

CLIENT_ID = '3bb72ea9e38004942c93ae0ec96ec05b5daab38e'
CLIENT_SECRET = '3646bd22edf0c28c8f6cf40aeb9b69910d1a16f61027330c193cb7bc10b7'
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'

def get_db_connection():
    conn = sqlite3.connect('painel.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
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
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Login falhou.')
    return render_template('login.html')

    @app.route('/produtos-calculo', methods=['GET'])
def produtos_calculo():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    token = session.get('bling_token')
    if not token:
        return redirect(url_for('login'))

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)
    if response.status_code != 200:
        return f"Erro ao buscar produtos do Bling: {response.text}", 400

    data = response.json()
    produtos = []

    if 'data' in data:
        for item in data['data']:
            produto = item.get('produto', {})
            produtos.append({
                'sku': produto.get('codigo', ''),
                'nome': produto.get('nome', ''),
                'estoque': produto.get('estoqueAtual', 0),
                'preco': produto.get('preco', '0.00')
            })

    return render_template("produtos_bling_calculo.html", produtos=produtos)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    busca = request.args.get('busca', '')
    conn = get_db_connection()
    if busca:
        produtos = conn.execute("SELECT * FROM produtos WHERE sku LIKE ? OR nome LIKE ?", (f'%{busca}%', f'%{busca}%')).fetchall()
    else:
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template("dashboard.html", produtos=produtos, busca=busca)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
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

@app.route('/editar/<sku>', methods=['GET', 'POST'])
def editar(sku):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        estoque = request.form['estoque']
        preco = request.form['preco']
        preco_custo = request.form['custo']
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
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM produtos WHERE sku=?', (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    detalhes = {}
    if request.method == 'POST':
        try:
            valor_dolar = float(request.form['valor_dolar'])
            dolar = 5.90
            comissao = 0.15
            imposto = 0.10
            mktplace = 0.18
            lucro = 0.15
            custo_total = valor_dolar * dolar * (1 + comissao + imposto)
            preco_final = custo_total / (1 - mktplace - lucro)
            resultado = round(preco_final, 2)
            detalhes = {
                'valor_dolar': valor_dolar,
                'custo_total': round(custo_total, 2),
                'dolar': dolar,
                'comissao': comissao,
                'imposto': imposto,
                'mktplace': mktplace,
                'lucro': lucro
            }
        except Exception:
            resultado = "Erro no cálculo"
    return render_template("calculadora.html", resultado=resultado, detalhes=detalhes)

@app.route('/auth')
def auth():
    return redirect(f"https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Erro: código de autorização não encontrado."
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post('https://www.bling.com.br/Api/v3/oauth/token', headers=headers, data=data)
    if response.status_code == 200:
        session['bling_token'] = response.json().get('access_token')
        return redirect(url_for('dashboard'))
    return f"Erro ao obter token Bling: {response.status_code} - {response.text}"

@app.route('/produtos-bling')
def produtos_bling():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    token = session.get('bling_token')
    if not token:
        return redirect(url_for('auth'))
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)
    if response.status_code != 200:
        return f"Erro: {response.text}"
    data = response.json()
    produtos = []
    for item in data.get('data', []):
        produto = item.get('produto') or item
        produtos.append({
            'sku': produto.get('codigo') or produto.get('sku'),
            'nome': produto.get('nome') or 'Sem nome',
            'estoque': produto.get('estoqueAtual') or 0,
            'preco': produto.get('preco') or 0.0
        })
    return render_template("produtos_bling_calculo.html", produtos=produtos)

@app.route('/exportar')
def exportar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    produtos = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    df = pd.DataFrame(produtos, columns=['sku', 'nome', 'estoque', 'preco', 'preco_custo', 'ultima_atualizacao', 'id'])
    caminho = "/tmp/exportados.xlsx"
    df.to_excel(caminho, index=False)
    return send_file(caminho, as_attachment=True)

@app.route('/usuarios')
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=usuarios)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)