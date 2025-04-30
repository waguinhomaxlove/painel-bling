
# Simulação de app_unificado_final.py
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')
