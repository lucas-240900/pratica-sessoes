from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import sqlite3

# função auxiliar
def validar_informacoes(username, password):
    if username == '':
        return 'Preencha o nome.'
    elif len(username) < 3:
        return 'O nome deve ter pelo menos 3 caracteres.'
    elif password == '':
        return 'Preencha a senha'
    else:
        return None

# iniciando o app
app = Flask(__name__)

# configurações da sessão
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'LUCAS'

# iniciando a sessão
Session(app)

def init_db():
    conn = sqlite3.connect('users.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sair')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    # POST
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.sqlite3')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        getUsername = cursor.fetchone()
        
        conn.close()

        if getUsername is not None:
            session["username"] = getUsername[1]
            session["password"] = getUsername[2]
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    
    # GET
    msg = request.args.get("msg")
    
    if session.get("username"):
        return redirect(url_for("dashboard"))
    
    return render_template('login.html', msg=msg)

@app.route('/cadastro', methods=["GET", "POST"])
def cadastro():
    erro = request.args.get("erro")
    
    # ERRO
    if erro != "":
        data = request.form
        return render_template('cadastrar.html', erro=erro, form=data)        
    
    # OK
    return render_template('cadastrar.html', erro=None, form=None)        
        
@app.route('/registrar', methods=['POST'])
def registrar():
    username = request.form['username']
    password = request.form['password']
    
    msg = validar_informacoes(username, password)
    
    # ERRO
    if msg is not None:
        return redirect(url_for('cadastro', erro=msg))
    
    # OK
    conn = sqlite3.connect('users.sqlite3')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO users (username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()
    
    return redirect(url_for('login', msg="Você foi cadastrado!" )) 

@app.route('/dashboard')
def dashboard():
    # se estiver logado
    if session.get("username"):
        return render_template('dashboard.html')
    
    return redirect(url_for("login"))
    
    
if __name__ == '__main__':
    app.run(debug=True)   