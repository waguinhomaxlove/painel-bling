
import os
import sqlite3
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect, session, url_for, make_response

app = Flask(__name__)
app.secret_key = 'chave-secreta'

CLIENT_ID = 'c0588a73f49371b037d8bb333c059e29406c7850'
CLIENT_SECRET = 'ce2bdfe24c2c87a804e7f5386fbd305c83a884c68a3db30823fc35c8e4f2'
REDIRECT_URI = 'https://painel-bling.onrender.com/callback'

@app.route('/auth')
def auth():
    url = f"https://www.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=secure123"
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Erro: código de autorização não encontrado."

    token_url = "https://www.bling.com.br/Api/v3/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        session['bling_token'] = access_token
        return redirect(url_for('dashboard'))
    else:
        return f"Erro ao obter token Bling.<br><br>Status: {response.status_code}<br><br>{response.text}"

# Simulação curta, o resto do código seria mantido conforme app unificado
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
