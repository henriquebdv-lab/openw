"""
Script para preparar os BOTS (jogadores fake) para a PRÓXIMA CORRIDA da temporada.
Isso evita que você precise resetar o banco inteiro a cada etapa.
Ele gera setups de Parc Fermé, Ajuste Fino, Dados de Classificação e Stints aleatórios
para todas as contas "bot%@fake.com".

Uso:
    python3 mock_preparacao.py
"""
import random
from app import app
from models import db, Usuario, SetupFimDeSemana, DadosClassificacao, EstrategiaStint, AjusteSalvo
from models_temporada import Temporada
import modelos_componente

def preparar_bots():
    temporada = Temporada.ativa_atual()
    if not temporada:
        print("[AVISO] Nenhuma temporada ativa.")
        return

    corrida = temporada.proxima_corrida()
    if not corrida:
        print("[AVISO] Nenhuma corrida pendente na temporada atual.")
        return

    bots = Usuario.query.filter(Usuario.email.like('bot%@fake.com')).all()
    if not bots:
        print("[AVISO] Nenhum bot encontrado no banco de dados.")
        return

    modelos = modelos_componente.MODELOS
    pista_id = corrida.pista_real_id

    preparados = 0
    for bot in bots:
        carro = bot.equipe
        if not carro:
            continue

        # 1. Limpa preparações antigas para a corrida atual (evita duplicação)
        SetupFimDeSemana.query.filter_by(equipe_id=carro.id, corrida_id=corrida.id).delete()
        DadosClassificacao.query.filter_by(equipe_id=carro.id, corrida_id=corrida.id).delete()
        EstrategiaStint.query.filter_by(equipe_id=carro.id).delete()
        
        # 2. Setup do Parc Fermé
        db.session.add(SetupFimDeSemana(
            equipe_id=carro.id, 
            corrida_id=corrida.id,
            modelo_motor=random.choice(modelos),
            modelo_cambio=random.choice(modelos),
            modelo_suspensao=random.choice(modelos),
            travado=True
        ))

        # 3. Ajuste Fino (Treino Livre)
        ajuste = AjusteSalvo.query.filter_by(equipe_id=carro.id, pista_real_id=pista_id).first()
        if not ajuste:
            db.session.add(AjusteSalvo(
                equipe_id=carro.id, 
                pista_real_id=pista_id,
                ajuste_cambio=random.randint(1, 99),
                ajuste_suspensao=random.randint(1, 99),
                ajuste_aero_dianteiro=random.randint(1, 99),
                ajuste_aero_traseiro=random.randint(1, 99),
                ajuste_freio=50
            ))

        # 4. Dados de Classificação (Quali)
        db.session.add(DadosClassificacao(
            equipe_id=carro.id, 
            corrida_id=corrida.id,
            modelo_pneu=random.choice(modelos),
            combustivel_litros=float(random.randint(5, 12))
        ))

        # 5. Estratégia de Corrida (Stints)
        for ordem in range(1, random.randint(1, 3) + 1):
            db.session.add(EstrategiaStint(
                equipe_id=carro.id, 
                ordem=ordem,
                modelo_pneu=random.choice(modelos),
                voltas=random.randint(15, 30),
                combustivel_litros=float(random.randint(40, 110))
            ))
        
        preparados += 1

    db.session.commit()
    print(f"[OK] {preparados} bots preparados com sucesso para a corrida: {corrida.pista_nome}")

if __name__ == "__main__":
    with app.app_context():
        preparar_bots()