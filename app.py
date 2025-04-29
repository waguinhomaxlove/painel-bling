from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # troque depois para segurança real

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -------------------- MODELO DE USUÁRIO --------------------
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def get(email):
        conn = sqlite3.connect('painel.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], email=row[1], password=row[2])
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('painel.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], email=row[1], password=row[2])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# -------------------- ROTAS --------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get(email)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')
        else:
            return 'Login falhou. Verifique o email e a senha.'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    produtos = cursor.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return render_template("dashboard.html", produtos=produtos)

# -------------------- CRIAR USUÁRIO (manual) --------------------
@app.route('/criar-usuario')
def criar_usuario():
    email = "admin@painel.com"
    senha = generate_password_hash("admin123")
    conn = sqlite3.connect("painel.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, senha))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Usuário já existe."
    finally:
        conn.close()
    return "Usuário criado com sucesso."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
