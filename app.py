import functools
from datetime import datetime
import click
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
import config
from constantes import TANQUE_MAXIMO_LITROS
from models import (
    db, Usuario, CarroJogador, ResultadoClassificacao, ResultadoCorrida,
    ResultadoTreinoLivre,
    FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorChassi, FornecedorCambio, FornecedorSuspensao,
    FornecedorEngenheiro,
    Configuracao, Desenvolvimento, TreinamentoBox, garantir_colunas_fornecedores,
)
EquipeDB = CarroJogador
from models_temporada import Temporada, CorridaAgendada
from pontuacao import pontos_por_posicao, premio_por_posicao, ranking_temporada
from progressao import (
    calcular_custo_proximo_avanco, calcular_tempo_proximo_avanco_horas,
    verificar_conclusao, avancar, aplicar_desenvolvimento_da_temporada,
)
from classificacao import Classificacao
from corrida import Corrida, calcular_tempo_pit_stop
from estrategia import montar_estrategia_corrida, sugerir_estrategia_estrategista
from treino_livre_sim import simular_treino_livre_real
import modelos_componente


def simular_treino_livre(ajustes):
    total = sum(ajustes.values())
    erro = abs(total - 250)
    tempo_volta = 90.0 + (erro / 10.0)
    if erro < 20:
        resumo = "Setup muito bom para esse treino."
        dicas = "Ajustes próximos do ideal; mantenha a consistência."
    elif erro < 60:
        resumo = "Setup razoável, ainda há margem para melhorar."
        dicas = "Aumente o câmbio e a suspensão em pequenas etapas."
    else:
        resumo = "Setup ainda longe do ideal."
        dicas = "Reduza o excesso de ajuste e busque equilíbrio entre freio e aerodinâmica."
    return {"tempo_volta": round(tempo_volta, 3), "resumo": resumo, "dicas": dicas}


def simular_treino_oficial(ajustes, pneu, combustivel, volta_primeiro_pit, outro_pit):
    total = sum(ajustes.values())
    equilibrio = max(0, 250 - abs(total - 250))
    tempo_volta = 82.0 + (abs(total - 250) / 20.0) - (pneu.performance / 120.0) - (combustivel.eficiencia / 30.0) + (equilibrio / 100.0)
    if volta_primeiro_pit <= 8:
        estrategia = "Estratégia agressiva: primeiro pit cedo."
    elif volta_primeiro_pit <= 18:
        estrategia = "Estratégia equilibrada: primeiro pit no meio da corrida."
    else:
        estrategia = "Estratégia conservadora: primeiro pit mais tarde."
    if outro_pit:
        estrategia += " Um segundo pit também foi previsto."
    else:
        estrategia += " A corrida deve terminar com um único pit stop."
    return {"tempo_volta": round(tempo_volta, 3), "estrategia": estrategia,
            "pneu": pneu.nome, "combustivel": combustivel.nome}


from seed_fornecedores import popular_banco
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais, obter_pista_real, calcular_numero_voltas,
    atualizar_pista_real,
)
CATEGORIAS_PISTA = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
CATEGORIAS_CHUVA = ["seco", "intermediario", "chuva"]
app = Flask(__name__)
app.config.from_object(config)
if not app.config.get("SECRET_KEY"):
    app.config["SECRET_KEY"] = "dev-secret-key-troque-em-producao"
db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    garantir_colunas_fornecedores()
    criar_banco_pistas_reais()


@app.template_filter("tempo_min")
def _filtro_tempo_min(segundos):
    if segundos is None or segundos == "":
        return "-"
    try:
        segundos = float(segundos)
    except (TypeError, ValueError):
        return "-"
    sinal = "-" if segundos < 0 else ""
    segundos = abs(segundos)
    minutos = int(segundos // 60)
    segs = segundos - (minutos * 60)
    return f"{sinal}{minutos}:{segs:06.3f}"


@app.template_filter("tempo_dif")
def _filtro_tempo_dif(segundos):
    if segundos is None:
        return "-"
    try:
        segundos = float(segundos)
    except (TypeError, ValueError):
        return "-"
    if segundos == 0:
        return "-"
    if abs(segundos) >= 60:
        minutos = int(abs(segundos) // 60)
        s = abs(segundos) - (minutos * 60)
        sinal = "-" if segundos < 0 else "+"
        return f"{sinal}{minutos}:{s:06.3f}"
    return f"+{segundos:.3f}s"


@app.template_filter("dinheiro")
def _filtro_dinheiro(valor):
    if valor is None:
        return "-"
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# NOTE: FornecedorChassi mantido no admin (LEGADO) mas não aparece mais
# no formulário de criar equipe. Fica visível pra admin ver o histórico.
FORNECEDORES_CONFIG = {
    "motor": {"model": FornecedorMotor, "titulo": "Motor", "campo_equipe": "motor_fornecedor_id",
              "campos": [{"nome": "potencia", "label": "Potência", "tipo": "float"},
                         {"nome": "eficiencia_combustivel", "label": "Eficiência de Combustível", "tipo": "float"}]},
    "combustivel": {"model": FornecedorCombustivel, "titulo": "Combustível", "campo_equipe": "combustivel_fornecedor_id",
                    "campos": [{"nome": "eficiencia", "label": "Eficiência", "tipo": "float"},
                               {"nome": "aumento_potencia_motor", "label": "% Aumento Potência Motor", "tipo": "float"}]},
    "pneu": {"model": FornecedorPneu, "titulo": "Pneu", "campo_equipe": "pneu_fornecedor_id",
             "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                        {"nome": "desgaste", "label": "Desgaste", "tipo": "float"},
                        {"nome": "categoria_chuva", "label": "Faixa de chuva", "tipo": "string"}]},
    "cambio": {"model": FornecedorCambio, "titulo": "Câmbio", "campo_equipe": "cambio_fornecedor_id",
               "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                          {"nome": "categoria_pista", "label": "Categoria (A-J)", "tipo": "string"}]},
    "suspensao": {"model": FornecedorSuspensao, "titulo": "Suspensão", "campo_equipe": "suspensao_fornecedor_id",
                  "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                             {"nome": "categoria_pista", "label": "Categoria (A-J)", "tipo": "string"}]},
    "engenheiro": {"model": FornecedorEngenheiro, "titulo": "Engenheiro", "campo_equipe": "engenheiro_fornecedor_id",
                   "campos": [{"nome": "nivel", "label": "Nível", "tipo": "int"},
                              {"nome": "eficiencia_exata", "label": "Eficiência exata", "tipo": "float"}]},
}


@app.context_processor
def injetar_globais():
    usuario_id = session.get("usuario_id")
    usuario = Usuario.query.get(usuario_id) if usuario_id else None
    return {
        "usuario_logado": usuario,
        "categorias_fornecedor": FORNECEDORES_CONFIG,
        "temporada_ativa": Temporada.ativa_atual(),
    }


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
        usuario_id = session.get("usuario_id")
        if not usuario_id:
            return redirect(url_for("login"))
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.eh_admin:
            return render_template("acesso_negado.html"), 403
        return view_func(*args, **kwargs)
    return wrapper


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
    redirect_uri = url_for("auth_google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/login/google/callback")
def auth_google_callback():
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


@app.route("/minha-equipe", methods=["GET", "POST"])
@login_requerido
def minha_equipe():
    usuario = Usuario.query.get(session["usuario_id"])
    config_jogo = Configuracao.obter()
    if usuario.equipe:
        carro = usuario.equipe.montar_carro()
        return render_template("minha_equipe.html", equipe=usuario.equipe, carro=carro,
                               custo_montagem=usuario.equipe.custo_total_montagem())
    if request.method == "POST":
        # REGRA 1.2 / 2.2: engenheiro NAO e escolhido pelo jogador.
        # Conta nova ja vem com Engenheiro nivel 1 automatico (chassi/aero gratis).
        # Selecionamos o engenheiro de nivel 1 mais barato disponivel.
        engenheiro_inicial = (
            FornecedorEngenheiro.query.filter_by(ativo=True, nivel=1)
            .order_by(FornecedorEngenheiro.custo_temporada)
            .first()
        )
        if not engenheiro_inicial:
            # Fallback: se nao houver nivel 1 marcado, pega o mais barato de todos.
            engenheiro_inicial = (
                FornecedorEngenheiro.query.filter_by(ativo=True)
                .order_by(FornecedorEngenheiro.custo_temporada)
                .first()
            )
        engenheiro_id_auto = engenheiro_inicial.id if engenheiro_inicial else None

        combustivel_carregado = min(TANQUE_MAXIMO_LITROS, max(0.0, float(request.form["combustivel_carregado"])))
        # Chassi NÃO vem do formulário (é projetado pelo engenheiro nível 1)
        nova_equipe = CarroJogador(
            usuario_id=usuario.id,
            nome=request.form["nome"],
            orcamento=float(config_jogo.orcamento_inicial),
            motor_fornecedor_id=int(request.form["motor_fornecedor_id"]),
            combustivel_fornecedor_id=int(request.form["combustivel_fornecedor_id"]),
            pneu_fornecedor_id=int(request.form["pneu_fornecedor_id"]),
            chassi_fornecedor_id=None,  # legado, sempre nulo em contas novas
            cambio_fornecedor_id=int(request.form["cambio_fornecedor_id"]),
            suspensao_fornecedor_id=int(request.form["suspensao_fornecedor_id"]),
            engenheiro_fornecedor_id=engenheiro_id_auto,  # nível 1 automático
            combustivel_carregado=combustivel_carregado,
        )
        db.session.add(nova_equipe)
        db.session.flush()

        # Cria registro de desenvolvimento com nível 1 (chassi/aero grátis)
        desenvolvimento = Desenvolvimento(
            equipe_id=nova_equipe.id,
            chassi_percentual_aplicado=100.0,
            aero_percentual_aplicado=100.0,
            chassi_percentual_em_construcao=0.0,
            aero_percentual_em_construcao=0.0,
            nivel_engenheiro_projetista=1,
        )
        db.session.add(desenvolvimento)

        custo_contratos = float(nova_equipe.custo_total_contratos() or 0)
        nova_equipe.orcamento = nova_equipe.orcamento - custo_contratos

        custo_montagem_prevista = float(nova_equipe.custo_total_montagem() or 0)
        if nova_equipe.orcamento < custo_montagem_prevista:
            db.session.rollback()
            flash(
                f"Saldo insuficiente. Contratos custaram R$ {custo_contratos:,.2f}, "
                f"mas você precisa de R$ {custo_montagem_prevista:,.2f} pra montar o carro "
                f"pra 1ª corrida. Escolha fornecedores mais baratos.",
                "danger",
            )
            return redirect(url_for("minha_equipe"))

        db.session.commit()
        flash(
            f"Equipe criada! Contratos: R$ {custo_contratos:,.2f}. "
            f"Saldo restante: R$ {nova_equipe.orcamento:,.2f}. "
            f"Você começa com Engenheiro nível 1, chassi e aerodinâmica nível 1 (grátis).",
            "success",
        )
        return redirect(url_for("minha_equipe"))
    return render_template(
        "equipes.html",
        orcamento_inicial=config_jogo.orcamento_inicial,
        motores=FornecedorMotor.query.filter_by(ativo=True).order_by(FornecedorMotor.custo_temporada).all(),
        combustiveis=FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all(),
        pneus=FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all(),
        cambios=FornecedorCambio.query.filter_by(ativo=True).order_by(FornecedorCambio.custo_temporada).all(),
        suspensoes=FornecedorSuspensao.query.filter_by(ativo=True).order_by(FornecedorSuspensao.custo_temporada).all(),
    )



@app.route("/minha-equipe/editar", methods=["GET", "POST"])
@login_requerido
def editar_equipe():
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    equipe = usuario.equipe

    if Temporada.ativa_atual():
        flash("Você não pode trocar fornecedores durante uma temporada ativa. Contratos são anuais.", "warning")
        return redirect(url_for("minha_equipe"))

    if request.method == "POST":
        custo_troca_total = 0.0
        trocas_feitas = []
        for chave, cfg in FORNECEDORES_CONFIG.items():
            campo = cfg["campo_equipe"]
            valor_novo = request.form.get(campo)
            if not valor_novo:
                if chave == "engenheiro" and getattr(equipe, campo) is not None:
                    setattr(equipe, campo, None)
                    trocas_feitas.append(f"{cfg['titulo']} removido")
                continue
            valor_novo = int(valor_novo)
            valor_atual = getattr(equipe, campo)
            if valor_novo != valor_atual:
                novo_fornecedor = cfg["model"].query.get(valor_novo)
                if novo_fornecedor:
                    custo_troca_total += float(novo_fornecedor.custo_temporada or 0)
                    setattr(equipe, campo, valor_novo)
                    trocas_feitas.append(f"{cfg['titulo']}: {novo_fornecedor.nome}")
        try:
            combustivel_carregado = float(request.form.get("combustivel_carregado", equipe.combustivel_carregado))
            equipe.combustivel_carregado = min(TANQUE_MAXIMO_LITROS, max(0.0, combustivel_carregado))
        except (ValueError, TypeError):
            pass
        if trocas_feitas:
            if float(equipe.orcamento) < custo_troca_total:
                db.session.rollback()
                flash(f"Saldo insuficiente pra novos contratos (R$ {custo_troca_total:,.2f}).", "danger")
                return redirect(url_for("editar_equipe"))
            equipe.orcamento = float(equipe.orcamento) - custo_troca_total
            db.session.commit()
            flash(f"Trocas: {'; '.join(trocas_feitas)}. Custo dos novos contratos: R$ {custo_troca_total:,.2f}", "success")
        else:
            flash("Nenhuma troca feita.", "info")
        return redirect(url_for("minha_equipe"))

    return render_template(
        "editar_equipe.html", equipe=equipe,
        motores=FornecedorMotor.query.filter_by(ativo=True).order_by(FornecedorMotor.custo_temporada).all(),
        combustiveis=FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all(),
        pneus=FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all(),
        cambios=FornecedorCambio.query.filter_by(ativo=True).order_by(FornecedorCambio.custo_temporada).all(),
        suspensoes=FornecedorSuspensao.query.filter_by(ativo=True).order_by(FornecedorSuspensao.custo_temporada).all(),
        engenheiros=FornecedorEngenheiro.query.filter_by(ativo=True).order_by(FornecedorEngenheiro.custo_temporada).all(),
    )


@app.route("/minha-equipe/resetar", methods=["POST"])
@login_requerido
def resetar_equipe():
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    equipe_id = usuario.equipe.id
    Desenvolvimento.query.filter_by(equipe_id=equipe_id).delete()
    TreinamentoBox.query.filter_by(equipe_id=equipe_id).delete()
    ResultadoClassificacao.query.filter_by(equipe_id=equipe_id).delete()
    ResultadoCorrida.query.filter_by(equipe_id=equipe_id).delete()
    ResultadoTreinoLivre.query.filter_by(equipe_id=equipe_id).delete()
    db.session.delete(usuario.equipe)
    db.session.commit()
    flash("Conta resetada. Você pode montar sua equipe do zero.", "info")
    return redirect(url_for("minha_equipe"))


@app.route("/minha-equipe/desenvolvimento", methods=["GET", "POST"])
@login_requerido
def desenvolvimento_view():
    """Nova versão: desenvolve chassi + aero separadamente (em construção
    pra próxima temporada)."""
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    equipe = usuario.equipe
    registro = Desenvolvimento.obter_ou_criar(equipe.id)
    config = Configuracao.obter()

    # Verifica se algum trabalho em progresso concluiu
    # Detecta qual peça está sendo trabalhada pela flag em_progresso + em_construcao
    if registro.em_progresso and registro.horario_conclusao and datetime.utcnow() >= registro.horario_conclusao:
        # Aplica ao alvo correspondente (salvo em outro campo? simples: só um por vez)
        # Aqui a gente aplica em "peça em construção" pendente. Como só temos 1 timer,
        # o alvo vem da form (session ou campo em progresso). Simplificação: usa
        # verificar_conclusao no atributo em pauta - guardamos qual é em `alvo_em_progresso`.
        alvo = getattr(registro, "alvo_em_progresso", None) or "chassi_percentual_em_construcao"
        # Aplica manualmente
        atual = float(getattr(registro, alvo, 0) or 0)
        novo = min(100.0, atual + config.dev_incremento_percentual)
        setattr(registro, alvo, novo)
        registro.em_progresso = False
        registro.inicio_em = None
        registro.horario_conclusao = None
        db.session.commit()

    mensagem = None
    if request.method == "POST":
        peca = request.form.get("peca", "chassi")  # chassi ou aero
        if peca not in ("chassi", "aero"):
            peca = "chassi"

        alvo_atributo = f"{peca}_percentual_em_construcao"
        _, mensagem = avancar(
            registro, equipe,
            config.dev_custo_base, config.dev_custo_fator,
            config.dev_tempo_base_horas, config.dev_tempo_fator_horas,
            config.dev_incremento_percentual,
            alvo_atributo=alvo_atributo,
        )
        # Marca qual peça está em progresso pra recuperar depois
        if not hasattr(registro, "alvo_em_progresso"):
            pass  # não tem coluna, é atributo em memória - salva na sessão
        session[f"desenvolvimento_alvo_{equipe.id}"] = alvo_atributo

    proximo_custo_chassi = calcular_custo_proximo_avanco(
        registro.chassi_percentual_em_construcao or 0, config.dev_custo_base, config.dev_custo_fator
    )
    proximo_custo_aero = calcular_custo_proximo_avanco(
        registro.aero_percentual_em_construcao or 0, config.dev_custo_base, config.dev_custo_fator
    )
    proximo_tempo_chassi = calcular_tempo_proximo_avanco_horas(
        registro.chassi_percentual_em_construcao or 0, config.dev_tempo_base_horas, config.dev_tempo_fator_horas
    )
    proximo_tempo_aero = calcular_tempo_proximo_avanco_horas(
        registro.aero_percentual_em_construcao or 0, config.dev_tempo_base_horas, config.dev_tempo_fator_horas
    )

    return render_template("desenvolvimento.html",
        equipe=equipe, registro=registro,
        proximo_custo_chassi=proximo_custo_chassi,
        proximo_custo_aero=proximo_custo_aero,
        proximo_tempo_chassi=proximo_tempo_chassi,
        proximo_tempo_aero=proximo_tempo_aero,
        mensagem=mensagem)


@app.route("/treino-livre", methods=["GET", "POST"])
@login_requerido
def treino_livre_view():
    """TREINO LIVRE REAL (stint de teste, volta a volta).

    REGRA (regras.md 10.1 + decisao Opcao B): o Treino Livre trava direto na
    PROXIMA CORRIDA da temporada ativa. Nao ha dropdown de pistas: o jogador
    so pode treinar pra corrida que vem a seguir no calendario.
    Sem temporada ativa (ou sem proxima corrida), nao ha treino disponivel.
    """
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    equipe = usuario.equipe
    criar_banco_pistas_reais()

    # --- Trava na proxima corrida da temporada ativa (Opcao B) -------------
    pistas_por_id = {p["id"]: p for p in listar_pistas_reais()}
    temporada = Temporada.ativa_atual()
    proxima_corrida = temporada.proxima_corrida() if temporada else None
    pista_atual = None
    if proxima_corrida and proxima_corrida.pista_real_id in pistas_por_id:
        pista_atual = pistas_por_id[proxima_corrida.pista_real_id]

    # Lista com no maximo 1 pista (a proxima corrida). O template usa isso
    # tanto pro <select> travado quanto pra saber se pode treinar.
    pistas = [pista_atual] if pista_atual else []

    pneus = FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all()
    combustiveis = FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all()

    resultado = None
    mensagem = None
    novo_recorde = False

    if not temporada:
        mensagem = "Nenhuma temporada ativa. O treino livre so fica disponivel durante uma temporada."
    elif not pista_atual:
        mensagem = "Nao ha proxima corrida no calendario da temporada ativa. Nada pra treinar."

    # Valores padrao do formulario (a pista ja vem travada na proxima corrida).
    escolhas = {
        "pista_id": (pista_atual["id"] if pista_atual else None),
        "pneu_fornecedor_id": equipe.pneu_fornecedor_id,
        "combustivel_fornecedor_id": equipe.combustivel_fornecedor_id,
        "combustivel_litros": 30.0,
        "modelo_cambio": equipe.modelo_cambio or 500,
        "modelo_suspensao": equipe.modelo_suspensao or 500,
        "modelo_pneu": equipe.modelo_pneu or "",
    }

    if request.method == "POST" and pista_atual:
        def _int(nome, padrao=None):
            valor = request.form.get(nome)
            try:
                return int(valor)
            except (TypeError, ValueError):
                return padrao

        # A pista e SEMPRE a da proxima corrida (ignora o que vier no POST).
        escolhas["pista_id"] = pista_atual["id"]

        escolhas["pneu_fornecedor_id"] = _int("pneu_fornecedor_id", escolhas["pneu_fornecedor_id"])
        escolhas["combustivel_fornecedor_id"] = _int("combustivel_fornecedor_id", escolhas["combustivel_fornecedor_id"])
        try:
            litros = float(request.form.get("combustivel_litros", 30.0))
        except (TypeError, ValueError):
            litros = 30.0
        litros = min(TANQUE_MAXIMO_LITROS, max(1.0, litros))
        escolhas["combustivel_litros"] = litros

        modelo_cambio = _int("modelo_cambio", None)
        modelo_suspensao = _int("modelo_suspensao", None)
        modelo_pneu_raw = request.form.get("modelo_pneu")
        modelo_pneu = (
            int(modelo_pneu_raw)
            if (modelo_pneu_raw and modelos_componente.modelo_valido(modelo_pneu_raw))
            else None
        )
        escolhas["modelo_cambio"] = modelo_cambio or ""
        escolhas["modelo_suspensao"] = modelo_suspensao or ""
        escolhas["modelo_pneu"] = modelo_pneu or ""

        pneu_db = FornecedorPneu.query.get(escolhas["pneu_fornecedor_id"]) or (pneus[0] if pneus else None)
        combustivel_db = FornecedorCombustivel.query.get(escolhas["combustivel_fornecedor_id"]) or (combustiveis[0] if combustiveis else None)
        pista = obter_pista_real(pista_atual["id"])

        if not pneu_db or not combustivel_db:
            mensagem = "Cadastre fornecedores de pneu e combustivel antes de treinar."
        else:
            resultado = simular_treino_livre_real(
                equipe, pneu_db, combustivel_db, litros,
                pista=pista,
                modelo_cambio=modelo_cambio,
                modelo_suspensao=modelo_suspensao,
                modelo_pneu=modelo_pneu,
            )
            _, novo_recorde = ResultadoTreinoLivre.registrar_se_melhor(equipe.id, resultado)
            # Compatibilidade: mantem o fluxo Treino Oficial / Estrategia funcionando.
            session.setdefault("treino_livre_salvo", {
                "ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50,
            })
            if novo_recorde:
                mensagem = "Treino concluido — novo recorde salvo no ranking!"
            else:
                mensagem = "Treino concluido. Nao superou seu melhor tempo; o recorde anterior foi mantido."

    meu_resultado = ResultadoTreinoLivre.query.filter_by(equipe_id=equipe.id).first()
    return render_template(
        "treino_livre.html",
        equipe=equipe, pistas=pistas, pneus=pneus, combustiveis=combustiveis,
        modelos_disponiveis=modelos_componente.MODELOS,
        escolhas=escolhas, resultado=resultado, mensagem=mensagem,
        novo_recorde=novo_recorde, meu_resultado=meu_resultado,
        pista_atual=pista_atual,
    )

@app.route("/treino-livre/ranking")
@login_requerido
def treino_livre_ranking_view():
    """Ranking de treino livre: melhor volta de cada equipe, do mais rápido
    pro mais lento."""
    usuario = Usuario.query.get(session["usuario_id"])
    resultados = (
        ResultadoTreinoLivre.query
        .filter(ResultadoTreinoLivre.melhor_volta_tempo.isnot(None))
        .order_by(ResultadoTreinoLivre.melhor_volta_tempo.asc())
        .all()
    )
    minha_equipe_id = usuario.equipe.id if usuario.equipe else None
    return render_template(
        "treino_livre_ranking.html",
        resultados=resultados, minha_equipe_id=minha_equipe_id,
    )


@app.route("/treino-oficial", methods=["GET", "POST"])
@login_requerido
def treino_oficial_view():
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    ajustes = session.get("treino_livre_salvo") or {"ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                                                     "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50}
    pneus = FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all()
    combustiveis = FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all()
    resultado = None
    mensagem = None
    if not session.get("treino_livre_salvo"):
        mensagem = "Complete primeiro o treino livre."
    if request.method == "POST":
        if not session.get("treino_livre_salvo"):
            return render_template("treino_oficial.html", ajustes=ajustes, pneus=pneus, combustiveis=combustiveis, resultado=None, mensagem=mensagem)
        pneu = FornecedorPneu.query.get(int(request.form.get("pneu_fornecedor_id")))
        combustivel = FornecedorCombustivel.query.get(int(request.form.get("combustivel_fornecedor_id")))
        volta_primeiro_pit = int(request.form.get("volta_primeiro_pit", 10))
        outro_pit = request.form.get("outro_pit") == "on"
        resultado = simular_treino_oficial(ajustes, pneu or pneus[0], combustivel or combustiveis[0], volta_primeiro_pit, outro_pit)
        session["treino_oficial_salvo"] = {
            "pneu_fornecedor_id": request.form.get("pneu_fornecedor_id"),
            "combustivel_fornecedor_id": request.form.get("combustivel_fornecedor_id"),
            "volta_primeiro_pit": volta_primeiro_pit, "outro_pit": outro_pit,
        }
        mensagem = "Treino oficial concluído."
    return render_template("treino_oficial.html", ajustes=ajustes, pneus=pneus, combustiveis=combustiveis, resultado=resultado, mensagem=mensagem)


@app.route("/estrategia-corrida", methods=["GET", "POST"])
@login_requerido
def estrategia_corrida_view():
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    ajustes = session.get("treino_livre_salvo") or {"ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                                                     "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50}
    treino_oficial = session.get("treino_oficial_salvo") or {}
    pneus = FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all()
    combustiveis = FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all()
    resultado = None
    mensagem = None
    sugestao = None
    if request.method == "POST":
        pneu = FornecedorPneu.query.get(int(request.form.get("pneu_fornecedor_id")))
        combustivel = FornecedorCombustivel.query.get(int(request.form.get("combustivel_fornecedor_id")))
        volta_primeiro_pit = int(request.form.get("volta_primeiro_pit", 10))
        outro_pit = request.form.get("outro_pit") == "on"
        resultado = montar_estrategia_corrida(ajustes, pneu or pneus[0], combustivel or combustiveis[0], volta_primeiro_pit, outro_pit)
        sugestao = sugerir_estrategia_estrategista(ajustes)

        # REFACTOR xx-50/xx-900: salva os modelos escolhidos pra próxima corrida.
        # Cada campo é um número 50..900; valores inválidos/vazios são ignorados.
        # Campo vazio "" limpa a escolha (volta ao comportamento antigo).
        campos_modelo = {
            "modelo_motor": request.form.get("modelo_motor"),
            "modelo_combustivel": request.form.get("modelo_combustivel"),
            "modelo_pneu": request.form.get("modelo_pneu"),
            "modelo_cambio": request.form.get("modelo_cambio"),
            "modelo_suspensao": request.form.get("modelo_suspensao"),
        }
        for campo, valor in campos_modelo.items():
            if valor is None:
                continue
            if valor == "":
                setattr(usuario.equipe, campo, None)
            elif modelos_componente.modelo_valido(valor):
                setattr(usuario.equipe, campo, int(valor))
        db.session.commit()

        mensagem = "Estratégia definida."
    return render_template("estrategia_corrida.html", ajustes=ajustes, treino_oficial=treino_oficial,
                           pneus=pneus, combustiveis=combustiveis, resultado=resultado, sugestao=sugestao,
                           mensagem=mensagem, equipe=usuario.equipe,
                           modelos_disponiveis=modelos_componente.MODELOS)


@app.route("/minha-equipe/treinamento", methods=["GET", "POST"])
@login_requerido
def treinamento_view():
    usuario = Usuario.query.get(session["usuario_id"])
    if not usuario.equipe:
        return redirect(url_for("minha_equipe"))
    equipe = usuario.equipe
    registro = TreinamentoBox.obter_ou_criar(equipe.id)
    config = Configuracao.obter()
    verificar_conclusao(registro, config.treino_incremento_percentual)
    mensagem = None
    if request.method == "POST":
        _, mensagem = avancar(registro, equipe, config.treino_custo_base, config.treino_custo_fator,
                              config.treino_tempo_base_horas, config.treino_tempo_fator_horas, config.treino_incremento_percentual)
    proximo_custo = calcular_custo_proximo_avanco(registro.percentual, config.treino_custo_base, config.treino_custo_fator)
    proximo_tempo = calcular_tempo_proximo_avanco_horas(registro.percentual, config.treino_tempo_base_horas, config.treino_tempo_fator_horas)
    tempo_pit_atual = config.pit_tempo_sem_treino - ((config.pit_tempo_sem_treino - config.pit_tempo_treino_completo) * (registro.percentual / 100))
    return render_template("treinamento.html", equipe=equipe, registro=registro,
                           proximo_custo=proximo_custo, proximo_tempo=proximo_tempo, mensagem=mensagem,
                           tempo_pit_atual=round(tempo_pit_atual, 1))


@app.route("/pistas-reais")
def pistas_reais_view():
    criar_banco_pistas_reais()
    pistas = listar_pistas_reais()
    return render_template("pistas_reais.html", pistas=pistas)


@app.route("/temporada")
def temporada_view():
    temporada = Temporada.ativa_atual()
    if not temporada:
        return render_template("temporada.html", temporada=None, ranking=[], pistas_por_id={})
    ranking = ranking_temporada(temporada)
    pistas_por_id = {p["id"]: p for p in listar_pistas_reais()}
    return render_template("temporada.html", temporada=temporada, ranking=ranking, pistas_por_id=pistas_por_id)


@app.route("/classificacao", methods=["GET", "POST"])
@login_requerido
def classificacao_view():
    resultado = None
    if request.method == "POST":
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.eh_admin:
            return render_template("acesso_negado.html"), 403
        todas_equipes = CarroJogador.query.all()
        carros = [equipe_db.montar_carro() for equipe_db in todas_equipes]
        grid = Classificacao(carros).gerar_grid_largada()
        for posicao_info, equipe_db in zip(grid, todas_equipes):
            db.session.add(ResultadoClassificacao(equipe_id=equipe_db.id,
                tempo_classificacao=posicao_info["tempo_classificacao"], posicao_grid=posicao_info["posicao_grid"]))
        db.session.commit()
        resultado = grid
    return render_template("classificacao.html", resultado=resultado)


def _aplicar_dados_pista_no_carro(carro, pista):
    cat_cambio = (pista.get("categoria_cambio_ideal") or "A").upper()
    cat_suspensao = (pista.get("categoria_suspensao_ideal") or "A").upper()
    carro.categoria_cambio_ideal_pista = cat_cambio[0] if cat_cambio else "A"
    carro.categoria_suspensao_ideal_pista = cat_suspensao[0] if cat_suspensao else "A"
    carro.categoria_chuva = "seco"
    carro.temperatura_pista = pista.get("temperatura_trecho_1") or pista.get("temperatura_ambiente") or 20.0
    carro.tamanho_volta_km = pista.get("extensao_km") or 0.0
    carro.influencia_pista_motor = pista.get("influencia_motor") or 10
    carro.influencia_pista_cambio = pista.get("influencia_cambio") or 10
    carro.influencia_pista_suspensao = pista.get("influencia_suspensao") or 10
    carro.influencia_pista_pneu = pista.get("influencia_pneu") or 10
    carro.influencia_pista_combustivel = pista.get("influencia_combustivel") or 10
    carro.influencia_pista_engenheiro = pista.get("influencia_engenheiro") or 10


def _executar_corrida_e_persistir(pista, corrida_agendada=None):
    numero_voltas, distancia_total = calcular_numero_voltas(pista["extensao_km"])
    config = Configuracao.obter()
    todas_equipes = CarroJogador.query.all()
    carros = [equipe_db.montar_carro() for equipe_db in todas_equipes]

    percentuais_treino_box = []
    for carro, equipe_db in zip(carros, todas_equipes):
        treinamento = TreinamentoBox.obter_ou_criar(equipe_db.id)
        carro.tempo_pit_stop = calcular_tempo_pit_stop(pista["tempo_pit_stop_segundos"], config, treinamento.percentual)
        _aplicar_dados_pista_no_carro(carro, pista)
        percentuais_treino_box.append(float(treinamento.percentual or 0.0))

    temp_fallback = pista.get("temperatura_ambiente") or 20.0
    temperaturas_trechos = [
        pista.get("temperatura_trecho_1") or temp_fallback,
        pista.get("temperatura_trecho_2") or temp_fallback,
        pista.get("temperatura_trecho_3") or temp_fallback,
        pista.get("temperatura_trecho_4") or temp_fallback,
    ]

    resultado = Corrida(
        carros,
        total_voltas=numero_voltas,
        temperaturas_trechos=temperaturas_trechos,
        consumo_qualifying=True,
        percentuais_treino_box=percentuais_treino_box,
    ).simular()
    resultado["pista"] = pista
    resultado["distancia_total"] = distancia_total
    resultado["temperaturas_trechos"] = temperaturas_trechos

    equipes_por_nome = {e.nome: e for e in todas_equipes}
    resultados_para_temporada = []

    for posicao_info in resultado["classificacao_final"]:
        equipe_db = equipes_por_nome[posicao_info["equipe"]]
        db.session.add(ResultadoCorrida(
            equipe_id=equipe_db.id,
            tempo_total_segundos=posicao_info["tempo_total_segundos"],
            pit_stops=posicao_info["pit_stops"],
            posicao_final=posicao_info["posicao"],
        ))

        custo_montagem = float(equipe_db.custo_total_montagem() or 0)
        equipe_db.orcamento = float(equipe_db.orcamento or 0) - custo_montagem

        premio = premio_por_posicao(
            posicao_info["posicao"],
            posicao_info.get("abandonou", False),
        )
        equipe_db.orcamento = float(equipe_db.orcamento or 0) + premio

        if corrida_agendada is not None:
            pontos = pontos_por_posicao(
                posicao_info["posicao"],
                posicao_info.get("abandonou", False),
            )
            resultados_para_temporada.append({
                "equipe_id": equipe_db.id,
                "equipe_nome": equipe_db.nome,
                "posicao": posicao_info["posicao"],
                "pontos": pontos,
                "premio": premio,
                "abandonou": posicao_info.get("abandonou", False),
                "motivo_abandono": posicao_info.get("motivo_abandono"),
                "tempo_total": posicao_info["tempo_total_segundos"],
                "custo_montagem": custo_montagem,
            })

    if corrida_agendada is not None:
        corrida_agendada.salvar_resultados(resultados_para_temporada)
        corrida_agendada.executada = True
        corrida_agendada.data_execucao = datetime.utcnow()
    db.session.commit()
    return resultado


@app.route("/corrida", methods=["GET", "POST"])
@login_requerido
def corrida_view():
    resultado = None
    criar_banco_pistas_reais()
    pistas = listar_pistas_reais()
    temporada = Temporada.ativa_atual()
    proxima_corrida_temporada = temporada.proxima_corrida() if temporada else None
    pistas_por_id = {p["id"]: p for p in pistas}
    pista_proxima_temporada = pistas_por_id.get(proxima_corrida_temporada.pista_real_id) if proxima_corrida_temporada else None

    if request.method == "POST":
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.eh_admin:
            return render_template("acesso_negado.html"), 403
        modo_temporada = request.form.get("modo") == "temporada"
        if modo_temporada and proxima_corrida_temporada and pista_proxima_temporada:
            resultado = _executar_corrida_e_persistir(pista_proxima_temporada, corrida_agendada=proxima_corrida_temporada)
            flash(f"Corrida da temporada: {pista_proxima_temporada['nome']}.", "success")
        else:
            pista_id = int(request.form["pista_id"])
            pista = obter_pista_real(pista_id)
            resultado = _executar_corrida_e_persistir(pista, corrida_agendada=None)
            flash(f"Corrida: {pista['nome']}.", "success")
        temporada = Temporada.ativa_atual()
        proxima_corrida_temporada = temporada.proxima_corrida() if temporada else None
        pista_proxima_temporada = pistas_por_id.get(proxima_corrida_temporada.pista_real_id) if proxima_corrida_temporada else None

    return render_template("corrida.html", resultado=resultado, pistas=pistas,
                           temporada=temporada,
                           proxima_corrida_temporada=proxima_corrida_temporada,
                           pista_proxima_temporada=pista_proxima_temporada)


# ---------- ADMIN ----------
@app.route("/admin")
@admin_requerido
def admin_dashboard():
    contagens = {chave: cfg["model"].query.count() for chave, cfg in FORNECEDORES_CONFIG.items()}
    return render_template("admin_dashboard.html",
                           categorias=FORNECEDORES_CONFIG, contagens=contagens,
                           total_temporadas=Temporada.query.count(),
                           total_usuarios=Usuario.query.count())


@app.route("/admin/gerar-fornecedores", methods=["POST"])
@admin_requerido
def admin_gerar_fornecedores():
    popular_banco()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/fornecedores/<categoria>", methods=["GET", "POST"])
@admin_requerido
def admin_fornecedores(categoria):
    cfg = FORNECEDORES_CONFIG[categoria]
    Model = cfg["model"]
    if request.method == "POST":
        dados = {"nome": request.form["nome"], "custo_temporada": float(request.form["custo_temporada"]),
                 "custo_montagem": float(request.form["custo_montagem"]), "ativo": True}
        for campo in cfg["campos"]:
            valor = request.form[campo["nome"]]
            tipo = campo.get("tipo", "string")
            if tipo == "int": dados[campo["nome"]] = int(valor)
            elif tipo == "float": dados[campo["nome"]] = float(valor)
            else: dados[campo["nome"]] = valor
        db.session.add(Model(**dados))
        db.session.commit()
        return redirect(url_for("admin_fornecedores", categoria=categoria))
    pagina = int(request.args.get("pagina", 1))
    por_pagina = 50
    total = Model.query.count()
    itens = Model.query.order_by(Model.custo_temporada).offset((pagina - 1) * por_pagina).limit(por_pagina).all()
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    return render_template("admin_fornecedor_lista.html", categoria=categoria, cfg=cfg, itens=itens,
                           pagina=pagina, total_paginas=total_paginas, total=total,
                           categorias_pista=CATEGORIAS_PISTA, categorias_chuva=CATEGORIAS_CHUVA,
                           categoria_fornecedor_atual=categoria)


@app.route("/admin/fornecedores/<categoria>/<int:item_id>/editar", methods=["GET", "POST"])
@admin_requerido
def admin_fornecedor_editar(categoria, item_id):
    cfg = FORNECEDORES_CONFIG[categoria]
    Model = cfg["model"]
    item = Model.query.get_or_404(item_id)
    if request.method == "POST":
        item.nome = request.form["nome"]
        item.custo_temporada = float(request.form["custo_temporada"])
        item.custo_montagem = float(request.form["custo_montagem"])
        item.ativo = "ativo" in request.form
        for campo in cfg["campos"]:
            valor = request.form[campo["nome"]]
            tipo = campo.get("tipo", "string")
            if tipo == "int": setattr(item, campo["nome"], int(valor))
            elif tipo == "float": setattr(item, campo["nome"], float(valor))
            else: setattr(item, campo["nome"], valor)
        db.session.commit()
        return redirect(url_for("admin_fornecedores", categoria=categoria))
    return render_template("admin_fornecedor_editar.html", categoria=categoria, cfg=cfg, item=item,
                           categorias_pista=CATEGORIAS_PISTA, categorias_chuva=CATEGORIAS_CHUVA,
                           categoria_fornecedor_atual=categoria)


@app.route("/admin/pistas-reais")
@admin_requerido
def admin_pistas_reais():
    criar_banco_pistas_reais()
    return render_template("admin_pistas_reais.html", pistas=listar_pistas_reais())


@app.route("/admin/pistas-reais/<int:pista_id>/editar", methods=["GET", "POST"])
@admin_requerido
def admin_pista_editar(pista_id):
    criar_banco_pistas_reais()
    pista = obter_pista_real(pista_id)
    if not pista:
        return redirect(url_for("admin_pistas_reais"))
    if request.method == "POST":
        cat_cambio = (request.form.get("categoria_cambio_ideal") or "A").upper()
        cat_suspensao = (request.form.get("categoria_suspensao_ideal") or "A").upper()
        campos = {
            "tempo_pit_stop_segundos": float(request.form["tempo_pit_stop_segundos"]),
            "categoria_cambio_ideal": cat_cambio[0] if cat_cambio else "A",
            "categoria_suspensao_ideal": cat_suspensao[0] if cat_suspensao else "A",
            "influencia_motor": int(request.form["influencia_motor"]),
            "influencia_cambio": int(request.form["influencia_cambio"]),
            "influencia_suspensao": int(request.form["influencia_suspensao"]),
            "influencia_pneu": int(request.form["influencia_pneu"]),
            "influencia_combustivel": int(request.form["influencia_combustivel"]),
            "influencia_engenheiro": int(request.form["influencia_engenheiro"]),
            "temperatura_trecho_1": float(request.form["temperatura_trecho_1"]),
            "temperatura_trecho_2": float(request.form["temperatura_trecho_2"]),
            "temperatura_trecho_3": float(request.form["temperatura_trecho_3"]),
            "temperatura_trecho_4": float(request.form["temperatura_trecho_4"]),
        }
        atualizar_pista_real(pista_id, **campos)
        return redirect(url_for("admin_pistas_reais"))
    return render_template("admin_pista_editar.html", pista=pista, categorias_pista=CATEGORIAS_PISTA)


@app.route("/admin/temporadas", methods=["GET", "POST"])
@admin_requerido
def admin_temporadas():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if nome:
            nova = Temporada(nome=nome, ativa=False)
            db.session.add(nova)
            db.session.commit()
            flash(f"Temporada '{nome}' criada.", "success")
            return redirect(url_for("admin_temporada_editar", temporada_id=nova.id))
    temporadas = Temporada.query.order_by(Temporada.data_criacao.desc()).all()
    return render_template("admin_temporadas.html", temporadas=temporadas)


@app.route("/admin/temporadas/<int:temporada_id>/editar", methods=["GET", "POST"])
@admin_requerido
def admin_temporada_editar(temporada_id):
    temporada = Temporada.query.get_or_404(temporada_id)
    criar_banco_pistas_reais()
    pistas = listar_pistas_reais()
    pistas_por_id = {p["id"]: p for p in pistas}
    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "adicionar_pista":
            pista_id = int(request.form["pista_id"])
            pista = pistas_por_id.get(pista_id)
            if pista:
                proxima_ordem = max((c.ordem for c in temporada.corridas_agendadas), default=0) + 1
                db.session.add(CorridaAgendada(temporada_id=temporada.id, pista_real_id=pista_id,
                                                pista_nome=pista["nome"], ordem=proxima_ordem))
                db.session.commit()
                flash(f"Pista '{pista['nome']}' adicionada.", "success")
        elif acao == "renomear":
            novo_nome = request.form.get("nome", "").strip()
            if novo_nome:
                temporada.nome = novo_nome
                db.session.commit()
                flash("Nome atualizado.", "success")
        return redirect(url_for("admin_temporada_editar", temporada_id=temporada.id))
    return render_template("admin_temporada_editar.html", temporada=temporada, pistas=pistas, pistas_por_id=pistas_por_id)


@app.route("/admin/temporadas/<int:temporada_id>/ativar", methods=["POST"])
@admin_requerido
def admin_temporada_ativar(temporada_id):
    Temporada.query.update({"ativa": False})
    temporada = Temporada.query.get_or_404(temporada_id)
    temporada.ativa = True
    db.session.commit()
    flash(f"Temporada '{temporada.nome}' ativa.", "success")
    return redirect(url_for("admin_temporadas"))


@app.route("/admin/temporadas/<int:temporada_id>/desativar", methods=["POST"])
@admin_requerido
def admin_temporada_desativar(temporada_id):
    """Desativa a temporada E aplica o desenvolvimento (chassi+aero em construção)
    de todos os jogadores. Quem não completou os requisitos fica sem carro
    pra próxima temporada."""
    temporada = Temporada.query.get_or_404(temporada_id)
    temporada.ativa = False

    # Aplicar desenvolvimento pra todos os jogadores
    equipes = CarroJogador.query.all()
    aplicados = 0
    bloqueados = 0
    for equipe in equipes:
        desenvolvimento = Desenvolvimento.obter_ou_criar(equipe.id)
        engenheiro = None
        if equipe.engenheiro_fornecedor_id:
            engenheiro = FornecedorEngenheiro.query.get(equipe.engenheiro_fornecedor_id)
        resultado_dev = aplicar_desenvolvimento_da_temporada(desenvolvimento, engenheiro)
        if resultado_dev["aplicado"]:
            aplicados += 1
        else:
            bloqueados += 1

    db.session.commit()
    flash(
        f"Temporada '{temporada.nome}' desativada. "
        f"Chassi/aero aplicado em {aplicados} equipe(s). "
        f"{bloqueados} equipe(s) não completou os requisitos (chassi/aero em construção zerado, começam próxima temporada com o que tinham).",
        "info",
    )
    return redirect(url_for("admin_temporadas"))


@app.route("/admin/temporadas/corrida/<int:corrida_id>/remover", methods=["POST"])
@admin_requerido
def admin_temporada_remover_corrida(corrida_id):
    corrida = CorridaAgendada.query.get_or_404(corrida_id)
    if corrida.executada:
        flash("Não é possível remover corrida executada.", "warning")
        return redirect(url_for("admin_temporada_editar", temporada_id=corrida.temporada_id))
    temporada_id = corrida.temporada_id
    db.session.delete(corrida)
    db.session.commit()
    flash("Corrida removida.", "info")
    return redirect(url_for("admin_temporada_editar", temporada_id=temporada_id))


@app.route("/admin/usuarios", methods=["GET"])
@admin_requerido
def admin_usuarios():
    filtro_grupo = request.args.get("grupo", "").strip()
    filtro_classe = request.args.get("classe", "").strip()
    filtro_email = request.args.get("email", "").strip()
    query = Usuario.query
    if filtro_grupo: query = query.filter(Usuario.grupo == filtro_grupo)
    if filtro_classe: query = query.filter(Usuario.classe == filtro_classe)
    if filtro_email: query = query.filter(Usuario.email.ilike(f"%{filtro_email}%"))
    usuarios = query.order_by(Usuario.email).all()
    grupos_existentes = sorted({u.grupo for u in Usuario.query.all() if u.grupo})
    classes_existentes = sorted({u.classe for u in Usuario.query.all() if u.classe})
    return render_template("admin_usuarios.html", usuarios=usuarios,
                           grupos_existentes=grupos_existentes, classes_existentes=classes_existentes,
                           filtro_grupo=filtro_grupo, filtro_classe=filtro_classe, filtro_email=filtro_email)


@app.route("/admin/usuarios/<int:usuario_id>/editar", methods=["POST"])
@admin_requerido
def admin_usuario_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.grupo = (request.form.get("grupo") or "").strip() or None
    usuario.classe = (request.form.get("classe") or "").strip() or None
    if "eh_admin" in request.form:
        usuario.eh_admin = request.form.get("eh_admin") == "1"
    db.session.commit()
    flash(f"Usuário {usuario.email} atualizado.", "success")
    return redirect(url_for("admin_usuarios", grupo=request.args.get("grupo", ""),
                            classe=request.args.get("classe", ""), email=request.args.get("email", "")))


@app.route("/admin/configuracoes", methods=["GET", "POST"])
@admin_requerido
def admin_configuracoes():
    config = Configuracao.obter()
    if request.method == "POST":
        campos_float = [
            "orcamento_inicial",
            "dev_incremento_percentual", "dev_tempo_base_horas", "dev_tempo_fator_horas",
            "dev_custo_base", "dev_custo_fator",
            "treino_incremento_percentual", "treino_tempo_base_horas", "treino_tempo_fator_horas",
            "treino_custo_base", "treino_custo_fator",
            "pit_tempo_sem_treino", "pit_tempo_treino_completo",
        ]
        for campo in campos_float:
            setattr(config, campo, float(request.form[campo]))
        db.session.commit()
        flash("Configurações salvas.", "success")
        return redirect(url_for("admin_configuracoes"))
    return render_template("admin_configuracoes.html", config=config)


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco inicializado!")


@app.cli.command("tornar-admin")
@click.argument("email")
def tornar_admin(email):
    usuario = Usuario.query.filter_by(email=email.strip().lower()).first()
    if not usuario:
        print(f"Nenhum usuário com {email}.")
        return
    usuario.eh_admin = True
    db.session.commit()
    print(f"{email} agora é admin!")


if __name__ == "__main__":
    app.run(debug=True)
