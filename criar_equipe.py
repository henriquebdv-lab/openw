from app import app, db
from models import EquipeDB, FornecedorMotor, FornecedorCombustivel, FornecedorPneu, FornecedorChassi, Usuario

app.app_context().push()

# Criar usuário se não existir
usuario = Usuario.query.filter_by(email='teste@example.com').first()
print(f"Usuário encontrado: {usuario.email if usuario else 'Não encontrado'}")

# Obter fornecedores
motor = FornecedorMotor.query.first()
combustivel = FornecedorCombustivel.query.first()
pneu = FornecedorPneu.query.first()
chassi = FornecedorChassi.query.first()

print(f"Motor: {motor.nome if motor else 'Não encontrado'}")
print(f"Combustível: {combustivel.nome if combustivel else 'Não encontrado'}")

# Criar equipe
if usuario and motor and combustivel and pneu and chassi:
    equipe = EquipeDB(
        usuario_id=usuario.id,
        nome="Meu Time de Corrida",
        orcamento=1_000_000.0,
        motor_fornecedor_id=motor.id,
        combustivel_fornecedor_id=combustivel.id,
        pneu_fornecedor_id=pneu.id,
        chassi_fornecedor_id=chassi.id,
        cor_carro="#DC0000"
    )
    db.session.add(equipe)
    db.session.commit()
    print(f"✓ Equipe criada: {equipe.nome} com cor {equipe.cor_carro}")
else:
    print("✗ Dados insuficientes para criar equipe")
