# game.py
import hashlib
import turtle
import time
import random
import argparse
import socket
import rpyc

delay = 0.01

PALETA = ["blue","yellow","purple","orange"]
cores_outros = {}
outros = {}

wn = turtle.Screen()
wn.title("Move Game (RPC simples)")
wn.bgcolor("black")
wn.setup(width=0.5, height=0.5, startx=None, starty=None)
wn.tracer(0)

head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.penup()
head.goto(0,0)
head.direction = "stop"
head.color(random.choice(PALETA))  

def cor_para(nome):
    h = hashlib.md5(nome.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(PALETA)
    return PALETA[idx]

def go_up():    head.direction = "up"
def go_down():  head.direction = "down"
def go_left():  head.direction = "left"
def go_right(): head.direction = "right"
def close():    wn.bye()

# Retornar nas bordas (wrap)
def wrap_turtle(t, pad=10):
    half_w = wn.window_width() // 2 - pad
    half_h = wn.window_height() // 2 - pad
    x, y = t.xcor(), t.ycor()
    if x >  half_w:   t.setx(-half_w)
    elif x < -half_w: t.setx( half_w)
    if y >  half_h:   t.sety(-half_h)
    elif y < -half_h: t.sety( half_h)

def move():
    if head.direction == "up":
        head.sety(head.ycor() + 2)
    if head.direction == "down":
        head.sety(head.ycor() - 2)
    if head.direction == "left":
        head.setx(head.xcor() - 2)
    if head.direction == "right":
        head.setx(head.xcor() + 2)
    wrap_turtle(head)

wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(close, "Escape")

def porta_aberta(host, port, timeout=1.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18861)
    parser.add_argument("--name", default="Jogador")
    args = parser.parse_args()

    # Teste p evitar travar
    if not porta_aberta(args.server, args.port, timeout=1.5):
        wn.title(f"Servidor {args.server}:{args.port} inacessível")
        print(f"não consigo conectar em {args.server}:{args.port}. ")
        return

    proxy = rpyc.connect(
        args.server, args.port,
        config={'allow_public_attrs': True, 'sync_request_timeout': 2.0}
    ).root
    meu_nome = args.name
    head.color(cor_para(meu_nome))
    estado_inicial = proxy.obter_eventos(0)
    ultimo_seq = estado_inicial["ultimo_seq"]
    
    ultimo_publicado = (None, None)

    while True:
        wn.update()
        move()

        #   pos se mudou
        x, y = head.xcor(), head.ycor()
        if (x, y) != ultimo_publicado:
            try:
                proxy.publicar_posicao(meu_nome, x, y)
                ultimo_publicado = (x, y)
            except Exception as e:
                print("publicar_posicao falhou:", e)

        # busca eventos e aplica
        try:
            pacote = proxy.obter_eventos(ultimo_seq)
            ultimo_seq = pacote["ultimo_seq"]
            for ev in pacote["eventos"]:
                if ev.get("type") != "move":
                    continue
                nome = ev["player"]
                if nome == meu_nome:
                    continue
                if nome not in outros:
                    t = turtle.Turtle()
                    t.speed(0)
                    t.shape("circle")
                    t.color(cor_para(nome))  
                    t.penup()
                    t.goto(0,0)
                    outros[nome] = t
                outros[nome].goto(ev["x"], ev["y"])
        except Exception:
            pass

        time.sleep(delay)

if __name__ == "__main__":
    try:
        main()
    except turtle.Terminator:
        pass
