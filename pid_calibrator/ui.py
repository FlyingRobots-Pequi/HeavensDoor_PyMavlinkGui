import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import math
from .config import defaults
from .mavlink_client import MavlinkClient
from .plotter import Plotter


def quaternion_to_euler(q):
    """
    Converte quaternion q (w, x, y, z) para ângulos de Euler (roll, pitch, yaw).
    Retorna valores em radianos.
    """
    w, x, y, z = q
    # Roll (x-axis rotation)
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)
    # Pitch (y-axis rotation)
    t2 = 2.0 * (w * y - z * x)
    t2 = max(-1.0, min(1.0, t2))
    pitch = math.asin(t2)
    # Yaw (z-axis rotation)
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)
    return roll, pitch, yaw


class PIDCalibrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PX4 PID Calibrator")
        self.geometry("900x700")

        # Carrega configurações
        cfg = defaults()
        self.update_interval_ms = cfg['UPDATE_INTERVAL_MS']
        self.param_timeout     = cfg['PARAM_REQUEST_TIMEOUT']
        self.max_data_len      = cfg['MAX_DATA_LENGTH']
        self.window_seconds    = cfg['WINDOW_SECONDS']

        self.mav_client = None
        self.plotters   = {}
        self.ctrl_axes  = {}
        self.ctrl_lines = {}

        # Guarda setpoints e feedbacks
        self.last_rate_set = None
        self.last_rate_act = None
        self.last_att_set = None
        self.last_att_act = None
        self.last_vel_set = None
        self.last_vel_act = None
        self.last_pos_set = None
        self.last_pos_act = None

        self._build_ui()

    def _build_ui(self):
        # Frame de conexão
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm, text="Connection URI:").pack(side="left")
        self.conn_entry = ttk.Entry(frm, width=40)
        self.conn_entry.insert(0, defaults()['CONNECTION_URI'])
        self.conn_entry.pack(side="left", padx=5)
        ttk.Button(frm, text="Connect", command=self._on_connect).pack(side="left")

        # Treeview de parâmetros MAVLink
        self.tree = ttk.Treeview(self, columns=("val","def"), show="headings", height=8)
        self.tree.heading("val", text="Valor Atual")
        self.tree.heading("def", text="Total Params")
        self.tree.pack(fill="x", padx=10, pady=5)

        # Notebook pai: Controladores
        self.controller_nb = ttk.Notebook(self)
        self.controller_nb.pack(fill="both", expand=True, padx=10, pady=5)

        # Definição de controladores e suas abas-filho
        controllers = {
            'rate_controller':     ['roll', 'pitch', 'yaw'],
            'attitude_controller': ['roll', 'pitch', 'yaw'],
            'velocity_controller': ['horizontal', 'vertical'],
            'position_controller': ['horizontal', 'vertical'],
        }

        # Cria abas para cada controlador
        for ctrl_id, axes in controllers.items():
            title = ctrl_id.replace('_', ' ').title()
            ctrl_frame = ttk.Frame(self.controller_nb)
            self.controller_nb.add(ctrl_frame, text=title)

            inner_nb = ttk.Notebook(ctrl_frame)
            inner_nb.pack(fill="both", expand=True)

            self.ctrl_axes[ctrl_id]  = {}
            self.ctrl_lines[ctrl_id] = {}

            for axis in axes:
                frame = ttk.Frame(inner_nb)
                inner_nb.add(frame, text=axis.capitalize())

                fig = Figure(figsize=(6, 3), dpi=100)
                ax  = fig.add_subplot(111)
                ax.set_xlabel("Tempo (s)")
                ax.set_ylabel("Valor")
                lset, = ax.plot([], [], label="Setpoint")  # azul
                lact, = ax.plot([], [], label="Medido")   # laranja
                ax.legend(loc="upper right")

                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.get_tk_widget().pack(fill="both", expand=True)

                self.ctrl_axes[ctrl_id][axis]  = ax
                self.ctrl_lines[ctrl_id][axis] = (lset, lact)
                setattr(self, f'canvas_{ctrl_id}_{axis}', canvas)

            # Instancia Plotter por controlador
            self.plotters[ctrl_id] = Plotter(
                self.ctrl_axes[ctrl_id],
                self.ctrl_lines[ctrl_id],
                self.max_data_len,
                self.window_seconds
            )

    def _on_connect(self):
        uri = self.conn_entry.get()
        self.mav_client = MavlinkClient(uri, self.param_timeout)
        self.mav_client.connect()

        params = self.mav_client.request_all_params()
        for pid, val, count in params:
            self.tree.insert("", "end", iid=pid, values=(val, count))

        # inicia o loop de leitura e plotagem
        self.after(self.update_interval_ms, self._update_loop)

    def _update_loop(self):
        msgs = self.mav_client.recv_messages()

        # Processa mensagens
        for msg in msgs:
            t = msg.get_type()
            # Rate Controller
            if t == 'ATTITUDE_TARGET':
                self.last_rate_set = {
                    'roll':  msg.body_roll_rate  * 180/math.pi,
                    'pitch': msg.body_pitch_rate * 180/math.pi,
                    'yaw':   msg.body_yaw_rate   * 180/math.pi,
                }
                try:
                    roll_d, pitch_d, yaw_d = quaternion_to_euler(msg.q)
                    self.last_att_set = {
                        'roll':  roll_d  * 180/math.pi,
                        'pitch': pitch_d * 180/math.pi,
                        'yaw':   yaw_d   * 180/math.pi,
                    }
                except Exception:
                    pass

            elif t == 'ATTITUDE':
                self.last_rate_act = {
                    'roll':  msg.rollspeed  * 180/math.pi,
                    'pitch': msg.pitchspeed * 180/math.pi,
                    'yaw':   msg.yawspeed   * 180/math.pi,
                }
                self.last_att_act = {
                    'roll':  msg.roll  * 180/math.pi,
                    'pitch': msg.pitch * 180/math.pi,
                    'yaw':   msg.yaw   * 180/math.pi,
                }

            # Velocity/Position Controller
            elif t == 'POSITION_TARGET_LOCAL_NED':
                self.last_vel_set = {
                    'horizontal': math.hypot(msg.vx, msg.vy),
                    'vertical':   -msg.vz,
                }
                self.last_pos_set = {
                    'horizontal': math.hypot(msg.x, msg.y),
                    'vertical':   -msg.z,
                }

            elif t == 'LOCAL_POSITION_NED':
                self.last_vel_act = {
                    'horizontal': math.hypot(msg.vx, msg.vy),
                    'vertical':   -msg.vz,
                }
                self.last_pos_act = {
                    'horizontal': math.hypot(msg.x, msg.y),
                    'vertical':   -msg.z,
                }

        # Atualiza Rate Controller
        if self.last_rate_set is not None and self.last_rate_act is not None:
            self.plotters['rate_controller'].update(self.last_rate_set, self.last_rate_act)
            for axis in ['roll', 'pitch', 'yaw']:
                getattr(self, f'canvas_rate_controller_{axis}').draw()

        # Atualiza Attitude Controller
        if self.last_att_set is not None and self.last_att_act is not None:
            self.plotters['attitude_controller'].update(self.last_att_set, self.last_att_act)
            for axis in ['roll', 'pitch', 'yaw']:
                getattr(self, f'canvas_attitude_controller_{axis}').draw()

        # Atualiza Velocity Controller
        if self.last_vel_set is not None and self.last_vel_act is not None:
            self.plotters['velocity_controller'].update(self.last_vel_set, self.last_vel_act)
            for axis in ['horizontal', 'vertical']:
                getattr(self, f'canvas_velocity_controller_{axis}').draw()

        # Atualiza Position Controller
        if self.last_pos_set is not None and self.last_pos_act is not None:
            self.plotters['position_controller'].update(self.last_pos_set, self.last_pos_act)
            for axis in ['horizontal', 'vertical']:
                getattr(self, f'canvas_position_controller_{axis}').draw()

        # Agenda próxima execução
        self.after(self.update_interval_ms, self._update_loop)
