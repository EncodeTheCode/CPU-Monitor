import psutil
import tkinter as tk
from tkinter import ttk
import platform
import wmi
import random  # Simulated temperatures

# --- GUI Setup ---
root = tk.Tk()
root.title("CPU Monitor")
root.geometry("550x700")
root.configure(bg="#1e1e2f")
root.resizable(False, False)

# --- Styles ---
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1e1e2f", foreground="#ffffff", font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
style.configure("TButton", font=("Segoe UI", 12), padding=6)
style.configure("TProgressbar", troughcolor="#33334d", background="#4caf50", thickness=20)

# --- Scrollable frame setup ---
main_frame = tk.Frame(root, bg="#1e1e2f")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg="#1e1e2f", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

content_frame = tk.Frame(canvas, bg="#1e1e2f")
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# --- Header and CPU info ---
header = ttk.Label(content_frame, text="CPU Monitor", style="Header.TLabel")
header.pack(pady=10)

cpu_info_label = ttk.Label(content_frame, text="", wraplength=500)
cpu_info_label.pack(pady=5)

physical_frame = ttk.LabelFrame(content_frame, text="Physical Cores", padding=10)
physical_frame.pack(fill="x", padx=20, pady=10)

logical_frame = ttk.LabelFrame(content_frame, text="Logical / Virtual Cores", padding=10)
logical_frame.pack(fill="x", padx=20, pady=10)

update_btn = ttk.Button(content_frame, text="Update Info")
update_btn.pack(pady=15)

REFRESH_INTERVAL = 2000  # milliseconds

# --- Helper ---
def c_to_f(c):
    return c * 9 / 5 + 32

# --- Pre-create labels and bars ---
phys_labels = []
phys_bars = []
log_labels = []
log_bars = []

num_phys = psutil.cpu_count(logical=False)
num_log = psutil.cpu_count(logical=True)

for i in range(num_phys):
    label = ttk.Label(physical_frame, text="", anchor="w")
    label.pack(fill="x", pady=2)
    bar = ttk.Progressbar(physical_frame, length=450, maximum=100)
    bar.pack(pady=2)
    phys_labels.append(label)
    phys_bars.append(bar)

for i in range(num_log):
    label = ttk.Label(logical_frame, text="", anchor="w")
    label.pack(fill="x", pady=2)
    bar = ttk.Progressbar(logical_frame, length=450, maximum=100)
    bar.pack(pady=2)
    log_labels.append(label)
    log_bars.append(bar)

# --- WMI setup for base CPU info ---
w = wmi.WMI()
cpu_wmi = w.Win32_Processor()[0]
cpu_name = cpu_wmi.Name.strip()
base_clock = cpu_wmi.MaxClockSpeed  # nominal frequency in MHz

# --- Update function ---
def refresh_display():
    # psutil current system frequency
    freq = psutil.cpu_freq()
    current_freq = freq.current  # approximate current frequency

    cpu_info_label.config(
        text=f"CPU: {cpu_name}\n"
             f"Cores: {num_phys} Physical | {num_log} Logical\n"
             f"Current Frequency: {current_freq:.1f} MHz\n"
             f"Base/Nominal Clock: {base_clock} MHz\n"
             f"(Note: True Boost Clock per core cannot be read without hardware monitoring library)"
    )

    usage_all = psutil.cpu_percent(percpu=True)

    # Update physical cores
    for i in range(num_phys):
        usage = usage_all[i]
        temp_c = random.uniform(35, 70)  # simulated
        temp_f = c_to_f(temp_c)
        phys_labels[i].config(text=f"Core {i} | Usage: {usage:.1f}% | Temp: {temp_c:.1f}°C / {temp_f:.1f}°F")
        phys_bars[i]['value'] = usage

    # Update logical cores
    for i in range(num_log):
        usage = usage_all[i]
        temp_c = random.uniform(35, 70)
        temp_f = c_to_f(temp_c)
        log_labels[i].config(text=f"Logical Core {i} | Usage: {usage:.1f}% | Temp: {temp_c:.1f}°C / {temp_f:.1f}°F")
        log_bars[i]['value'] = usage

    # Update scroll region
    content_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

# --- Automatic update loop ---
def auto_update():
    refresh_display()
    root.after(REFRESH_INTERVAL, auto_update)

# --- Manual update ---
def manual_update():
    refresh_display()  # only update once

update_btn.config(command=manual_update)

# Start automatic periodic updates
auto_update()
root.mainloop()
