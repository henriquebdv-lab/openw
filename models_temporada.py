"""
Novas tabelas do sistema de Temporada.

Ficam num arquivo separado do models.py principal pra não mexer no
que já está funcionando com equipes reais. Usa o mesmo `db` de lá.

Ao subir o Flask pela 1ª vez com esse arquivo, você precisa rodar:
    flask db migrate -m "temporadas"
    flask db upgrade

Isso cria as tabelas novas sem tocar nas antigas.
"""

from datetime import datetime
import json

from sqlalchemy.exc import NoSuchTableError, OperationalError, ProgrammingError

from models import db


class Temporada(db.Model):
    """Um "campeonato": um conjunto ordenado de corridas + pontuação."""
    __tablename__ = "temporadas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    ativa = db.Column(db.Boolean, default=False, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    corridas_agendadas = db.relationship(
        "CorridaAgendada", backref="temporada",
        cascade="all, delete-orphan",
        order_by="CorridaAgendada.ordem",
    )

    @classmethod
    def ativa_atual(cls):
        """Retorna a temporada marcada como ativa, ou None."""
        try:
            return cls.query.filter_by(ativa=True).first()
        except (OperationalError, ProgrammingError, NoSuchTableError):
            return None

    def proxima_corrida(self):
        """Retorna a próxima CorridaAgendada ainda não executada, ou None."""
        return next((c for c in self.corridas_agendadas if not c.executada), None)

    def total_corridas(self):
        return len(self.corridas_agendadas)

    def corridas_executadas(self):
        return sum(1 for c in self.corridas_agendadas if c.executada)


class CorridaAgendada(db.Model):
    """Cada linha do calendário: qual pista, em qual ordem, se já rodou.

    Guarda os resultados numa coluna JSON pra ser autossuficiente
    (não depende do ResultadoCorrida antigo, e sobrevive a mudanças
    lá). Cada item do JSON é do formato:
        {equipe_id, equipe_nome, posicao, pontos, abandonou, tempo_total}
    """
    __tablename__ = "corridas_agendadas"

    id = db.Column(db.Integer, primary_key=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey("temporadas.id"), nullable=False)
    # Referência à pista no banco separado pistas_reais.db (só o ID).
    pista_real_id = db.Column(db.Integer, nullable=False)
    # Nome cacheado pra não depender de consulta cruzada em toda tela.
    pista_nome = db.Column(db.String(120))
    ordem = db.Column(db.Integer, nullable=False)
    executada = db.Column(db.Boolean, default=False, nullable=False)
    data_execucao = db.Column(db.DateTime)
    resultado_json = db.Column(db.Text, default="[]")

    def resultados(self):
        """Lê os resultados salvos como lista de dicts."""
        try:
            return json.loads(self.resultado_json or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def salvar_resultados(self, lista):
        self.resultado_json = json.dumps(lista, ensure_ascii=False)
