import time
from pymavlink import mavutil

class MavlinkClient:
    def __init__(self, uri, param_timeout):
        self.uri            = uri
        self.param_timeout  = param_timeout
        self.mav            = None
        self.target_system  = None
        self.target_component = None

    def connect(self):
        # Abre a conexão e aguarda heartbeat do PX4
        self.mav = mavutil.mavlink_connection(self.uri)
        print("Aguardando heartbeat...")
        self.mav.wait_heartbeat()
        self.target_system    = self.mav.target_system
        self.target_component = self.mav.target_component
        print(f"Conectado ao sistema {self.target_system}:{self.target_component}")

    def request_all_params(self):
        """
        Envia PARAM_REQUEST_LIST e retorna uma lista de tuplas:
          (param_id, valor_atual, total_de_params)
        """
        self.mav.mav.param_request_list_send(
            self.target_system,
            self.target_component
        )
        params = []
        while True:
            msg = self.mav.recv_match(type='PARAM_VALUE', timeout=self.param_timeout)
            if not msg:
                break
            pid = msg.param_id.decode('utf-8').strip('\x00')
            params.append((pid, msg.param_value, msg.param_count))
        return params

    def recv_messages(self):
        """
        Lê todas as mensagens pendentes (non‑blocking) e retorna em uma lista.
        """
        msgs = []
        msg = self.mav.recv_match(blocking=False)
        while msg:
            msgs.append(msg)
            msg = self.mav.recv_match(blocking=False)
        return msgs
