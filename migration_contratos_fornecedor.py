"""cria tabela contratos_fornecedor

MIGRAÇÃO MANUAL (opção B — só use se NÃO for pelo autogenerate).

COMO USAR ESTE ARQUIVO:
1) Copie este arquivo pra dentro de  migrations/versions/
2) Abra ele e ajuste a linha  down_revision = "..."  pro ID da sua migração
   mais recente. Pra descobrir esse ID, rode no terminal:
       flask db heads
   (ele mostra algo tipo  a1b2c3d4e5f6 (head)  — cole esse valor em down_revision)
3) Rode:
       flask db upgrade

Se você preferir o caminho automático (recomendado pra iniciante), NÃO use este
arquivo: siga o passo a passo do autogenerate que está na resposta do chat.
"""

from alembic import op
import sqlalchemy as sa


# ATENÇÃO: troque pelo ID gerado pra ESTA migração (pode manter este, é único).
revision = "ows_contratos_0001"
# ATENÇÃO: cole aqui o ID do seu head atual (veja com: flask db heads).
# Se este for o PRIMEIRO migration do projeto, deixe None.
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "contratos_fornecedor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipe_id", sa.Integer(), nullable=False),
        sa.Column("temporada_id", sa.Integer(), nullable=False),
        sa.Column("tipo_peca", sa.String(length=20), nullable=False),
        sa.Column("fornecedor_id", sa.Integer(), nullable=False),
        sa.Column("assinado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["equipe_id"], ["carros_jogadores.id"]),
        sa.ForeignKeyConstraint(["temporada_id"], ["temporadas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "equipe_id", "temporada_id", "tipo_peca",
            name="uq_contrato_equipe_temporada_tipo",
        ),
    )
    op.create_index(
        "ix_contratos_fornecedor_equipe_id", "contratos_fornecedor", ["equipe_id"]
    )
    op.create_index(
        "ix_contratos_fornecedor_temporada_id", "contratos_fornecedor", ["temporada_id"]
    )


def downgrade():
    op.drop_index("ix_contratos_fornecedor_temporada_id", table_name="contratos_fornecedor")
    op.drop_index("ix_contratos_fornecedor_equipe_id", table_name="contratos_fornecedor")
    op.drop_table("contratos_fornecedor")
