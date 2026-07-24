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
