"""
Rotas de autenticação e home:
- /              (home)
- /registrar
- /login
- /login/google  + callback
- /logout
"""
from flask import render_template, request, redirect, url_for, session

from models import db, Usuario
from extensoes import oauth


def registrar(app):

    @app.route("/registrar", methods=["GET", "POST"])
    def registrar():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            senha = request.form["senha"]
            if Usuario.query.filter_by(email=email).first():
                return render_template("registrar.html", erro="Esse e-mail já está cadastrado.")
            usuario = Usuario(email=email)
            usuario.definir_senha(senha)
            db.session.add(usuario)
            db.session.commit()
            session["usuario_id"] = usuario.id
            return redirect(url_for("minha_equipe"))
        return render_template("registrar.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            senha = request.form["senha"]
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and usuario.verificar_senha(senha):
                session["usuario_id"] = usuario.id
                return redirect(url_for("home"))
            return render_template("login.html", erro="E-mail ou senha inválidos.")
        return render_template("login.html")

    @app.route("/login/google")
    def login_google():
        google = oauth.create_client("google")
        redirect_uri = url_for("auth_google_callback", _external=True)
        return google.authorize_redirect(redirect_uri)

    @app.route("/login/google/callback")
    def auth_google_callback():
        google = oauth.create_client("google")
        token = google.authorize_access_token()
        userinfo = token.get("userinfo")
        email = userinfo["email"]
        google_id = userinfo["sub"]
        usuario = Usuario.query.filter_by(google_id=google_id).first()
        if not usuario:
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                usuario.google_id = google_id
            else:
                usuario = Usuario(email=email, google_id=google_id)
                db.session.add(usuario)
        db.session.commit()
        session["usuario_id"] = usuario.id
        return redirect(url_for("home"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.route("/")
    def home():
        return render_template("home.html")
