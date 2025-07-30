import time
import numpy as np

class Plotter:
    def __init__(self, axes, lines, maxlen, window_seconds):
        self.axes = axes
        self.lines = lines
        self.maxlen = maxlen
        self.window = window_seconds
        self.start_time = time.time()
        self.data = {axis: {'t': [], 'set': [], 'act': []} for axis in axes}

    def update(self, current_set, current_act):
        now = time.time() - self.start_time
        for axis in self.axes:
            d = self.data[axis]
            d['t'].append(now)
            d['set'].append(current_set[axis])
            d['act'].append(current_act[axis])
            # mantém tamanho
            for k in d:
                d[k] = d[k][-self.maxlen:]
            # atualiza linhas
            lset, lact = self.lines[axis]
            lset.set_data(d['t'], d['set'])
            lact.set_data(d['t'], d['act'])
            # limites X
            self.axes[axis].relim()
            self.axes[axis].autoscale_view()
            self.axes[axis].set_xlim(max(0, now - self.window), now)