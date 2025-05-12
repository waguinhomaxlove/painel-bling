from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        # Aqui você pode colocar a lógica de autenticação
        email = request.form['email']
        senha = request.form['senha']
        if email == "admin" and senha == "123":
            return redirect(url_for('dashboard'))
        else:
            erro = "E-mail ou senha inválidos"
    return render_template('login.html', erro=erro)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    busca = request.args.get('busca', '')
    produtos = []  # Preencha com dados do banco se necessário
    return render_template('dashboard.html', busca=busca, produtos=produtos)

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    usuarios = []  # Preencha com dados reais
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/respostas', methods=["GET", "POST"])
def respostas():
    texto = ""
    if request.method == "POST":
        codigo = request.form["codigo"]
        tipo = request.form["resposta"]
        if codigo.lower().startswith("txas"):
            link = f"https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}"
            transportadora = "Total Express"
        else:
            link = f"https://www2.correios.com.br/sistemas/rastreamento/default.cfm?objetos={codigo}"
            transportadora = "Correios"
        if tipo == "1":
            texto = f"""Olá! Tudo bem?\n\nVerificamos aqui que o seu pedido está dentro do prazo estimado de entrega e segue em trânsito normalmente com a transportadora {transportadora}.\n\nVocê pode acompanhar o andamento da entrega no link abaixo:\nCódigo de rastreio: {codigo}\nRastreamento: {link}\n\nFicamos à disposição para qualquer dúvida ou suporte adicional.\nAgradecemos pela sua paciência e preferência!\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo in ["1e", "2"]:
            texto = f"""Olá! Tudo certo?\n\nConforme verificação no sistema da transportadora {transportadora}, o seu pedido foi entregue com sucesso.\n\nCódigo de rastreio: {codigo}\nRastreamento: {link}\n\nCaso ainda não tenha localizado o pacote, sugerimos verificar com moradores, porteiros ou recepção.\nQualquer dúvida, estamos à disposição!\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "3":
            texto = f"""Olá! Tudo bem?\n\nVerificamos que seu pedido está com atraso na entrega.\nJá estamos abrindo uma solicitação junto à transportadora {transportadora} para apurar o ocorrido.\n\nCódigo de rastreio: {codigo}\nRastreamento: {link}\n\nNos comprometemos a retornar com uma posição em até 48 horas úteis.\nAgradecemos pela compreensão e paciência.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "4":
            texto = f"""Olá! Tudo bem?\n\nSentimos muito pelo transtorno com o seu produto.\nEm casos como esse, você pode optar por troca ou cancelamento, conforme sua preferência.\n\nJá emitimos um código de postagem reversa para devolução gratuita pelos Correios:\nCódigo de devolução: {codigo}\n\nVocê tem até 10 dias corridos para realizar o envio a partir da data de hoje.\nAssim que o produto retornar e for conferido, daremos sequência à troca ou reembolso.\n\nFicamos à disposição para qualquer dúvida ou assistência.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "5":
            texto = f"""Olá! Tudo bem?\n\nLamentamos o transtorno. Verificamos que o seu pedido foi considerado extraviado pela transportadora {transportadora}.\n\nDiante disso, já iniciamos o processo de cancelamento e estorno conforme o método de pagamento utilizado.\n\nCaso necessário, segue o código de devolução para qualquer conferência adicional:\nCódigo de devolução: {codigo}\n\nFicamos à disposição para qualquer dúvida ou suporte adicional.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "6":
            texto = f"""Olá! Tudo bem?\n\nVerificamos que o seu pedido foi enviado corretamente, porém o número indicado pela transportadora {transportadora} não foi localizado para a entrega.\n\nCódigo de rastreio: {codigo}\nRastreamento: {link}\n\nNeste caso, você pode optar por cancelamento com estorno ou reenvio do produto com os dados de endereço revisados.\nPor favor, nos informe sua preferência para seguirmos com o atendimento.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
    return render_template("respostas.html", texto=texto)

@app.route('/', methods=['GET', 'POST'])
def calculadora():
    resultado = None
    detalhes = None

    if request.method == 'POST':
        try:
            valor_dolar = float(request.form['valor_dolar'].replace(',', '.'))
            dolar = 5.90  # cotação fixa
            importador = 0.15  # comissão do fornecedor
            imposto = 0.10  # imposto sobre a venda
            mktplace = 0.21  # comissão marketplace
            lucro = 0.15  # lucro líquido desejado

            # cálculo do custo em reais com comissão do fornecedor
            custo_base = valor_dolar * dolar
            custo_importador = custo_base * importador
            custo_fixo_unitario = 5.00

            # cálculo da parcela das despesas fixas (por unidade vendida)
            faturamento_estimado = 120000  # Exemplo de faturamento mensal
            despesas_fixas = 3000.00
            proporcao_despesas = despesas_fixas / faturamento_estimado  # ex: 0.025 = 2,5%
            
            custo_total = custo_base + custo_importador + custo_fixo_unitario
            preco_final = custo_total / (1 - imposto - mktplace - lucro - proporcao_despesas)

            resultado = f"{preco_final:.2f}"
            detalhes = {
                'dolar': dolar,
                'importador': importador,
                'imposto': imposto,
                'mktplace': mktplace,
                'lucro': lucro,
                'custo_total': f"{custo_total:.2f}",
                'preco_final': f"{preco_final:.2f}"
            }
        except:
            resultado = 'Erro no cálculo'

    return render_template('calculadora.html', resultado=resultado, detalhes=detalhes)


@app.route('/editar/<sku>', methods=['GET', 'POST'])
def editar(sku):
    produto = [sku, 'Nome do Produto', 10, 199.90, 150.00]
    return render_template('editar.html', produto=produto)

@app.route('/produtos_bling')
def produtos_bling():
    produtos = []  # Simulado
    return render_template('produtos_bling.html', produtos=produtos)

@app.route('/produtos_bling_calculo')
def produtos_bling_calculo():
    produtos = []  # Simulado
    return render_template('produtos_bling_calculo.html', produtos=produtos)

@app.route('/produtos_calculo', methods=['GET', 'POST'])
def produtos_calculo():
    produtos = []  # Simulado
    return render_template('produtos_calculo.html', produtos=produtos)

@app.route('/produtos-bling')
def produtos_bling_2():
    produtos = []  # Simulado
    return render_template('produtos-bling.html', produtos=produtos)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/exportar')
def exportar():
    return "Função de exportação ainda não implementada."

@app.route('/adicionar', methods=['POST'])
def adicionar():
    return redirect(url_for('dashboard'))

@app.route('/excluir/<sku>')
def excluir(sku):
    return redirect(url_for('dashboard'))

# Inicialização da aplicação
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
