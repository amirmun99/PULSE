import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --------- Configuration ----------
CSV_FILE = 'pulse_sample_data.csv'
# ----------------------------------

# Load CSV, treating Timestamp as float
df = pd.read_csv(CSV_FILE, dtype={'Timestamp': float}, low_memory=False)
print("Loaded CSV with columns:", df.columns.tolist())

# Use Timestamp as seconds since start
t = df['Timestamp']

# Compute metrics
g_force = np.sqrt(df['AccX']**2 + df['AccY']**2 + df['AccZ']**2)
vibration = np.sqrt(df['GyroX']**2 + df['GyroY']**2 + df['GyroZ']**2)
direction = np.degrees(np.arctan2(df['MagY'], df['MagX']))

roll = df['Roll']
pitch = df['Pitch']
yaw = df['Yaw']

# Set up figure and axes
fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
ax_g, ax_v, ax_d, ax_rpy = axes

ax_g.plot(t, g_force, label='G force (m/s²)')
ax_v.plot(t, vibration, label='Vibration (°/s)')
ax_d.plot(t, direction, label='Direction (°)')
ax_rpy.plot(t, roll, label='Roll (°)')
ax_rpy.plot(t, pitch, label='Pitch (°)')
ax_rpy.plot(t, yaw, label='Yaw (°)')

for ax in axes:
    ax.legend(loc='upper right')
    ax.grid(True)

# Add vertical indicator lines
vlines = [ax.axvline(t.iloc[0], color='k', lw=1) for ax in axes]

# Slider axis
slider_ax = plt.axes([0.2, 0.02, 0.6, 0.03])
time_slider = Slider(slider_ax, 'Time (s)', t.iloc[0], t.iloc[-1],
                     valinit=t.iloc[0], valstep=(t.iloc[1] - t.iloc[0]))

# Update function
def update(val):
    ts = time_slider.val
    for vl in vlines:
        vl.set_xdata(ts)
    fig.canvas.draw_idle()

time_slider.on_changed(update)

# Label x-axis
ax_rpy.set_xlabel('Time since start (s)')

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.show()
