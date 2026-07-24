"""
Extensões compartilhadas do app (evita import circular).

- migrate  : Flask-Migrate (inicializado no app.py com init_app)
- oauth    : Authlib OAuth (login com Google), registrado em init_oauth()
- login_requerido / admin_requerido : decorators de controle de acesso

Os decorators NÃO mudam de nome nem de comportamento em relação ao app.py
antigo, então tudo que já usava @login_requerido / @admin_requerido continua
igual.
"""
import functools

from flask import redirect, url_for, session, render_template
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth

# Instâncias únicas, ligadas ao app depois (init_app), pra evitar import circular.
migrate = Migrate()
oauth = OAuth()


def init_oauth(app):
    """Registra o provedor Google no OAuth usando as credenciais do config.

    Depois disto, qualquer rota pode pegar o cliente com:
        from extensoes import oauth
        google = oauth.create_client("google")
    """
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def login_requerido(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def admin_requerido(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        from models import Usuario
        usuario_id = session.get("usuario_id")
        if not usuario_id:
            return redirect(url_for("login"))
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.eh_admin:
            return render_template("acesso_negado.html"), 403
        return view_func(*args, **kwargs)
    return wrapper
