from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/gerar_resposta', methods=['GET', 'POST'])
def gerar_resposta():
    resposta_gerada = None
    if request.method == 'POST':
        rastreio = request.form['rastreio'].strip()
        tipo = request.form['tipo']
        transportadora = 'Total Express'
        link = f"https://totalconecta.totalexpress.com.br/rastreamento/?codigo={rastreio}"

        if tipo == 'transito':
            resposta_gerada = f"""Olá! Tudo bem?

Verificamos aqui que o seu pedido está dentro do prazo estimado de entrega e segue em trânsito normalmente com a transportadora {transportadora}.

Você pode acompanhar o andamento da entrega acessando o link abaixo:
Código de rastreio: {rastreio}
URL para rastreamento: {link}

Ficamos à disposição para qualquer dúvida ou suporte adicional.
Agradecemos pela sua paciência e preferência!

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == 'entregue':
            resposta_gerada = f"""Olá! Tudo bem?

Constatamos aqui que o seu pedido foi entregue com sucesso pela transportadora {transportadora}, conforme o rastreamento abaixo:

Código de rastreio: {rastreio}
URL para rastreamento: {link}

Caso ainda não tenha recebido o produto, recomendamos verificar com outras pessoas no local de entrega (portaria, recepção ou familiares).
Se continuar com dúvidas, estamos à disposição para ajudar.

Agradecemos pela preferência!

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == 'atraso':
            resposta_gerada = f"""Olá! Tudo bem?

Verificamos que seu pedido está com atraso na entrega.
Já estamos abrindo uma solicitação junto à transportadora {transportadora} para apurar o ocorrido.

Código de rastreio: {rastreio}
URL para rastreamento: {link}

Nos comprometemos a retornar com uma posição em até 48 horas úteis.
Agradecemos pela compreensão e paciência.

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == 'extravio':
            resposta_gerada = f"""Olá! Tudo bem?

Lamentamos o transtorno. Verificamos que o seu pedido foi considerado extraviado pela transportadora {transportadora}.

Diante disso, já iniciamos o processo de cancelamento e estorno conforme o método de pagamento utilizado.

Caso necessário, segue o código de devolução para qualquer conferência adicional:
Código de devolução: AM387888418BR

Ficamos à disposição para qualquer dúvida ou suporte adicional.

Atenciosamente,
Equipe Robô Hardware LTDA"""
        elif tipo == 'numero_nao_localizado':
            resposta_gerada = f"""Olá! Tudo bem?

Verificamos que o seu pedido foi enviado corretamente, porém o número indicado pela transportadora {transportadora} não foi localizado para a entrega.

Código de rastreio: {rastreio}
URL para rastreamento: {link}

Neste caso, você pode optar por cancelamento com estorno ou reenvio do produto com os dados de endereço revisados.
Por favor, nos informe sua preferência para seguirmos com o atendimento.

Atenciosamente,
Equipe Robô Hardware LTDA"""

    return render_template("resposta_form.html", resposta=resposta_gerada)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)