# game.py
import turtle
import time
import random
import argparse
import rpyc

delay = 0.01

# Score (mantidos, se quiser usar depois)
score = 0
high_score = 0

# Paleta p/ outros jogadores
PALETA = ["blue","yellow","purple","orange","magenta","cyan","white","brown","gold","pink"]
cores_outros = {}
outros = {}  # nome -> turtle.Turtle()

def cor_para(nome):
    if nome not in cores_outros:
        cores_outros[nome] = random.choice(PALETA)
    return cores_outros[nome]

# Set up the screen
wn = turtle.Screen()
wn.title("Move Game by @Garrocho")
wn.bgcolor("green")
wn.setup(width=1.0, height=1.0, startx=None, starty=None)
wn.tracer(0) # Turns off the screen updates

# gamer 1 (eu)
head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.color("red")
head.penup()
head.goto(0,0)
head.direction = "stop"

# Functions
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

# Keyboard bindings
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(close, "Escape")

def main():
    # <<< NOVO: parâmetros para apontar pro servidor >>>
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18861)
    parser.add_argument("--name", default="Jogador")
    args = parser.parse_args()

    # <<< NOVO: conecta ao servidor RPC simples >>>
    proxy = rpyc.connect(args.server, args.port, config={'allow_public_attrs': True}).root
    meu_nome = args.name

    ultimo_seq = 0
    ultimo_publicado = (None, None)

    # Main game loop
    while True:
        wn.update()
        move()

        # <<< NOVO: publica minha posição se mudou >>>
        x, y = head.xcor(), head.ycor()
        if (x, y) != ultimo_publicado:
            proxy.publicar_movimento(meu_nome, x, y, head.direction)
            ultimo_publicado = (x, y)

        # <<< NOVO: busca eventos novos e aplica >>>
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
            # atualiza posição do outro jogador
            outros[nome].goto(ev["x"], ev["y"])

        time.sleep(delay)

if __name__ == "__main__":
    try:
        main()
    except turtle.Terminator:
        pass
