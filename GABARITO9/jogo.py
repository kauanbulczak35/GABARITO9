from pyscript import document, when
from random import randint
import asyncio

# ELEMENTOS DO HTML
jogo = document.querySelector("#jogo")

jogador = document.querySelector("#jogador")
moeda = document.querySelector("#moeda")
inimigo = document.querySelector("#inimigo")

placar = document.querySelector("#placar")
vidas = document.querySelector("#vidas")
tempo = document.querySelector("#tempo")
fase = document.querySelector("#fase")
mensagem = document.querySelector("#mensagem")

# SONS
som_moeda = document.querySelector("#somMoeda")
som_colisao = document.querySelector("#somColisao")


def tocar_som(som):
    try:
        som.currentTime = 0
        som.play()
    except Exception:
        pass


# VARIÁVEIS
pontos = 0
vida = 3
segundos = 60
fase_atual = 1

velocidade_jogador = 10
velocidade_inimigo = 5

game_over = False
ultimo_dano = -10

# POSIÇÕES
x_jogador = 100
y_jogador = 100

x_moeda = 300
y_moeda = 200

x_inimigo = 500
y_inimigo = 200


# LIMITES DO CENÁRIO
def limite_x():
    return max(0, jogo.clientWidth - 40)


def limite_y():
    return max(0, jogo.clientHeight - 40)


# ATUALIZAR POSIÇÕES
def atualizar_posicoes():
    jogador.style.left = f"{x_jogador}px"
    jogador.style.top = f"{y_jogador}px"

    moeda.style.left = f"{x_moeda}px"
    moeda.style.top = f"{y_moeda}px"

    inimigo.style.left = f"{x_inimigo}px"
    inimigo.style.top = f"{y_inimigo}px"


# NOVA MOEDA
def nova_moeda():
    global x_moeda, y_moeda

    x_moeda = randint(10, max(10, limite_x()))
    y_moeda = randint(10, max(10, limite_y()))

    moeda.style.left = f"{x_moeda}px"
    moeda.style.top = f"{y_moeda}px"


# SISTEMA DE FASES
def atualizar_fase():
    global fase_atual, velocidade_inimigo

    if pontos >= 10:
        fase_atual = 3
        velocidade_inimigo = 12
        mensagem.innerText = "Fase 3: o detetive está mais rápido!"

    elif pontos >= 5:
        fase_atual = 2
        velocidade_inimigo = 8
        mensagem.innerText = "Fase 2: cuidado, o detetive acelerou!"

    else:
        fase_atual = 1
        velocidade_inimigo = 5
        mensagem.innerText = "Fase 1: colete as moedas!"

    fase.innerText = str(fase_atual)


# MOVIMENTAÇÃO DO JOGADOR
@when("keydown", "body")
def movimentar(event):

    global x_jogador, y_jogador

    if game_over:
        return

    tecla = event.key

    # Impede a página de subir ou descer
    # quando as setas forem pressionadas.
    if tecla in [
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight"
    ]:
        event.preventDefault()

    if tecla == "ArrowUp":
        y_jogador -= velocidade_jogador

    elif tecla == "ArrowDown":
        y_jogador += velocidade_jogador

    elif tecla == "ArrowLeft":
        x_jogador -= velocidade_jogador

    elif tecla == "ArrowRight":
        x_jogador += velocidade_jogador

    else:
        return

    # Impede o ninja de sair do cenário
    x_jogador = max(0, min(x_jogador, limite_x()))
    y_jogador = max(0, min(y_jogador, limite_y()))

    atualizar_posicoes()
    verificar_colisao()


# VERIFICAR COLISÕES
def verificar_colisao():

    global pontos

    if game_over:
        return

    distancia_moeda = (
        abs(x_jogador - x_moeda) < 35
        and abs(y_jogador - y_moeda) < 35
    )

    if distancia_moeda:

        pontos += 1
        placar.innerText = str(pontos)

        tocar_som(som_moeda)

        nova_moeda()
        atualizar_fase()

    distancia_inimigo = (
        abs(x_jogador - x_inimigo) < 35
        and abs(y_jogador - y_inimigo) < 35
    )

    if distancia_inimigo:
        perder_vida()


# PERDER VIDA
def perder_vida():

    global vida, ultimo_dano

    if game_over:
        return

    agora = asyncio.get_running_loop().time()

    if agora - ultimo_dano < 1:
        return

    ultimo_dano = agora

    vida -= 1
    vidas.innerText = str(vida)

    tocar_som(som_colisao)

    mensagem.innerText = "O detetive encontrou o ninja!"

    if vida <= 0:
        finalizar_jogo()


# MOVIMENTAÇÃO DO DETETIVE
async def mover_inimigo():

    global x_inimigo

    while not game_over:

        x_inimigo -= velocidade_inimigo

        if x_inimigo < -40:
            x_inimigo = jogo.clientWidth

        inimigo.style.left = f"{x_inimigo}px"

        verificar_colisao()

        await asyncio.sleep(0.03)


# CRONÔMETRO
async def contar_tempo():

    global segundos

    while segundos > 0 and not game_over:

        await asyncio.sleep(1)

        if game_over:
            break

        segundos -= 1
        tempo.innerText = str(segundos)

    if segundos <= 0 and not game_over:
        finalizar_jogo()


# FIM DE JOGO
def finalizar_jogo():

    global game_over

    game_over = True

    mensagem.innerText = (
        f"Fim de jogo! Você conseguiu {pontos} pontos!"
    )


# INICIAR JOGO
atualizar_posicoes()
atualizar_fase()
nova_moeda()


async def iniciar():

    await asyncio.gather(
        mover_inimigo(),
        contar_tempo()
    )


asyncio.create_task(iniciar())
