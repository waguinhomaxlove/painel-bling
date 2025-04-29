from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Bling API v3 Configuração
CLIENT_ID = 'c0588a73f49371b037d8bb333c059e29406c7850'
CLIENT_SECRET = 'ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2'
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'
API_TOKEN_URL = 'https://api.bling.com.br/oauth/token'

access_token = None

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def get(email):
        conn = sqlite3.connect('painel.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], email=row[1], password=row[2])
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('painel.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], email=row[1], password=row[2])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get(email)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')
        else:
            return 'Login falhou. Verifique o email e a senha.'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# Bling OAuth v3 fluxo
@app.route('/auth')
@login_required
def auth():
    auth_url = f"https://www.bling.com.br/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global access_token
    code = request.args.get('code')
    if code:
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': code
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(API_TOKEN_URL, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
            return redirect('/dashboard')
        else:
            return 'Erro ao obter token Bling.'
    return 'Nenhum código recebido.'

@app.route('/dashboard')
@login_required
def dashboard():
    busca = request.args.get('busca', '').strip()
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()

    if busca:
        produtos = cursor.execute("SELECT * FROM produtos WHERE sku LIKE ? OR nome LIKE ?", (f"%{busca}%", f"%{busca}%")).fetchall()
    else:
        produtos = cursor.execute("SELECT * FROM produtos").fetchall()

    conn.close()
    return render_template("dashboard.html", produtos=produtos, busca=busca)

@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    sku = request.form['sku']
    nome = request.form['nome']
    estoque = request.form['estoque']
    preco = request.form['preco']
    custo = request.form['custo']

    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (sku, nome, estoque, preco, custo, atualizado_em)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
    """, (sku, nome, estoque, preco, custo))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/editar/<sku>', methods=['GET', 'POST'])
@login_required
def editar(sku):
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        estoque = request.form['estoque']
        preco = request.form['preco']
        custo = request.form['custo']

        cursor.execute("""
            UPDATE produtos SET nome = ?, estoque = ?, preco = ?, custo = ?, atualizado_em = datetime('now', 'localtime')
            WHERE sku = ?
        """, (nome, estoque, preco, custo, sku))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    produto = cursor.execute("SELECT * FROM produtos WHERE sku = ?", (sku,)).fetchone()
    conn.close()
    return render_template("editar.html", produto=produto)

@app.route('/excluir/<sku>')
@login_required
def excluir(sku):
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/exportar')
@login_required
def exportar():
    conn = sqlite3.connect("painel.db")
    df = pd.read_sql_query("SELECT sku, nome, estoque, preco, custo, atualizado_em FROM produtos", conn)
    conn.close()

    path = "produtos_exportados.xlsx"
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/calculadora', methods=['GET', 'POST'])
@login_required
def calculadora():
    resultado = None
    if request.method == 'POST':
        try:
            valor_dolar = float(request.form.get('valor', 0))

            cotacao = 5.90
            comissao_vendedor = 0.15
            impostos = 0.10
            comissao_marketplace = 0.18
            lucro_liquido_desejado = 0.15

            custo_base = valor_dolar * cotacao
            custo_total = custo_base * (1 + comissao_vendedor + impostos)

            preco_final = custo_total / (1 - comissao_marketplace - lucro_liquido_desejado)
            resultado = round(preco_final, 2)

        except Exception as e:
            print("Erro na calculadora:", e)
            resultado = "Erro ao calcular."

    return render_template("calculadora.html", resultado=resultado)

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, senha_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email já cadastrado."

    lista = cursor.execute("SELECT id, email FROM users").fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=lista)

@app.route('/criar-usuario')
def criar_usuario():
    email = "admin@painel.com"
    senha = generate_password_hash("admin123")
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, senha))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Usuário já existe."
    finally:
        conn.close()
    return "Usuário criado com sucesso."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
