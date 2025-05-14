
from flask import Flask, render_template, request, session, redirect, url_for
from xml.etree import ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo123'

# -------------------- ROTAS DE AUTENTICAÇÃO --------------------
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'admin' and senha == '1234':
            session['usuario'] = usuario
            return redirect('/dashboard')
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# -------------------- DASHBOARD --------------------
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# -------------------- USUÁRIOS --------------------
@app.route('/usuarios')
def usuarios():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('usuarios.html')

@app.route('/editar')
def editar():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('editar.html')

# -------------------- CALCULADORA --------------------
@app.route('/calculadora')
def calculadora():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('calculadora.html')

# -------------------- PRODUTOS --------------------
@app.route('/produtos-bling')
def produtos_bling():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('produtos-bling.html')

@app.route('/produtos_bling')
def produtos_bling2():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('produtos_bling.html')

@app.route('/produtos_calculo')
def produtos_calculo():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('produtos_calculo.html')

@app.route('/produtos_bling_calculo')
def produtos_bling_calculo():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('produtos_bling_calculo.html')

# -------------------- RESPOSTAS --------------------
@app.route('/respostas')
def respostas():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('respostas.html')

# -------------------- FORMULÁRIO ROMANEIO --------------------
@app.route('/romaneio_form')
def romaneio_form():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('romaneio_form.html')

# -------------------- PROCESSAMENTO DE XML --------------------
@app.route('/romaneio_xml', methods=['GET', 'POST'])
def romaneio_xml():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("xmlfiles")
        session['romaneios'] = []
        ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}

        for f in uploaded_files:
            try:
                tree = ET.parse(f)
                root = tree.getroot()

                nome = root.find('.//ns:dest/ns:xNome', ns)
                nota = root.find('.//ns:ide/ns:nNF', ns)
                qtd_el = root.find('.//ns:vol/ns:qVol', ns)

                session['romaneios'].append({
                    'nome': nome.text if nome is not None else 'NOME NÃO ENCONTRADO',
                    'nota': nota.text if nota is not None else '0000',
                    'quantidade': int(float(qtd_el.text)) if qtd_el is not None else 1
                })
            except Exception as e:
                print(f"Erro ao ler XML: {e}")
        return render_template("romaneio_xml_preencher.html", romaneios=session['romaneios'])
    return render_template("romaneio_xml.html")

# -------------------- ENVIO FINAL ROMANEIO --------------------
@app.route('/romaneio_gerado', methods=['POST'])
def romaneio_gerado_post():
    total = int(request.form['total_linhas'])
    romaneios_final = []
    for i in range(total):
        romaneios_final.append({
            'nome': request.form.get(f'nome_{i}', ''),
            'nota': request.form.get(f'nota_{i}', ''),
            'quantidade': request.form.get(f'quantidade_{i}', ''),
            'rastreio': request.form.get(f'rastreio_{i}', '')
        })
    data_atual = datetime.now().strftime('%d/%m/%Y')
    return render_template("romaneio_gerado.html", romaneios=romaneios_final, data=data_atual, total=total)

# -------------------- EXECUÇÃO --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
