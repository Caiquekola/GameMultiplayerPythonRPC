# servidorrpc.py
import rpyc, threading, time
from rpyc.utils.server import ThreadedServer

_lock = threading.Lock()
_seq = 0
_eventos = []

class Servico(rpyc.Service):
    def exposed_publicar_movimento(self, player, x, y, direcao):
        global _seq, _eventos
        with _lock:
            _seq += 1
            _eventos.append({
                "seq": _seq, "type": "move", "player": str(player),
                "x": float(x), "y": float(y), "dir": str(direcao or ""), "ts": time.time(),
            })
            if len(_eventos) > 5000: del _eventos[:3000]
            return True

    def exposed_obter_eventos(self, desde_seq):
        with _lock:
            ult = _seq
            novos = [ev for ev in _eventos if ev["seq"] > int(desde_seq)]
        return {"ultimo_seq": ult, "eventos": novos}

if __name__ == "__main__":
    print("[Servidor] escutando em 0.0.0.0:18861")
    ThreadedServer(
        Servico,
        hostname="0.0.0.0",              # <<< aceita conexões remotas
        port=18861,
        protocol_config={"allow_public_attrs": True},
    ).start()
