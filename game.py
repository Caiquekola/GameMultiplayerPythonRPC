# game.py
import turtle
import time
import random
import argparse
import socket
import rpyc

delay = 0.01

PALETA = ["blue","yellow","purple","orange","magenta","cyan","white","brown","gold","pink"]
cores_outros = {}
outros = {}

wn = turtle.Screen()
wn.title("Move Game (RPC simples)")
wn.bgcolor("green")
wn.setup(width=0.5, height=0.5, startx=None, starty=None)
wn.tracer(0)

head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.color("red")
head.penup()
head.goto(0,0)
head.direction = "stop"

def cor_para(nome):
    if nome not in cores_outros:
        cores_outros[nome] = random.choice(PALETA)
    return cores_outros[nome]

def go_up():    head.direction = "up"
def go_down():  head.direction = "down"
def go_left():  head.direction = "left"
def go_right(): head.direction = "right"
def close():    wn.bye()

# --- NOVO: wrap toroidal nas bordas ---
def wrap_turtle(t, pad=10):
    half_w = wn.window_width() // 2 - pad
    half_h = wn.window_height() // 2 - pad
    x, y = t.xcor(), t.ycor()

    if x >  half_w:  t.setx(-half_w)
    elif x < -half_w: t.setx( half_w)
    if y >  half_h:  t.sety(-half_h)
    elif y < -half_h: t.sety( half_h)

def move():
    if head.direction == "up":
        y = head.ycor(); head.sety(y + 2)
    if head.direction == "down":
        y = head.ycor(); head.sety(y - 2)
    if head.direction == "left":
        x = head.xcor(); head.setx(x - 2)
    if head.direction == "right":
        x = head.xcor(); head.setx(x + 2)

    # --- NOVO: aplica wrap após mover ---
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

    # --- Pré-teste rápido para evitar travar no rpyc.connect ---
    if not porta_aberta(args.server, args.port, timeout=1.5):
        wn.title(f"Servidor {args.server}:{args.port} inacessível")
        print(f"[ERRO] não consigo conectar em {args.server}:{args.port}. "
              "Confira se o servidor está rodando e a porta está liberada.")
        return  # sai limpo sem travar a janela

    # --- Conecta com timeout de request curto ---
    proxy = rpyc.connect(
        args.server, args.port,
        config={'allow_public_attrs': True, 'sync_request_timeout': 2.0}
    ).root
    meu_nome = args.name

    ultimo_seq = 0
    ultimo_publicado = (None, None)

    while True:
        wn.update()
        move()

        # publica meu movimento se mudou
        x, y = head.xcor(), head.ycor()
        if (x, y) != ultimo_publicado:
            try:
                proxy.publicar_movimento(meu_nome, x, y, head.direction)
                ultimo_publicado = (x, y)
            except Exception as e:
                # se perder o servidor, não trava a UI
                print("[WARN] publicar_movimento falhou:", e)

        # busca eventos novos e aplica
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
            # servidor lento/offline: segue o jogo local sem travar
            pass

        time.sleep(delay)

if __name__ == "__main__":
    try:
        main()
    except turtle.Terminator:
        pass
