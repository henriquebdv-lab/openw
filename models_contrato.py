"""
ContratoFornecedor — vínculo de fornecedor por TEMPORADA (regra do Estrategia F1).

Regra do jogo:
- O jogador assina 1 contrato de fornecedor por TIPO DE PEÇA
  (motor, combustível, pneu, câmbio, suspensão, engenheiro) UMA VEZ POR TEMPORADA.
- O contrato vale a temporada inteira e NÃO pode ser trocado livremente durante
  a temporada ativa (rescisão com multa fica pra depois — por ora só BLOQUEIA a
  troca livre).

Este arquivo é SEPARADO do models.py principal de propósito. Ele reaproveita o
MESMO objeto `db` (SQLAlchemy) do models.py, então tudo fica no mesmo banco e nas
mesmas migrações — sem duplicar instância.

IMPORTANTE (compatibilidade):
- NÃO altera nenhuma tabela existente.
- O campo que aponta pro fornecedor se chama `fornecedor_id` (e NÃO "contrato_id"),
  pra não confundir com o nome desta tabela nova.
- Como cada tipo de peça vive numa tabela de fornecedor diferente
  (fornecedores_motor, fornecedores_combustivel, ...), `fornecedor_id` é um
  Integer SEM ForeignKey física (FK polimórfica resolvida por `tipo_peca`).
"""

from datetime import datetime

# Reaproveita a MESMA instância db do models.py (não cria outra!)
from models import (
    db,
    FornecedorMotor,
    FornecedorCombustivel,
    FornecedorPneu,
    FornecedorCambio,
    FornecedorSuspensao,
    FornecedorEngenheiro,
)
from models_temporada import Temporada


# Tipos de peça válidos (é o "tipo_peca" da tabela)
TIPOS_PECA = ("motor", "combustivel", "pneu", "cambio", "suspensao", "engenheiro")

# Mapa tipo_peca -> classe do fornecedor correspondente, pra resolver a "FK polimórfica"
MODELO_POR_TIPO = {
    "motor": FornecedorMotor,
    "combustivel": FornecedorCombustivel,
    "pneu": FornecedorPneu,
    "cambio": FornecedorCambio,
    "suspensao": FornecedorSuspensao,
    "engenheiro": FornecedorEngenheiro,
}

# Mapa tipo_peca -> nome do campo legado no CarroJogador (usado no fallback e na
# migração dos contratos das temporadas antigas).
CAMPO_LEGADO_POR_TIPO = {
    "motor": "motor_fornecedor_id",
    "combustivel": "combustivel_fornecedor_id",
    "pneu": "pneu_fornecedor_id",
    "cambio": "cambio_fornecedor_id",
    "suspensao": "suspensao_fornecedor_id",
    "engenheiro": "engenheiro_fornecedor_id",
}


class ContratoFornecedorError(Exception):
    """Erro de regra de negócio ao assinar/trocar contrato."""
    pass


class ContratoFornecedor(db.Model):
    """1 contrato = (equipe, temporada, tipo_peca) -> fornecedor.

    Só pode existir UM contrato por (equipe_id, temporada_id, tipo_peca),
    garantido pela UniqueConstraint abaixo.
    """
    __tablename__ = "contratos_fornecedor"
    __table_args__ = (
        db.UniqueConstraint(
            "equipe_id", "temporada_id", "tipo_peca",
            name="uq_contrato_equipe_temporada_tipo",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("carros_jogadores.id"), nullable=False, index=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey("temporadas.id"), nullable=False, index=True)
    tipo_peca = db.Column(db.String(20), nullable=False)  # um de TIPOS_PECA

    # FK polimórfica: aponta pra fornecedores_<tipo_peca>.id (sem FK física).
    fornecedor_id = db.Column(db.Integer, nullable=False)

    assinado_em = db.Column(db.DateTime, default=datetime.utcnow)

    equipe = db.relationship("CarroJogador")
    temporada = db.relationship("Temporada")

    def __repr__(self):
        return (f"<ContratoFornecedor equipe={self.equipe_id} "
                f"temp={self.temporada_id} {self.tipo_peca}=#{self.fornecedor_id}>")

    # ---------------------------------------------------------------
    # Helpers de instância
    # ---------------------------------------------------------------
    def fornecedor(self):
        """Retorna o objeto Fornecedor* correspondente (ou None)."""
        modelo = MODELO_POR_TIPO.get(self.tipo_peca)
        if not modelo:
            return None
        return modelo.query.get(self.fornecedor_id)


# ===================================================================
# CRIAÇÃO DA TABELA (atalho sem migração — mesmo padrão db.create_all)
# ===================================================================
def garantir_tabela_contratos():
    """Cria a tabela contratos_fornecedor se ainda não existir.

    Segue o MESMO padrão do seu garantir_colunas_fornecedores(): create_all()
    só cria o que falta e NUNCA apaga/altera tabela existente. Chame isto dentro
    do bloco `with app.app_context():` no app.py, logo após garantir_colunas_fornecedores().

    Use isto se você NÃO quiser mexer com Flask-Migrate agora — é à prova de erro.
    """
    try:
        db.create_all()
    except Exception:
        pass


# ===================================================================
# REGRAS DE NEGÓCIO
# ===================================================================
def _temporada_ativa_ou_erro():
    temporada = Temporada.ativa_atual()
    if not temporada:
        raise ContratoFornecedorError(
            "Não há temporada ativa. Só é possível assinar contratos com uma temporada ativa."
        )
    return temporada


def _validar_tipo(tipo_peca):
    if tipo_peca not in TIPOS_PECA:
        raise ContratoFornecedorError(
            f"tipo_peca inválido: {tipo_peca!r}. Use um de {TIPOS_PECA}."
        )


def obter_contrato(equipe_id, tipo_peca, temporada_id=None):
    """Retorna o ContratoFornecedor de (equipe, temporada, tipo_peca) ou None.

    Se temporada_id não for informado, usa a temporada ATIVA. Se não houver
    temporada ativa, retorna None (não levanta erro).
    """
    _validar_tipo(tipo_peca)
    if temporada_id is None:
        temporada = Temporada.ativa_atual()
        if not temporada:
            return None
        temporada_id = temporada.id
    return ContratoFornecedor.query.filter_by(
        equipe_id=equipe_id, temporada_id=temporada_id, tipo_peca=tipo_peca
    ).first()


def obter_fornecedor_contratado(equipe_id, tipo_peca, usar_fallback_legado=True):
    """Retorna o OBJETO Fornecedor* contratado pela equipe na temporada ativa.

    Esta é a função que substitui o uso direto de
    CarroJogador.motor_fornecedor_id (etc.) no montar_carro() e no treino_livre_sim.

    Ordem de resolução:
      1) Contrato da temporada ativa (ContratoFornecedor).
      2) Se não houver contrato E usar_fallback_legado=True, cai no campo antigo
         do CarroJogador (motor_fornecedor_id, ...). Isso mantém as equipes/temporadas
         antigas funcionando enquanto você migra tudo pros contratos.

    Retorna o objeto (ex.: FornecedorMotor) ou None.
    """
    _validar_tipo(tipo_peca)

    contrato = obter_contrato(equipe_id, tipo_peca)
    if contrato:
        return contrato.fornecedor()

    if not usar_fallback_legado:
        return None

    # Fallback legado: lê o FK direto que ainda existe no CarroJogador.
    from models import CarroJogador
    equipe = CarroJogador.query.get(equipe_id)
    if not equipe:
        return None
    campo = CAMPO_LEGADO_POR_TIPO[tipo_peca]
    fornecedor_id = getattr(equipe, campo, None)
    if not fornecedor_id:
        return None
    modelo = MODELO_POR_TIPO[tipo_peca]
    return modelo.query.get(fornecedor_id)


def obter_id_fornecedor_contratado(equipe_id, tipo_peca, usar_fallback_legado=True):
    """Igual à função acima, mas retorna só o ID (ou None). Útil pra montar_carro,
    que hoje trabalha com os *_fornecedor_id."""
    obj = obter_fornecedor_contratado(equipe_id, tipo_peca, usar_fallback_legado)
    return obj.id if obj else None


def assinar_contrato(equipe_id, tipo_peca, fornecedor_id, temporada_id=None,
                     permitir_troca=False):
    """Assina (ou re-assina) o contrato de uma peça pra temporada ativa.

    Regras:
      - Precisa de temporada ativa (a menos que você passe temporada_id explícito).
      - Se JÁ existe contrato pra (equipe, temporada, tipo_peca):
          * mesmo fornecedor -> não faz nada, retorna o contrato existente.
          * fornecedor diferente -> BLOQUEIA (levanta ContratoFornecedorError),
            a não ser que permitir_troca=True (reservado pra futura "rescisão com
            multa"; por enquanto ninguém chama com True no fluxo normal).
      - Se não existe -> cria.

    Retorna o ContratoFornecedor.
    """
    _validar_tipo(tipo_peca)

    if temporada_id is None:
        temporada_id = _temporada_ativa_ou_erro().id

    # Valida se o fornecedor existe na tabela certa
    modelo = MODELO_POR_TIPO[tipo_peca]
    if not modelo.query.get(fornecedor_id):
        raise ContratoFornecedorError(
            f"Fornecedor #{fornecedor_id} não existe para tipo_peca={tipo_peca}."
        )

    contrato = ContratoFornecedor.query.filter_by(
        equipe_id=equipe_id, temporada_id=temporada_id, tipo_peca=tipo_peca
    ).first()

    if contrato:
        if contrato.fornecedor_id == int(fornecedor_id):
            return contrato  # já é esse, nada a fazer
        if not permitir_troca:
            raise ContratoFornecedorError(
                f"Já existe contrato de {tipo_peca} nesta temporada. "
                f"Contratos valem a temporada inteira e não podem ser trocados livremente."
            )
        # permitir_troca=True: futura rescisão com multa entraria aqui.
        contrato.fornecedor_id = int(fornecedor_id)
        contrato.assinado_em = datetime.utcnow()
        db.session.commit()
        return contrato

    contrato = ContratoFornecedor(
        equipe_id=equipe_id,
        temporada_id=temporada_id,
        tipo_peca=tipo_peca,
        fornecedor_id=int(fornecedor_id),
    )
    db.session.add(contrato)
    db.session.commit()
    return contrato


def pode_trocar_contrato(tipo_peca=None):
    """True se dá pra assinar/trocar contrato agora (fluxo normal).

    Regra simples: só pode assinar/alterar contratos quando NÃO há temporada
    ativa (pré-temporada). Com temporada ativa, contratos ficam travados.
    Use isto nas views pra mostrar/esconder o botão de trocar fornecedor.
    """
    return Temporada.ativa_atual() is None


def contratos_da_equipe(equipe_id, temporada_id=None):
    """Lista todos os contratos da equipe numa temporada (default: a ativa).
    Retorna dict { tipo_peca: ContratoFornecedor }."""
    if temporada_id is None:
        temporada = Temporada.ativa_atual()
        if not temporada:
            return {}
        temporada_id = temporada.id
    contratos = ContratoFornecedor.query.filter_by(
        equipe_id=equipe_id, temporada_id=temporada_id
    ).all()
    return {c.tipo_peca: c for c in contratos}


def importar_contratos_do_legado(equipe_id, temporada_id):
    """UTILITÁRIO (opcional): cria contratos a partir dos campos antigos do
    CarroJogador (motor_fornecedor_id, ...) pra uma temporada.

    Serve pra "migrar" uma equipe que já existia antes dos contratos:
    lê os FKs diretos e cria 1 ContratoFornecedor por peça, sem duplicar.
    Ignora peças sem fornecedor (ex.: engenheiro pode ser None).

    Retorna quantos contratos foram criados.
    """
    from models import CarroJogador
    equipe = CarroJogador.query.get(equipe_id)
    if not equipe:
        return 0

    criados = 0
    for tipo_peca, campo in CAMPO_LEGADO_POR_TIPO.items():
        fornecedor_id = getattr(equipe, campo, None)
        if not fornecedor_id:
            continue
        existe = ContratoFornecedor.query.filter_by(
            equipe_id=equipe_id, temporada_id=temporada_id, tipo_peca=tipo_peca
        ).first()
        if existe:
            continue
        db.session.add(ContratoFornecedor(
            equipe_id=equipe_id,
            temporada_id=temporada_id,
            tipo_peca=tipo_peca,
            fornecedor_id=int(fornecedor_id),
        ))
        criados += 1

    if criados:
        db.session.commit()
    return criados
