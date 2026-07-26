"""
Pacote de rotas do Open Wheel Strategy.

Cada arquivo aqui dentro Ã© uma Ã¡rea pequena do jogo e expÃµe uma funÃ§Ã£o
`registrar(app)`. Este __init__ sÃ³ chama todas elas, na ordem.

Por que assim (e nÃ£o Blueprint puro):
- Blueprint muda o nome da rota (login -> auth.login), o que quebraria TODOS
  os url_for(...) dos templates. Com este padrÃ£o, o nome da rota continua
  igual (login, minha_equipe, ...), entÃ£o nenhum template precisa mudar.
"""
from rotas import auth, equipe, desenvolvimento, treino, corrida, temporada, admin, fim_de_semana


def registrar_rotas(app):
    auth.registrar(app)
    equipe.registrar(app)
    desenvolvimento.registrar(app)
    treino.registrar(app)
    corrida.registrar(app)
    temporada.registrar(app)
    admin.registrar(app)
    fim_de_semana.registrar(app)