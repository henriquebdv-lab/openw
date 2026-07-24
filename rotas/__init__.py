"""
Pacote de rotas do Open Wheel Strategy.

Cada arquivo aqui dentro é uma área pequena do jogo e expõe uma função
`registrar(app)`. Este __init__ só chama todas elas, na ordem.

Por que assim (e não Blueprint puro):
- Blueprint muda o nome da rota (login -> auth.login), o que quebraria TODOS
  os url_for(...) dos templates. Com este padrão, o nome da rota continua
  igual (login, minha_equipe, ...), então nenhum template precisa mudar.
"""
from rotas import auth, equipe, desenvolvimento, treino, corrida, temporada, admin


def registrar_rotas(app):
    auth.registrar(app)
    equipe.registrar(app)
    desenvolvimento.registrar(app)
    treino.registrar(app)
    corrida.registrar(app)
    temporada.registrar(app)
    admin.registrar(app)
