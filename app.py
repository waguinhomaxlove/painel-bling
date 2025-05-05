
from flask import Flask, render_template, request, redirect, session, url_for, make_response, send_file
import os
import sqlite3
import requests
import pandas as pd

app = Flask(__name__)
app.secret_key = 'chave-secreta'

# Exemplo mínimo de rota existente
@app.route('/')
def index():
    return "Painel funcionando. Vá para /planilha para abrir a tabela."

# Rota nova para servir a tabela HTML
@app.route('/planilha')
def planilha():
    return send_file("tabela.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
