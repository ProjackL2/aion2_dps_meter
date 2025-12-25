import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from collections import deque


class Plotter:
    def __init__(self, damage_calculator, max_points=100):
        self.damage_calculator = damage_calculator
        self.max_points = max_points

        self.timestamps = deque(maxlen=max_points)
        self.moving_avg_data = deque(maxlen=max_points)
        self.avg_data = deque(maxlen=max_points)

        self.start_timestamp = 0
        self.last_timestamp = 0
        self.fig = None
        self.ax = None
        self.animation = None
        self.annot = None

    def run_blocking(self):
        self._run_plot()

        if self.fig:
            plt.close(self.fig)


    def _run_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_xlabel('Time (sec)')
        self.ax.set_ylabel('DPS')
        self.ax.set_title('DPS Meter - Damage Per Second')
        self.ax.grid(True, alpha=0.3)

        self.line_moving, = self.ax.plot([], [], label='Moving Average', linewidth=2, color='#FF6B6B')
        self.line_avg, = self.ax.plot([], [], label='Average', linewidth=2, color='#95E1D3')

        self.ax.legend(loc='upper left')

        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                       textcoords="offset points",
                                       bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.9),
                                       arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)

        self.animation = FuncAnimation(
            self.fig, 
            self._update_plot, 
            interval=1000,
            blit=False,
            cache_frame_data=False
        )

        plt.tight_layout()
        plt.show()

    def _update_plot(self, frame):
        if self.last_timestamp == self.damage_calculator.last_timestamp_ms:
            return self.line_moving, self.line_avg

        if self.start_timestamp == 0:
            self.start_timestamp = self.damage_calculator.last_timestamp_ms

        current_time = self.damage_calculator.last_timestamp_ms - self.start_timestamp
        self.last_timestamp = self.damage_calculator.last_timestamp_ms

        self.timestamps.append(current_time / 1000.00)
        self.moving_avg_data.append(self.damage_calculator.moving_average)
        self.avg_data.append(self.damage_calculator.average_per_time)

        if len(self.timestamps) > 0:
            times = list(self.timestamps)
            self.line_moving.set_data(times, list(self.moving_avg_data))
            self.line_avg.set_data(times, list(self.avg_data))

            self.ax.relim()
            self.ax.autoscale_view()

            if len(times) > 0:
                if len(times) < self.max_points:
                    self.ax.set_xlim(0, max(times[-1], 10))
                else:
                    self.ax.set_xlim(times[0], times[-1])

        return self.line_moving, self.line_avg

    def _find_nearest_point(self, x, y, line):
        xdata, ydata = line.get_data()
        if len(xdata) == 0:
            return None, None, None

        ax_bbox = self.ax.get_window_extent()
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_scale = (xlim[1] - xlim[0]) / ax_bbox.width if ax_bbox.width > 0 else 1
        y_scale = (ylim[1] - ylim[0]) / ax_bbox.height if ax_bbox.height > 0 else 1

        distances = []
        for xi, yi in zip(xdata, ydata):
            dx = (xi - x) / x_scale if x_scale != 0 else 0
            dy = (yi - y) / y_scale if y_scale != 0 else 0
            distances.append(dx**2 + dy**2)

        if not distances:
            return None, None, None

        min_idx = distances.index(min(distances))
        return min_idx, xdata[min_idx], ydata[min_idx]

    def _on_hover(self, event):
        if event.inaxes != self.ax:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()
            return

        for line, label in [(self.line_moving, 'Moving Average'), (self.line_avg, 'Average')]:
            if len(line.get_xdata()) == 0:
                continue

            idx, x, y = self._find_nearest_point(event.xdata, event.ydata, line)

            if idx is not None:
                display_coords = self.ax.transData.transform((x, y))
                event_coords = (event.x, event.y)
                distance = ((display_coords[0] - event_coords[0])**2 + 
                           (display_coords[1] - event_coords[1])**2)**0.5

                if distance < 20:
                    self.annot.xy = (x, y)
                    text = f"{label}\nTime: {x:.2f}s\nDPS: {y:.2f}"
                    self.annot.set_text(text)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return

        if self.annot.get_visible():
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()