
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

        # Detectar transportadora e link
        if codigo.lower().startswith("txas"):
            link = f"https://totalconecta.totalexpress.com.br/rastreamento/?codigo={codigo}"
            transportadora = "Total Express"
        else:
            link = f"https://www2.correios.com.br/sistemas/rastreamento/default.cfm?objetos={codigo}"
            transportadora = "Correios"

        if tipo == "1":
            texto = f"""Olá! Tudo bem?

Verificamos aqui que o seu pedido está dentro do prazo estimado de entrega e segue em trânsito normalmente com a transportadora {transportadora}.

Você pode acompanhar o andamento da entrega no link abaixo:
Código de rastreio: {codigo}
Rastreamento: {link}

Ficamos à disposição para qualquer dúvida ou suporte adicional.
Agradecemos pela sua paciência e preferência!

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo in ["1e", "2"]:
            texto = f"""Olá! Tudo certo?

Conforme verificação no sistema da transportadora {transportadora}, o seu pedido foi entregue com sucesso.

Código de rastreio: {codigo}
Rastreamento: {link}

Caso ainda não tenha localizado o pacote, sugerimos verificar com moradores, porteiros ou recepção.
Qualquer dúvida, estamos à disposição!

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == "3":
            texto = f"""Olá! Tudo bem?

Verificamos que seu pedido está com atraso na entrega.
Já estamos abrindo uma solicitação junto à transportadora {transportadora} para apurar o ocorrido.

Código de rastreio: {codigo}
Rastreamento: {link}

Nos comprometemos a retornar com uma posição em até 48 horas úteis.
Agradecemos pela compreensão e paciência.

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == "4":
            texto = f"""Olá! Tudo bem?

Sentimos muito pelo transtorno com o seu produto.
Em casos como esse, você pode optar por troca ou cancelamento, conforme sua preferência.

Já emitimos um código de postagem reversa para devolução gratuita pelos Correios:
Código de devolução: {codigo}

Você tem até 10 dias corridos para realizar o envio a partir da data de hoje.
Assim que o produto retornar e for conferido, daremos sequência à troca ou reembolso.

Ficamos à disposição para qualquer dúvida ou assistência.

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == "5":
            texto = f"""Olá! Tudo bem?

Lamentamos o transtorno. Verificamos que o seu pedido foi considerado extraviado pela transportadora {transportadora}.

Diante disso, já iniciamos o processo de cancelamento e estorno conforme o método de pagamento utilizado.

Caso necessário, segue o código de devolução para qualquer conferência adicional:
Código de devolução: {codigo}

Ficamos à disposição para qualquer dúvida ou suporte adicional.

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == "6":
            texto = f"""Olá! Tudo bem?

Verificamos que o seu pedido foi enviado corretamente, porém o número indicado pela transportadora {transportadora} não foi localizado para a entrega.

Código de rastreio: {codigo}
Rastreamento: {link}

Neste caso, você pode optar por cancelamento com estorno ou reenvio do produto com os dados de endereço revisados.
Por favor, nos informe sua preferência para seguirmos com o atendimento.

Atenciosamente,
Equipe Robô Hardware LTDA"""

    return render_template("respostas.html", texto=texto)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
