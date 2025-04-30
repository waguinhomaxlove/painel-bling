app.py
import os
import sqlite3
import requests
import pandas as pd
from flask import Flask, rendertemplate, request, redirect, session, urlfor, make_response
app = Flask(name)
app.secretkey = 'chave-secreta'
from datetime import timedelta
app.permanentsession_lifetime = timedelta(days=1)
CLIENTID = 'c0588a73f49371b037d8bb333c059e29406c7850'
CLIENTSECRET = 'ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2'
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'
def getdbconnection():
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
        conn = getdbconnection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
    if user:
        session['usuario'] = email
        session.permanent = True
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
        return redirect(urlfor('login'))
    conn = getdbconnection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return rendertemplate("dashboard.html", produtos=produtos)
@app.route('/usuarios')
def usuarios():
    conn = getdbconnection()
    usuarios = conn.execute('SELECT id, nome, email FROM usuarios').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)
@app.route('/adicionar', methods=['POST'])
def adicionar():
    sku = request.form['sku']
    nome = request.form['nome']
    estoque = request.form['estoque']
    preco = request.form['preco']
    precocusto = request.form['precocusto']
    conn = getdbconnection()
    conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, precocusto) VALUES (?, ?, ?, ?, ?)',
                 (sku, nome, estoque, preco, precocusto))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))
@app.route('/editar/<sku>', methods=['GET', 'POST'])
def editar(sku):
    conn = getdbconnection()
    produto = conn.execute('SELECT * FROM produtos WHERE sku = ?', (sku,)).fetchone()
    if request.method == 'POST':
        nome = request.form['nome']
        estoque = request.form['estoque']
        preco = request.form['preco']
        precocusto = request.form['precocusto']
        conn.execute('UPDATE produtos SET nome = ?, estoque = ?, preco = ?, precocusto = ? WHERE sku = ?',
                     (nome, estoque, precocusto, preco, sku))
        conn.commit()
        conn.close()
        return redirect(urlfor('dashboard'))
    conn.close()
    return rendertemplate('editar.html', produto=produto)
@app.route('/excluir/<sku>')
def excluir(sku):
    conn = getdbconnection()
    conn.execute('DELETE FROM produtos WHERE sku = ?', (sku,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))
@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    detalhes = {}
    if request.method == 'POST':
        try:
            valordolar = float(request.form['valordolar'])
            dolar = 5.90
            fornecedor = 0.15
            imposto = 0.10
            mktplace = 0.18
            lucro = 0.15
            custototal = valordolar * dolar * (1 + fornecedor + imposto)
            precofinal = custototal / (1 - mktplace - lucro)
            resultado = round(precofinal, 2)
            detalhes = {
                "valordolar": valordolar,
                "valorconvertido": round(valordolar * dolar, 2),
                "custototal": round(custototal, 2),
                "precofinal": resultado,
                "cotacao": dolar,
                "importador": fornecedor,
                "imposto": imposto,
                "marketplace": mktplace,
                "lucro": lucro
            }
        except Exception as e:
            resultado = 'Erro no cálculo'
    return render_template("calculadora.html", resultado=resultado, detalhes=detalhes)
@app.route('/exportar')
def exportar():
    conn = getdbconnection()
    produtos = conn.execute('SELECT sku, nome, estoque, preco, precocusto, ultimaatualizacao FROM produtos').fetchall()
    conn.close()
    dados = [dict(p) for p in produtos]
    df = pd.DataFrame(dados)
    output = df.tocsv(index=False, sep=';', encoding='utf-8-sig')
    response = makeresponse(output)
    response.headers["Content-Disposition"] = "attachment; filename=produtos_exportados.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8-sig"
    return response
@app.route('/auth')
def auth():
    url = f"https://www.bling.com.br/Api/v3/oauth/authorize?responsetype=code&clientid={CLIENTID}&redirecturi={REDIRECT_URI}&state=secure123"
    return redirect(url)
@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Erro: código de autorização não encontrado."
    tokenurl = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {
        "granttype": "authorizationcode",
        "code": code,
        "redirecturi": REDIRECTURI,
        "clientid": CLIENTID,
        "clientsecret": CLIENTSECRET
    }
    response = requests.post(tokenurl, data=data)  # Removido auth
    if response.statuscode == 200:
        accesstoken = response.json().get("accesstoken")
        session['blingtoken'] = accesstoken
        print("Token obtido:", accesstoken)  # Debug
        return redirect(urlfor('dashboard'))
    else:
        print("Erro ao obter token Bling:", response.text)  # Debug
        return f"Erro ao obter token Bling.<br><br>Status: {response.statuscode}<br><br>{response.text}"
@app.route('/produtos-bling')
def produtosbling():
    token = session.get('blingtoken')
    print("Token na sessão:", token)  # Debug
if not token:
    return redirect(url_for('login'))

headers = { "Authorization": f"Bearer {token}" }
response = requests.get("https://api.bling.com.br/v3/produtos", headers=headers)

print("Código de status da resposta:", response.status_code)  # Debug
if response.status_code != 200:
    print("Erro na resposta do Bling:", response.text)  # Debug
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

return render_template("produtos_bling.html", produtos=produtos)

@app.route('/produtos-calculo')
def produtoscalculo():
    token = session.get('blingtoken')
    if not token:
        return redirect(url_for('login'))
headers = { "Authorization": f"Bearer {token}" }
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

if name == 'main':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)