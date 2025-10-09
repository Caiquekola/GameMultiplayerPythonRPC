# game.py
import turtle
import time
import random
import argparse
import rpyc

delay = 0.01

# Cores para outros jogadores
PALETA = ["blue", "yellow", "purple", "orange", "magenta", "cyan", "white", "brown", "gold", "pink"]
cores_outros = {}

# Outros jogadores: nome -> turtle.Turtle()
outros = {}

# Tela
wn = turtle.Screen()
wn.title("Move Game (RPC simples)")
wn.bgcolor("green")
wn.setup(width=1.0, height=1.0, startx=None, starty=None)
wn.tracer(0)

# Meu jogador
head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.color("red")
head.penup()
head.goto(0, 0)
head.direction = "stop"

def cor_para(nome):
    if nome not in cores_outros:
        cores_outros[nome] = random.choice(PALETA)
    return cores_outros[nome]

# Controles
def go_up():    head.direction = "up"
def go_down():  head.direction = "down"
def go_left():  head.direction = "left"
def go_right(): head.direction = "right"
def close():    wn.bye()

def move():
    if head.direction == "up":
        y = head.ycor(); head.sety(y + 2)
    if head.direction == "down":
        y = head.ycor(); head.sety(y - 2)
    if head.direction == "left":
        x = head.xcor(); head.setx(x - 2)
    if head.direction == "right":
        x = head.xcor(); head.setx(x + 2)

# Teclado
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(close, "Escape")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18861)
    parser.add_argument("--name", default="Jogador")
    args = parser.parse_args()

    # Conecta ao servidor RPC simples
    proxy = rpyc.connect(args.server, args.port, config={'allow_public_attrs': True}).root
    meu_nome = args.name

    ultimo_seq = 0
    ultimo_publicado = (None, None)

    while True:
        wn.update()
        move()

        # Publica meu movimento se mudou a posição
        x, y = head.xcor(), head.ycor()
        if (x, y) != ultimo_publicado:
            proxy.publicar_movimento(meu_nome, x, y, head.direction)
            ultimo_publicado = (x, y)

        # Busca eventos novos e aplica
        pacote = proxy.obter_eventos(ultimo_seq)
        ultimo_seq = pacote["ultimo_seq"]
        for ev in pacote["eventos"]:
            if ev["type"] != "move":
                continue
            nome = ev["player"]
            if nome == meu_nome:
                continue  # ignora meus próprios eventos
            if nome not in outros:
                t = turtle.Turtle()
                t.speed(0)
                t.shape("circle")
                t.color(cor_para(nome))
                t.penup()
                t.goto(0, 0)
                outros[nome] = t
            # Atualiza posição do outro jogador
            outros[nome].goto(ev["x"], ev["y"])

        time.sleep(delay)

if __name__ == "__main__":
    try:
        main()
    except turtle.Terminator:
        pass
