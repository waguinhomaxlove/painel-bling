
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return "Sistema ativo. Acesse /respostas para gerar respostas automáticas."

@app.route("/respostas", methods=["GET", "POST"])
def respostas():
    texto = ""
    if request.method == "POST":
        codigo = request.form["codigo"]
        tipo = request.form["resposta"]

        if tipo == "1":
            texto = f"""Olá! Tudo bem?\n\nVerificamos aqui que o seu pedido está dentro do prazo estimado de entrega e segue em trânsito normalmente com a transportadora Total Express.\n\nVocê pode acompanhar o andamento da entrega acessando o site da Total Express e informando o código de rastreio abaixo:\nCódigo de rastreio: {codigo}\nURL para rastreamento: https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}\n\nFicamos à disposição para qualquer dúvida ou suporte adicional.\nAgradecemos pela sua paciência e preferência!\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "1e" or tipo == "2":
            texto = f"""Olá! Tudo certo?\n\nConforme verificação no sistema da Total Express, o seu pedido foi entregue com sucesso.\n\nCódigo de rastreio: {codigo}\nURL para rastreamento: https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}\n\nCaso ainda não tenha localizado o pacote, sugerimos verificar com moradores, porteiros ou recepção.\nQualquer dúvida, estamos à disposição!\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "3":
            texto = f"""Olá! Tudo bem?\n\nVerificamos que seu pedido está com atraso na entrega.\nJá estamos abrindo uma solicitação junto à transportadora Total Express para apurar o ocorrido.\n\nCódigo de rastreio: {codigo}\nURL para rastreamento: https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}\n\nNos comprometemos a retornar com uma posição em até 48 horas úteis.\nAgradecemos pela compreensão e paciência.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "4":
            texto = f"""Olá! Tudo bem?\n\nSentimos muito pelo transtorno com o seu produto.\nEm casos como esse, você pode optar por troca ou cancelamento, conforme sua preferência.\n\nJá emitimos um código de postagem reversa para devolução gratuita pelos Correios:\nCódigo de devolução: {codigo}\n\nVocê tem até 10 dias corridos para realizar o envio a partir da data de hoje.\nAssim que o produto retornar e for conferido, daremos sequência à troca ou reembolso.\n\nFicamos à disposição para qualquer dúvida ou assistência.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "5":
            texto = f"""Olá! Tudo bem?\n\nLamentamos o transtorno. Verificamos que o seu pedido foi considerado extraviado pela transportadora Total Express.\n\nDiante disso, já iniciamos o processo de cancelamento e estorno conforme o método de pagamento utilizado.\n\nCaso necessário, segue o código de devolução para qualquer conferência adicional:\nCódigo de devolução: {codigo}\n\nFicamos à disposição para qualquer dúvida ou suporte adicional.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""
        elif tipo == "6":
            texto = f"""Olá! Tudo bem?\n\nVerificamos que o seu pedido foi enviado corretamente, porém o número indicado pela transportadora Total Express não foi localizado para a entrega.\n\nCódigo de rastreio: {codigo}\nURL para rastreamento: https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}\n\nNeste caso, você pode optar por cancelamento com estorno ou reenvio do produto com os dados de endereço revisados.\nPor favor, nos informe sua preferência para seguirmos com o atendimento.\n\nAtenciosamente,\nEquipe Robô Hardware LTDA"""

    return render_template("respostas.html", texto=texto)

if __name__ == "__main__":
    app.run(debug=True)
