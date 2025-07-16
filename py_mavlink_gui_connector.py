#!/usr/bin/env python3
import time, numpy as np
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
        self.geometry("800x600")

        self.mav        = None
        self.start_time = None
        self.t_data     = []
        self.set_data   = []
        self.act_data   = []

        self._build_ui()

    def _build_ui(self):
        # Conexão
        frm = ttk.Frame(self); frm.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm, text="Serial URI:").pack(side="left")
        self.conn = ttk.Entry(frm, width=30)
        self.conn.insert(0, "serial:/dev/ttyACM0:57600")
        self.conn.pack(side="left", padx=5)
        ttk.Button(frm, text="Connect", command=self.connect).pack(side="left")

        # Parâmetros
        self.tree = ttk.Treeview(self, columns=("val","def"), show="headings", height=8)
        self.tree.heading("val", text="Valor Atual")
        self.tree.heading("def", text="Total Params")
        self.tree.pack(fill="x", padx=10, pady=5)

        # Gráfico
        plot_f = ttk.Frame(self); plot_f.pack(fill="both", expand=True, padx=10, pady=5)
        fig = Figure(figsize=(6,3), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("Tempo (s)"); self.ax.set_ylabel("Taxa (°/s)")
        self.lset, = self.ax.plot([], [], label="Setpoint")
        self.lact, = self.ax.plot([], [], label="Medido")
        self.ax.legend(loc="upper right")

        canvas = FigureCanvasTkAgg(fig, master=plot_f)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas = canvas

    def connect(self):
        uri = self.conn.get()
        if uri.startswith("serial:"):
            _, port, baud = uri.split(":")
            self.mav = mavutil.mavlink_connection(port, baud=int(baud))
        else:
            self.mav = mavutil.mavlink_connection(uri)

        print("⏳ aguardando heartbeat...")
        self.mav.wait_heartbeat()
        print("✅ conectado!")

        self.start_time = time.time()
        self.request_params()
        self.after(100, self.update_plot)

    def request_params(self):
        if not self.mav:
            return
        # limpa
        for i in self.tree.get_children():
            self.tree.delete(i)
        # solicita lista
        self.mav.mav.param_request_list_send(
            self.mav.target_system,
            self.mav.target_component
        )  # :contentReference[oaicite:4]{index=4}

        # lê respostas
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
        # processa mensagens pendentes
        msg = self.mav.recv_match(blocking=False)
        while msg:
            t = msg.get_type()
            if t == 'ATTITUDE_TARGET':
                self.current_set = msg.body_roll_rate * 180/np.pi
            elif t == 'ATTITUDE':
                self.current_act = msg.rollspeed     * 180/np.pi
            msg = self.mav.recv_match(blocking=False)

        # atualiza buffers
        if hasattr(self, "current_set") and hasattr(self, "current_act"):
            now = time.time() - self.start_time
            self.t_data.append(now)
            self.set_data.append(self.current_set)
            self.act_data.append(self.current_act)

            maxlen = 1000
            self.t_data   = self.t_data[-maxlen:]
            self.set_data = self.set_data[-maxlen:]
            self.act_data = self.act_data[-maxlen:]

            self.lset.set_data(self.t_data,   self.set_data)
            self.lact.set_data(self.t_data,   self.act_data)
            self.ax.relim(); self.ax.autoscale_view()
            self.canvas.draw()

        self.after(100, self.update_plot)

if __name__ == "__main__":
    # pip install pymavlink==2.4.42 matplotlib numpy
    PIDCalibrator().mainloop()

