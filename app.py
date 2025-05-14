from flask import Flask, render_template, request, session
from xml.etree import ElementTree as ET
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'segredo123'

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)