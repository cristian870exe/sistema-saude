from flask import Flask, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "segredo123"

def conectar():
    return sqlite3.connect("banco.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        data TEXT,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = hash_senha(request.form.get("senha"))

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["usuario"] = usuario
            return redirect("/dashboard")
        else:
            return "<h3>Login inválido</h3><a href='/'>Voltar</a>"

    return """
    <h2>🏥 Sistema de Saúde</h2>
    <form method="POST">
        <input name="usuario" placeholder="Usuário"><br>
        <input name="senha" type="password" placeholder="Senha"><br>
        <button type="submit">Entrar</button>
    </form>
    <a href='/cadastro'>Criar conta</a>
    """

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = hash_senha(request.form.get("senha"))

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                           (usuario, senha))
            conn.commit()
        except:
            return "<h3>Usuário já existe</h3><a href='/cadastro'>Voltar</a>"

        conn.close()
        return "<h3>Cadastro realizado!</h3><a href='/'>Login</a>"

    return """
    <h2>Cadastro</h2>
    <form method="POST">
        <input name="usuario" placeholder="Usuário"><br>
        <input name="senha" type="password" placeholder="Senha"><br>
        <button type="submit">Cadastrar</button>
    </form>
    """

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    if request.method == "POST":
        data = request.form.get("data")
        tipo = request.form.get("tipo")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO consultas (usuario, data, tipo) VALUES (?, ?, ?)",
                       (usuario, data, tipo))
        conn.commit()
        conn.close()

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT data, tipo FROM consultas WHERE usuario=?", (usuario,))
    consultas = cursor.fetchall()
    conn.close()

    lista = ""
    for c in consultas:
        lista += f"<li>{c[0]} - {c[1]}</li>"

    return f"""
    <h2>Bem-vindo {usuario}</h2>

    <h3>📅 Agendar consulta</h3>
    <form method="POST">
        <input type="date" name="data"><br>
        <select name="tipo">
            <option>Clínico Geral</option>
            <option>Dentista</option>
            <option>Psicólogo</option>
        </select><br>
        <button type="submit">Agendar</button>
    </form>

    <h3>📄 Histórico</h3>
    <ul>{lista}</ul>

    <a href='/logout'>Sair</a>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)