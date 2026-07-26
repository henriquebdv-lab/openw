"""
Rotas da equipe do jogador:
- /minha-equipe            (ver / criar equipe)
- /minha-equipe/editar     (trocar fornecedores fora de temporada)
- /minha-equipe/resetar    (apagar equipe e recomeçar)
"""
from flask import render_template, request, redirect, url_for, session, flash

from constantes import TANQUE_MAXIMO_LITROS
from models import (
    db, Usuario, CarroJogador, Configuracao, Desenvolvimento, TreinamentoBox,
    ResultadoClassificacao, ResultadoCorrida, ResultadoTreinoLivre,
    FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorCambio, FornecedorSuspensao, FornecedorEngenheiro,
)
from models_temporada import Temporada
from extensoes import login_requerido
from fornecedores_config import FORNECEDORES_CONFIG


def _fornecedores_ativos():
    """Listas de fornecedores ativos ordenados por custo (usadas nos forms)."""
    return dict(
        motores=FornecedorMotor.query.filter_by(ativo=True).order_by(FornecedorMotor.custo_temporada).all(),
        combustiveis=FornecedorCombustivel.query.filter_by(ativo=True).order_by(FornecedorCombustivel.custo_temporada).all(),
        pneus=FornecedorPneu.query.filter_by(ativo=True).order_by(FornecedorPneu.custo_temporada).all(),
        cambios=FornecedorCambio.query.filter_by(ativo=True).order_by(FornecedorCambio.custo_temporada).all(),
        suspensoes=FornecedorSuspensao.query.filter_by(ativo=True).order_by(FornecedorSuspensao.custo_temporada).all(),
        engenheiros=FornecedorEngenheiro.query.filter_by(ativo=True).order_by(FornecedorEngenheiro.custo_temporada).all(),
    )


def registrar(app):

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
            engenheiro_id = request.form.get("engenheiro_fornecedor_id")
            
            # CORREÇÃO: Força a contratação de um engenheiro nível 1 se não vier no form
            if not engenheiro_id:
                eng_basico = FornecedorEngenheiro.query.filter_by(nivel=1, ativo=True).first()
                engenheiro_id = eng_basico.id if eng_basico else None

            combustivel_carregado = TANQUE_MAXIMO_LITROS  # padrao: tanque cheio (campo removido da tela)
            nova_equipe = CarroJogador(
                usuario_id=usuario.id,
                nome=request.form["nome"],
                orcamento=float(config_jogo.orcamento_inicial),
                motor_fornecedor_id=int(request.form["motor_fornecedor_id"]),
                combustivel_fornecedor_id=int(request.form["combustivel_fornecedor_id"]),
                pneu_fornecedor_id=int(request.form["pneu_fornecedor_id"]),
                chassi_fornecedor_id=None,
                cambio_fornecedor_id=int(request.form["cambio_fornecedor_id"]),
                suspensao_fornecedor_id=int(request.form["suspensao_fornecedor_id"]),
                engenheiro_fornecedor_id=int(engenheiro_id) if engenheiro_id else None,
                combustivel_carregado=combustivel_carregado,
            )
            db.session.add(nova_equipe)
            db.session.flush()
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
                f"Você começa com chassi e aerodinâmica de nível 1 (grátis).",
                "success",
            )
            return redirect(url_for("minha_equipe"))
        return render_template(
            "equipes.html",
            orcamento_inicial=config_jogo.orcamento_inicial,
            **_fornecedores_ativos(),
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
        return render_template("editar_equipe.html", equipe=equipe, **_fornecedores_ativos())

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