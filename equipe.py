class Equipe:
    """Representa o jogador - dono da equipe (sem status de habilidade própria)."""

    def __init__(self, nome, orcamento=1_000_000.0):
        self.nome = nome
        self.orcamento = orcamento

    def __repr__(self):
        return f"Equipe({self.nome})"
