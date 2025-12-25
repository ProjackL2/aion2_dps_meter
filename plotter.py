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
        self.ax_table = None
        self.animation_plot = None
        self.animation_table = None
        self.annot = None

    def run_blocking(self):
        self._run_plot()

        if self.fig:
            plt.close(self.fig)


    def _run_plot(self):
        from matplotlib.gridspec import GridSpec

        self.fig = plt.figure(figsize=(16, 8))
        self.fig.canvas.manager.set_window_title('Aion 2: OCR DPS Meter')

        # Grid: graph (70%), table (30%)
        gs = GridSpec(1, 2, figure=self.fig, width_ratios=[7, 3], 
                     wspace=0.05, left=0.06, right=0.98, top=0.95, bottom=0.08)

        # Main DPS graph
        self.ax = self.fig.add_subplot(gs[0, 0])
        self.ax.set_xlabel('Time (sec)')
        self.ax.set_ylabel('Damage')
        self.ax.set_title('Damage Per Second', fontsize=12, fontweight='bold', pad=10)
        self.ax.grid(True, alpha=0.3)

        # Skill table area
        self.ax_table = self.fig.add_subplot(gs[0, 1])
        self.ax_table.axis('off')
        self.ax_table.set_title('Skills Statistics', fontsize=12, fontweight='bold', pad=10)
        self.ax_table.text(0.5, 0.5, 'No skill data available yet',
                           ha='center', va='center', fontsize=10, color='gray')

        self.line_moving, = self.ax.plot([], [], label='DPS', linewidth=2, color='#95E1D3')
        self.line_avg, = self.ax.plot([], [], label='Average DPS', linewidth=2, color='#FF6B6B')

        self.ax.legend(loc='upper left')

        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                       textcoords="offset points",
                                       bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.9),
                                       arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)

        self.animation_plot = FuncAnimation(
            self.fig, 
            self._update_plot_animation,
            interval=1000,
            blit=False,
            cache_frame_data=False
        )
        self.animation_table = FuncAnimation(
            self.fig,
            self._update_table_animation,
            interval=1000,
            blit=False,
            cache_frame_data=False
        )

        plt.show()

    def _prepare_table_data(self):
        if not self.damage_calculator.by_skills:
            return [], []

        headers = ['Skill Name', 'Count', 'Total', 'Average']
        rows = []
        for skill_name, skill_info in self.damage_calculator.by_skills.items():
            rows.append([
                skill_name,
                str(len(skill_info.damage)),
                f"{skill_info.total_damage:,.1f}",
                f"{skill_info.average:,.1f}",
                skill_info.total_damage
            ])

        rows.sort(key=lambda x: x[4], reverse=True)
        rows = [row[:4] for row in rows]

        return headers, rows

    def _update_table_animation(self, frame):
        if self.ax_table is None:
            return []

        self.ax_table.clear()
        self.ax_table.axis('off')
        self.ax_table.set_title('Skills Statistics', fontsize=12, fontweight='bold', pad=10)

        headers, rows = self._prepare_table_data()

        if not rows:
            self.ax_table.text(0.5, 0.5, 'No skill data available yet',
                              ha='center', va='center', fontsize=10, color='gray')
            return []

        cell_text = rows
        col_labels = headers

        table = self.ax_table.table(
            cellText=cell_text,
            colLabels=col_labels,
            cellLoc='left',
            loc='upper left',
            colWidths=[0.45, 0.18, 0.20, 0.17]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.2)

        return []

    def _update_plot_animation(self, frame):
        if self.last_timestamp == self.damage_calculator.last_timestamp_ms:
            return []

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
        return []

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