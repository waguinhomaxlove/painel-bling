import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash  # Secure password hashing

app = Flask(__name__)
app.secret_key = 'chave-secreta'

CLIENT_ID = os.getenv('c0588a73f49371b037d8bb333c059e29406c7850')
CLIENT_SECRET = os.getenv('ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2')
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
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['senha'], senha):  # Verify hashed password
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
        hashed_password = generate_password_hash(senha)  # Hash the password
        try:
            conn.execute('INSERT INTO usuarios (email, senha) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')  # Flash success message
        except sqlite3.IntegrityError:
            flash('Erro: Email já cadastrado.', 'danger')  # Flash error message
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')

    usuarios = conn.execute('SELECT id, email FROM usuarios').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Protect route

    sku = request.form.get('sku')
    nome = request.form.get('nome')
    estoque = request.form.get('estoque')
    preco = request.form.get('preco')
    preco_custo = request.form.get('preco_custo')
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, preco_custo) VALUES (?, ?, ?, ?, ?)',
                     (sku, nome, estoque, preco, preco_custo))
        conn.commit()
        flash('Produto adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar produto: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('dashboard'))


@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Protect route

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
        except ValueError:
            flash('Por favor, insira um valor válido para o dólar.', 'danger')
        except Exception as e:
            flash(f'Erro no cálculo: {e}', 'danger')
    return render_template("calculadora.html", resultado=resultado)


@app.route('/auth')
def auth():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Protect route

    url = f"https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return redirect(url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Erro: código de autorização não encontrado."

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
    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        token_data = response.json()
        session['bling_token'] = token_data.get('access_token')
        return redirect(url_for('produtos_bling'))
    except requests.exceptions.RequestException as e:
        return f"Erro ao obter token Bling: {e}"


@app.route('/produtos-bling')
def produtos_bling():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Protect route

    token = session.get('bling_token')
    if not token:
        return redirect(url_for('auth'))
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)
        response.raise_for_status()
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
    except requests.exceptions.RequestException as e:
        return f"Erro ao buscar produtos do Bling: {e}"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)