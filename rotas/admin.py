"""
Rotas de administração (/admin/...):
- dashboard, dia_corrida, gerar fornecedores, CRUD de fornecedores
- pistas reais (editar)
- temporadas (criar, editar, ativar, desativar, remover corrida)
- usuários (listar, editar)
- configurações de balanceamento
- evento especial (novo)
"""
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash

from models import db, Usuario, CarroJogador, Configuracao, Desenvolvimento, FornecedorEngenheiro, ResultadoClassificacao, SetupFimDeSemana, DadosClassificacao, EstrategiaStint
from models_temporada import Temporada, CorridaAgendada
from extensoes import admin_requerido
from fornecedores_config import FORNECEDORES_CONFIG, CATEGORIAS_PISTA, CATEGORIAS_CHUVA
from seed_fornecedores import popular_banco
from progressao import aplicar_desenvolvimento_da_temporada
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais, obter_pista_real, atualizar_pista_real,
)
from classificacao import Classificacao
from rotas.corrida import _executar_corrida_e_persistir


def registrar(app):

    @app.route("/admin")
    @admin_requerido
    def admin_dashboard():
        contagens = {chave: cfg["model"].query.count() for chave, cfg in FORNECEDORES_CONFIG.items()}
        return render_template("admin_dashboard.html",
                               categorias=FORNECEDORES_CONFIG, contagens=contagens,
                               total_temporadas=Temporada.query.count(),
                               total_usuarios=Usuario.query.count())

    @app.route("/admin/dia-corrida", methods=["GET", "POST"])
    @admin_requerido
    def admin_dia_corrida():
        temporada = Temporada.ativa_atual()
        proxima_corrida_temporada = temporada.proxima_corrida() if temporada else None
        
        criar_banco_pistas_reais()
        pistas = listar_pistas_reais()
        pistas_por_id = {p["id"]: p for p in pistas}
        pista_proxima_temporada = pistas_por_id.get(proxima_corrida_temporada.pista_real_id) if proxima_corrida_temporada else None

        # --- LÓGICA DE STATUS DAS EQUIPES ---
        todas_equipes = CarroJogador.query.all()
        status_equipes = []
        equipes_prontas = []

        if proxima_corrida_temporada:
            for eq in todas_equipes:
                setup = SetupFimDeSemana.query.filter_by(equipe_id=eq.id, corrida_id=proxima_corrida_temporada.id).first()
                quali = DadosClassificacao.query.filter_by(equipe_id=eq.id, corrida_id=proxima_corrida_temporada.id).first()
                tem_stints = len(eq.stints) > 0

                pronta = bool(setup and setup.travado and quali and tem_stints)
                if pronta:
                    equipes_prontas.append(eq)

                status_equipes.append({
                    "equipe": eq,
                    "setup": setup,
                    "quali": quali,
                    "stints": tem_stints,
                    "pronta": pronta
                })

        ja_classificou = False
        if proxima_corrida_temporada:
             ja_classificou = ResultadoClassificacao.query.count() > 0
        ja_correu = proxima_corrida_temporada.executada if proxima_corrida_temporada else False

        if request.method == "POST":
            acao = request.form.get("acao")
            
            if acao == "classificacao":
                if not proxima_corrida_temporada:
                    flash("Não há corrida pendente.", "danger")
                    return redirect(url_for('admin_dia_corrida'))
                if ja_classificou:
                    flash("A classificação já foi rodada para esta etapa.", "warning")
                    return redirect(url_for('admin_dia_corrida'))
                if not equipes_prontas:
                    flash("Nenhuma equipe cumpriu os requisitos para classificar.", "danger")
                    return redirect(url_for('admin_dia_corrida'))

                # Limpa a classificação anterior para a tela do jogador refletir o novo grid
                ResultadoClassificacao.query.delete()
                
                carros = []
                for eq in equipes_prontas:
                    setup = SetupFimDeSemana.query.filter_by(equipe_id=eq.id, corrida_id=proxima_corrida_temporada.id).first()
                    quali = DadosClassificacao.query.filter_by(equipe_id=eq.id, corrida_id=proxima_corrida_temporada.id).first()
                    
                    carro = eq.montar_carro()
                    carro.definir_modelos(
                        motor=setup.modelo_motor,
                        cambio=setup.modelo_cambio,
                        suspensao=setup.modelo_suspensao,
                        pneu=quali.modelo_pneu
                    )
                    carro.combustivel_carregado = quali.combustivel_litros
                    carros.append(carro)

                grid = Classificacao(carros).gerar_grid_largada()
                
                for posicao_info in grid:
                    eq_nome = posicao_info["equipe"]
                    eq_obj = next(e for e in equipes_prontas if e.nome == eq_nome)
                    db.session.add(ResultadoClassificacao(
                        equipe_id=eq_obj.id,
                        tempo_classificacao=posicao_info["tempo_classificacao"],
                        posicao_grid=posicao_info["posicao_grid"]
                    ))
                db.session.commit()
                flash("Classificação rodada com sucesso! O grid já está disponível.", "success")
                return redirect(url_for('admin_dia_corrida'))
                
            elif acao == "corrida_temporada":
                if not proxima_corrida_temporada or not pista_proxima_temporada:
                    flash("Não há corrida pendente nesta temporada.", "danger")
                    return redirect(url_for('admin_dia_corrida'))
                if not ja_classificou:
                    flash("Você precisa rodar a Classificação antes da Corrida.", "warning")
                    return redirect(url_for('admin_dia_corrida'))
                if ja_correu:
                    flash("Esta corrida já foi executada.", "warning")
                    return redirect(url_for('admin_dia_corrida'))
                if not equipes_prontas:
                    flash("Nenhuma equipe pronta para correr.", "danger")
                    return redirect(url_for('admin_dia_corrida'))

                _executar_corrida_e_persistir(
                    pista_proxima_temporada, 
                    corrida_agendada=proxima_corrida_temporada,
                    equipes_elegiveis=equipes_prontas
                )
                flash(f"Corrida oficial ({pista_proxima_temporada['nome']}) rodada com sucesso! Resultados liberados.", "success")
                return redirect(url_for('admin_dia_corrida'))
                    
            elif acao == "corrida_livre":
                pista_id = request.form.get("pista_id")
                if pista_id:
                    p = obter_pista_real(int(pista_id))
                    if p:
                        _executar_corrida_e_persistir(p, corrida_agendada=None)
                        flash(f"Corrida Livre ({p['nome']}) simulada com sucesso!", "success")
                return redirect(url_for('admin_dia_corrida'))
            
        resultados_classi = []
        if ja_classificou:
            resultados_classi = ResultadoClassificacao.query.order_by(ResultadoClassificacao.posicao_grid).all()

        return render_template("admin_dia_corrida.html", 
                               temporada=temporada,
                               proxima_corrida_temporada=proxima_corrida_temporada,
                               pista_proxima_temporada=pista_proxima_temporada,
                               pistas=pistas,
                               status_equipes=status_equipes,
                               ja_classificou=ja_classificou,
                               ja_correu=ja_correu,
                               resultados_classi=resultados_classi)

    @app.route("/admin/evento-especial", methods=["GET", "POST"])
    @admin_requerido
    def admin_evento_especial():
        """Nova rota: Corrida totalmente customizada ignorando limites do jogo."""
        criar_banco_pistas_reais()
        pistas = listar_pistas_reais()
        
        if request.method == "POST":
            pista_id = request.form.get("pista_id")
            voltas_custom = request.form.get("voltas")
            
            if pista_id and voltas_custom:
                p = obter_pista_real(int(pista_id))
                if p:
                    # Roda o simulador com a quantidade exata de voltas (sem contar para a temporada ativa)
                    _executar_corrida_e_persistir(p, corrida_agendada=None, voltas_customizadas=int(voltas_custom))
                    flash(f"🏁 Evento Especial em {p['nome']} concluído! O replay com {voltas_custom} voltas já está disponível na aba Corrida.", "success")
            return redirect(url_for('admin_evento_especial'))
            
        return render_template("admin_evento_especial.html", pistas=pistas)

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
        temporada = Temporada.query.get_or_404(temporada_id)
        temporada.ativa = False
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
            f"{bloqueados} equipe(s) não completou os requisitos.",
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
                "premio_corrida_pos_1", "multiplicador_consumo", "chance_quebra_base", "chance_quebra_minima"
            ]
            for campo in campos_float:
                setattr(config, campo, float(request.form[campo]))
            db.session.commit()
            flash("Configurações salvas.", "success")
            return redirect(url_for("admin_configuracoes"))
        return render_template("admin_configuracoes.html", config=config)