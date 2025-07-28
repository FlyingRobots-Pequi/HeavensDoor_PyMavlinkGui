#!/usr/bin/env python3
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from pymavlink import mavutil

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class PIDCalibrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PX4 PID Calibrator")
        self.geometry("900x700")

        self.mav = None
        self.start_time = time.time()

        # Dados para roll, pitch, yaw
        self.data = {
            'roll':  {'t': [], 'set': [], 'act': []},
            'pitch': {'t': [], 'set': [], 'act': []},
            'yaw':   {'t': [], 'set': [], 'act': []},
        }

        self._build_ui()

    def _build_ui(self):
        # Seção de conexão
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm, text="Connection URI (ex: udp:0.0.0.0:14550):").pack(side="left")
        self.conn = ttk.Entry(frm, width=40)
        self.conn.insert(0, "udp:0.0.0.0:14550")
        self.conn.pack(side="left", padx=5)
        ttk.Button(frm, text="Connect", command=self.connect).pack(side="left")

        # Parâmetros MAVLink
        self.tree = ttk.Treeview(self, columns=("val", "def"), show="headings", height=8)
        self.tree.heading("val", text="Valor Atual")
        self.tree.heading("def", text="Total Params")
        self.tree.pack(fill="x", padx=10, pady=5)

        # Abas para gráficos
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.axes = {}
        self.lines = {}

        for axis in ['roll', 'pitch', 'yaw']:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=axis.capitalize())

            fig = Figure(figsize=(6, 3), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Taxa (°/s)")
            lset, = ax.plot([], [], label="Setpoint")
            lact, = ax.plot([], [], label="Medido")
            ax.legend(loc="upper right")

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.axes[axis] = ax
            self.lines[axis] = (lset, lact)
            setattr(self, f'canvas_{axis}', canvas)

    def connect(self):
        uri = self.conn.get()
        self.mav = mavutil.mavlink_connection(uri)
        print("Aguardando heartbeat...")
        self.mav.wait_heartbeat()
        print("Conectado!")

        self.start_time = time.time()
        self.request_params()
        self.after(100, self.update_plot)

    def request_params(self):
        if not self.mav:
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        self.mav.mav.param_request_list_send(
            self.mav.target_system,
            self.mav.target_component
        )

        while True:
            msg = self.mav.recv_match(type='PARAM_VALUE', timeout=1)
            if not msg:
                break
            pid = msg.param_id.decode('utf-8').strip('\x00')
            self.tree.insert("", "end", iid=pid,
                             values=(msg.param_value, msg.param_count))

    def update_plot(self):
        if not self.mav:
            return

        # Processa mensagens pendentes
        msg = self.mav.recv_match(blocking=False)
        while msg:
            t = msg.get_type()
            if t == 'ATTITUDE_TARGET':
                self.current_set = {
                    'roll':  msg.body_roll_rate * 180 / np.pi,
                    'pitch': msg.body_pitch_rate * 180 / np.pi,
                    'yaw':   msg.body_yaw_rate * 180 / np.pi,
                }
            elif t == 'ATTITUDE':
                self.current_act = {
                    'roll':  msg.rollspeed * 180 / np.pi,
                    'pitch': msg.pitchspeed * 180 / np.pi,
                    'yaw':   msg.yawspeed * 180 / np.pi,
                }
            msg = self.mav.recv_match(blocking=False)

        # Atualiza os dados e os gráficos
        if hasattr(self, 'current_set') and hasattr(self, 'current_act'):
            now = time.time() - self.start_time
            for axis in ['roll', 'pitch', 'yaw']:
                self.data[axis]['t'].append(now)
                self.data[axis]['set'].append(self.current_set[axis])
                self.data[axis]['act'].append(self.current_act[axis])

                maxlen = 1000
                for k in ['t', 'set', 'act']:
                    self.data[axis][k] = self.data[axis][k][-maxlen:]

                lset, lact = self.lines[axis]
                lset.set_data(self.data[axis]['t'], self.data[axis]['set'])
                lact.set_data(self.data[axis]['t'], self.data[axis]['act'])
                self.axes[axis].relim()
                self.axes[axis].autoscale_view()
                getattr(self, f'canvas_{axis}').draw()

        self.after(50, self.update_plot)

if __name__ == "__main__":
    PIDCalibrator().mainloop()
