# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # troque para algo seguro

# Função para conectar ao banco
def get_db_connection():
    conn = sqlite3.connect('painel.db')
    conn.row_factory = sqlite3.Row
    return conn

# Cálculo de preço com base em dólar e taxas
def calcular_preco_final(valor_dolar, taxa_dolar, comissao_importador, comissao_marketplace, imposto, lucro_desejado):
    comissao_importador /= 100
    comissao_marketplace /= 100
    imposto /= 100
    lucro_desejado /= 100

    custo_base = valor_dolar * taxa_dolar
    custo_total = custo_base * (1 + comissao_importador)
    preco_final = custo_total / (1 - comissao_marketplace - imposto - lucro_desejado)
    lucro_liquido = preco_final - custo_total

    return round(preco_final, 2), round(custo_total, 2), round(lucro_liquido, 2)

# Rota inicial (login)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'admin' and senha == '1234':
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos.')
    return render_template('login.html')

# Dashboard principal
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template('dashboard.html', produtos=produtos)

# Rota para adicionar produto manualmente (teste)
@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    sku = request.form['sku']
    nome = request.form['nome']
    estoque = request.form['estoque']
    preco = request.form['preco']
    preco_custo = request.form['preco_custo']
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (sku, nome, estoque, preco, preco_custo, ultima_atualizacao) VALUES (?, ?, ?, ?, ?, ?)',
                 (sku, nome, estoque, preco, preco_custo, agora))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Rota para calculadora de preço
@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    if request.method == 'POST':
        valor_dolar = float(request.form['valor_dolar'])
        taxa_dolar = float(request.form['taxa_dolar'])
        comissao_importador = float(request.form['comissao_importador'])
        comissao_marketplace = float(request.form['comissao_marketplace'])
        imposto = float(request.form['imposto'])
        lucro_desejado = float(request.form['lucro_desejado'])

        resultado = calcular_preco_final(valor_dolar, taxa_dolar, comissao_importador, comissao_marketplace, imposto, lucro_desejado)

    return render_template('calculadora.html', resultado=resultado)

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
