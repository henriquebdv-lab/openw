"""
Tabelas do banco de dados.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def garantir_colunas_fornecedores():
    from sqlalchemy import text
    try:
        with db.engine.begin() as conexao:
            for tabela, coluna, definicao in [
                ("fornecedores_pneu", "categoria_chuva", "TEXT DEFAULT 'seco'"),
                ("fornecedores_cambio", "categoria_pista", "TEXT DEFAULT 'A'"),
                ("fornecedores_suspensao", "categoria_pista", "TEXT DEFAULT 'A'"),
                ("fornecedores_engenheiro", "eficiencia_exata", "REAL DEFAULT 0.0"),
                ("usuarios", "grupo", "TEXT"),
                ("usuarios", "classe", "TEXT"),
                ("configuracao", "orcamento_inicial", "REAL DEFAULT 55000.0"),
                # Chassi/Aero: novos campos do Desenvolvimento
                ("desenvolvimentos", "chassi_percentual_aplicado", "REAL DEFAULT 100.0"),
                ("desenvolvimentos", "chassi_percentual_em_construcao", "REAL DEFAULT 0.0"),
                ("desenvolvimentos", "aero_percentual_aplicado", "REAL DEFAULT 100.0"),
                ("desenvolvimentos", "aero_percentual_em_construcao", "REAL DEFAULT 0.0"),
                ("desenvolvimentos", "nivel_engenheiro_projetista", "INTEGER DEFAULT 1"),
                # CarroJogador: chassi_fornecedor_id vira opcional (legado)
            ]:
                try:
                    conexao.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"))
                except Exception as erro:
                    mensagem = str(erro).lower()
                    if (
                        "duplicate column name" not in mensagem
                        and "already exists" not in mensagem
                        and "duplicate column" not in mensagem
                        and "no such table" not in mensagem
                    ):
                        raise
    except Exception:
        pass


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    eh_admin = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    grupo = db.Column(db.String(50), nullable=True)
    classe = db.Column(db.String(50), nullable=True)

    equipe = db.relationship("CarroJogador", backref="usuario", uselist=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, senha)


class FornecedorMotor(db.Model):
    __tablename__ = "fornecedores_motor"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    potencia = db.Column(db.Float, default=0.0)
    eficiencia_combustivel = db.Column(db.Float, default=0.0)


class FornecedorCombustivel(db.Model):
    __tablename__ = "fornecedores_combustivel"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    eficiencia = db.Column(db.Float, default=0.0)
    aumento_potencia_motor = db.Column(db.Float, default=0.0)


class FornecedorPneu(db.Model):
    __tablename__ = "fornecedores_pneu"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    performance = db.Column(db.Float, default=0.0)
    desgaste = db.Column(db.Float, default=1.8)
    categoria_chuva = db.Column(db.String(20), default="seco")


class FornecedorChassi(db.Model):
    """LEGADO: mantido no banco por compatibilidade, mas não é mais usado.
    Chassi agora é projetado pelo Engenheiro contratado (regra do manual)."""
    __tablename__ = "fornecedores_chassi"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    performance = db.Column(db.Float, default=0.0)


class FornecedorCambio(db.Model):
    __tablename__ = "fornecedores_cambio"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    performance = db.Column(db.Float, default=0.0)
    categoria_pista = db.Column(db.String(2), default="A")


class FornecedorSuspensao(db.Model):
    __tablename__ = "fornecedores_suspensao"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    performance = db.Column(db.Float, default=0.0)
    categoria_pista = db.Column(db.String(2), default="A")


class FornecedorEngenheiro(db.Model):
    __tablename__ = "fornecedores_engenheiro"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    custo_temporada = db.Column(db.Float, default=0.0)
    custo_montagem = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    nivel = db.Column(db.Integer, default=1)
    eficiencia_exata = db.Column(db.Float, default=0.0)


class Configuracao(db.Model):
    __tablename__ = "configuracao"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_inicial = db.Column(db.Float, default=55_000.0)

    dev_incremento_percentual = db.Column(db.Float, default=5.0)
    dev_tempo_base_horas = db.Column(db.Float, default=1.0)
    dev_tempo_fator_horas = db.Column(db.Float, default=10.0)
    dev_custo_base = db.Column(db.Float, default=50_000.0)
    dev_custo_fator = db.Column(db.Float, default=1.0)
    treino_incremento_percentual = db.Column(db.Float, default=5.0)
    treino_tempo_base_horas = db.Column(db.Float, default=1.0)
    treino_tempo_fator_horas = db.Column(db.Float, default=6.0)
    treino_custo_base = db.Column(db.Float, default=30_000.0)
    treino_custo_fator = db.Column(db.Float, default=1.0)
    pit_tempo_sem_treino = db.Column(db.Float, default=25.0)
    pit_tempo_treino_completo = db.Column(db.Float, default=9.0)

    @classmethod
    def obter(cls):
        config = cls.query.get(1)
        if not config:
            config = cls(id=1)
            db.session.add(config)
            db.session.commit()
        return config


class Desenvolvimento(db.Model):
    """Progresso de chassi + aerodinâmica de um jogador.

    Regra do manual:
    - Chassi e aero são projetados pelo Engenheiro contratado.
    - Cada um vai de 0 a 100%.
    - O que está EM CONSTRUÇÃO durante a temporada só passa a valer
      NA PRÓXIMA temporada, quando o admin fecha a temporada e o
      sistema aplica os projetos concluídos.
    - Para participar da próxima temporada, chassi + aero precisam
      chegar a 100% até o fim da temporada atual.
    - Jogador novo recebe chassi + aero de nível 1, 100% aplicado.
    """
    __tablename__ = "desenvolvimentos"

    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("carros_jogadores.id"), unique=True, nullable=False)

    # Campo legado (ainda usado em bancos antigos)
    percentual = db.Column(db.Float, default=0.0)

    # Chassi
    chassi_percentual_aplicado = db.Column(db.Float, default=100.0)      # o que o carro USA nas corridas
    chassi_percentual_em_construcao = db.Column(db.Float, default=0.0)    # o que o engenheiro está construindo

    # Aerodinâmica
    aero_percentual_aplicado = db.Column(db.Float, default=100.0)
    aero_percentual_em_construcao = db.Column(db.Float, default=0.0)

    # Nível do engenheiro que projetou o chassi/aero atualmente aplicado.
    # Define a performance máxima. Jogador novo começa com 1.
    nivel_engenheiro_projetista = db.Column(db.Integer, default=1)

    em_progresso = db.Column(db.Boolean, default=False)
    inicio_em = db.Column(db.DateTime, nullable=True)
    horario_conclusao = db.Column(db.DateTime, nullable=True)

    @classmethod
    def obter_ou_criar(cls, equipe_id):
        registro = cls.query.filter_by(equipe_id=equipe_id).first()
        if not registro:
            registro = cls(equipe_id=equipe_id)
            db.session.add(registro)
            db.session.commit()
        return registro


class TreinamentoBox(db.Model):
    __tablename__ = "treinamentos_box"
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("carros_jogadores.id"), unique=True, nullable=False)
    percentual = db.Column(db.Float, default=0.0)
    em_progresso = db.Column(db.Boolean, default=False)
    inicio_em = db.Column(db.DateTime, nullable=True)
    horario_conclusao = db.Column(db.DateTime, nullable=True)

    @classmethod
    def obter_ou_criar(cls, equipe_id):
        registro = cls.query.filter_by(equipe_id=equipe_id).first()
        if not registro:
            registro = cls(equipe_id=equipe_id)
            db.session.add(registro)
            db.session.commit()
        return registro


class CarroJogador(db.Model):
    """Representa o CARRO INDIVIDUAL de um jogador.

    Regra nova:
    - Chassi NÃO é mais contrato com fornecedor. É projetado pelo
      Engenheiro. Por isso `chassi_fornecedor_id` virou opcional
      (legado, mantido pra bancos antigos).
    - A performance do chassi vem do Desenvolvimento + nível do
      engenheiro que projetou.
    """
    __tablename__ = "carros_jogadores"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    orcamento = db.Column(db.Float, default=55_000.0)

    motor_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_motor.id"), nullable=False)
    combustivel_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_combustivel.id"), nullable=False)
    pneu_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_pneu.id"), nullable=False)
    # Legado: pode ser NULL agora
    chassi_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_chassi.id"), nullable=True)
    cambio_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_cambio.id"), nullable=False)
    suspensao_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_suspensao.id"), nullable=False)
    engenheiro_fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores_engenheiro.id"), nullable=True)

    combustivel_carregado = db.Column(db.Float, default=110.0)
    cor_primaria = db.Column(db.String(7), default="#cc0000")
    cor_secundaria = db.Column(db.String(7), default="#ffffff")

    def montar_carro(self):
        from equipamentos import Motor, Combustivel, Pneu, Chassi, Cambio, Suspensao, Engenheiro
        from equipe import Equipe
        from carro import Carro
        from constantes import performance_chassi_do_nivel

        motor_db = FornecedorMotor.query.get(self.motor_fornecedor_id)
        combustivel_db = FornecedorCombustivel.query.get(self.combustivel_fornecedor_id)
        pneu_db = FornecedorPneu.query.get(self.pneu_fornecedor_id)
        cambio_db = FornecedorCambio.query.get(self.cambio_fornecedor_id)
        suspensao_db = FornecedorSuspensao.query.get(self.suspensao_fornecedor_id)
        engenheiro_db = (
            FornecedorEngenheiro.query.get(self.engenheiro_fornecedor_id)
            if self.engenheiro_fornecedor_id else None
        )

        equipe = Equipe(self.nome, self.orcamento)
        motor = Motor(motor_db.nome, motor_db.custo_temporada, motor_db.potencia, motor_db.eficiencia_combustivel)
        combustivel = Combustivel(combustivel_db.nome, combustivel_db.custo_temporada, combustivel_db.eficiencia,
                                   combustivel_db.aumento_potencia_motor)
        pneu = Pneu(pneu_db.nome, pneu_db.custo_temporada, pneu_db.performance, pneu_db.desgaste,
                    categoria_chuva=getattr(pneu_db, "categoria_chuva", "seco") or "seco")

        # Chassi: performance vem do nível do engenheiro projetista + percentual aplicado
        desenvolvimento = Desenvolvimento.obter_ou_criar(self.id)
        performance_chassi_base = performance_chassi_do_nivel(desenvolvimento.nivel_engenheiro_projetista or 1)
        performance_chassi_efetiva = performance_chassi_base * (
            (desenvolvimento.chassi_percentual_aplicado or 0) / 100.0
        )
        chassi = Chassi(
            nome=f"Chassi nível {desenvolvimento.nivel_engenheiro_projetista or 1}",
            custo=0.0,
            performance=performance_chassi_efetiva,
        )

        cambio = Cambio(cambio_db.nome, cambio_db.custo_temporada, cambio_db.performance,
                        categoria_pista=getattr(cambio_db, "categoria_pista", "A") or "A")
        suspensao = Suspensao(suspensao_db.nome, suspensao_db.custo_temporada, suspensao_db.performance,
                              categoria_pista=getattr(suspensao_db, "categoria_pista", "A") or "A")

        engenheiro = None
        if engenheiro_db:
            # Efeito antigo (eficiência exata usada em consumo/desgaste).
            # A performance do CHASSI já foi aplicada acima usando o nível do
            # engenheiro projetista, então aqui só passamos a eficiência efetiva
            # zerada (compat) ou usamos como efeito auxiliar.
            eficiencia_efetiva = 0.0
            engenheiro = Engenheiro(engenheiro_db.nome, engenheiro_db.custo_temporada,
                                     engenheiro_db.nivel, eficiencia_efetiva)

        config = Configuracao.obter()
        treinamento = TreinamentoBox.obter_ou_criar(self.id)
        tempo_pit_stop = config.pit_tempo_sem_treino - (
            (config.pit_tempo_sem_treino - config.pit_tempo_treino_completo) * (treinamento.percentual / 100)
        )

        carro_obj = Carro(
            equipe=equipe, motor=motor, combustivel=combustivel, pneu=pneu, chassi=chassi,
            cambio=cambio, suspensao=suspensao, engenheiro=engenheiro,
            combustivel_carregado=self.combustivel_carregado, tempo_pit_stop=tempo_pit_stop,
        )

        # Aero: performance somada como bônus separado no carro
        from constantes import performance_aero_do_nivel
        performance_aero_base = performance_aero_do_nivel(desenvolvimento.nivel_engenheiro_projetista or 1)
        carro_obj.performance_aero = performance_aero_base * (
            (desenvolvimento.aero_percentual_aplicado or 0) / 100.0
        )

        return carro_obj

    def custo_total_montagem(self):
        total = 0.0
        for modelo, campo_id in [
            (FornecedorMotor, self.motor_fornecedor_id),
            (FornecedorCombustivel, self.combustivel_fornecedor_id),
            (FornecedorPneu, self.pneu_fornecedor_id),
            (FornecedorCambio, self.cambio_fornecedor_id),
            (FornecedorSuspensao, self.suspensao_fornecedor_id),
        ]:
            item = modelo.query.get(campo_id)
            if item:
                total += item.custo_montagem
        if self.engenheiro_fornecedor_id:
            engenheiro = FornecedorEngenheiro.query.get(self.engenheiro_fornecedor_id)
            if engenheiro:
                total += engenheiro.custo_montagem
        return total

    def custo_total_contratos(self):
        total = 0.0
        for modelo, campo_id in [
            (FornecedorMotor, self.motor_fornecedor_id),
            (FornecedorCombustivel, self.combustivel_fornecedor_id),
            (FornecedorPneu, self.pneu_fornecedor_id),
            (FornecedorCambio, self.cambio_fornecedor_id),
            (FornecedorSuspensao, self.suspensao_fornecedor_id),
        ]:
            item = modelo.query.get(campo_id)
            if item:
                total += float(item.custo_temporada or 0)
        if self.engenheiro_fornecedor_id:
            engenheiro = FornecedorEngenheiro.query.get(self.engenheiro_fornecedor_id)
            if engenheiro:
                total += float(engenheiro.custo_temporada or 0)
        return total


EquipeDB = CarroJogador   # alias pra código antigo


class ResultadoClassificacao(db.Model):
    __tablename__ = "resultados_classificacao"
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("carros_jogadores.id"), nullable=False)
    tempo_classificacao = db.Column(db.Float)
    posicao_grid = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    equipe = db.relationship("CarroJogador")


class ResultadoCorrida(db.Model):
    __tablename__ = "resultados_corrida"
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("carros_jogadores.id"), nullable=False)
    tempo_total_segundos = db.Column(db.Float)
    pit_stops = db.Column(db.Integer)
    posicao_final = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    equipe = db.relationship("CarroJogador")
