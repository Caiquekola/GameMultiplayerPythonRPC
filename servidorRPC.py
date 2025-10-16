# servidorrpc.py
import rpyc
import threading
import time
from rpyc.utils.server import ThreadedServer

_lock = threading.Lock()
_seq = 0
_eventos = []  #{"seq","type":"move","player","x","y","ts"}

class Servico(rpyc.Service):
    def exposed_publicar_posicao(self, player, x, y):
        #a posição (x,y) do jogador.
        global _seq, _eventos
        with _lock:
            _seq += 1
            _eventos.append({
                "seq": _seq,
                "type": "move",   
                "player": str(player),
                "x": float(x),
                "y": float(y),
                "ts": time.time(),
            })
            if len(_eventos) > 5000:
                del _eventos[:3000]
            return True

    def exposed_publicar_movimento(self, player, x, y, *_, **__):
        return self.exposed_publicar_posicao(player, x, y)

    def exposed_obter_eventos(self, desde_seq):
        with _lock:
            ult = _seq
            novos = [ev for ev in _eventos if ev["seq"] > int(desde_seq)]
        return {"ultimo_seq": ult, "eventos": novos}

if __name__ == "__main__":
    print("[Servidor] escutando em 0.0.0.0:18861")
    ThreadedServer(
        Servico,
        hostname="0.0.0.0",
        port=18861,
        protocol_config={"allow_public_attrs": True}
    ).start()
