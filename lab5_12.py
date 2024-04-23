import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, lfilter

# Функція для генерації сигналу
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    clean_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if show_noise:
        noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
        return clean_signal + noise
    else:
        return clean_signal

# Функція для фільтрації сигналу
def filter_signal(signal, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, signal)

# Початкові параметри
initial_amplitude = 1.0
initial_frequency = 1.0
initial_phase = 0.0
initial_noise_mean = 0.0
initial_noise_covariance = 0.1
initial_cutoff = 1.0

t = np.arange(0.0, 10.0, 0.01)
signal = harmonic_with_noise(t, initial_amplitude, initial_frequency, initial_phase,
                             initial_noise_mean, initial_noise_covariance, True)

fig, ax = plt.subplots(2, figsize=(8, 6))
plt.subplots_adjust(left=0.1, bottom=0.4, hspace=0.5)

# Малюємо початковий графік
ax[0].set_title('Graph of harmonic with noise')
l, = ax[0].plot(t, signal, lw=2, color='red')
ax[1].set_title('Filtered harmonic')
l_filtered, = ax[1].plot(t, signal, lw=2, color='blue')

# Створюємо слайдери
axcolor = 'lightgoldenrodyellow'
ax_amplitude = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_frequency = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.1, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
ax_noise_covariance = plt.axes([0.1, 0.0, 0.65, 0.03], facecolor=axcolor)
ax_cutoff = plt.axes([0.1, 0.25, 0.65, 0.03], facecolor=axcolor)

s_amplitude = Slider(ax_amplitude, 'Amplitude', 0.1, 10.0, valinit=initial_amplitude)
s_frequency = Slider(ax_frequency, 'Frequency', 0.1, 10.0, valinit=initial_frequency)
s_phase = Slider(ax_phase, 'Phase', 0.0, 2 * np.pi, valinit=initial_phase)
s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=initial_noise_mean)
s_noise_covariance = Slider(ax_noise_covariance, 'Noise Covariance', 0.0, 1.0, valinit=initial_noise_covariance)
s_cutoff = Slider(ax_cutoff, 'Cutoff', 0.1, 5.0, valinit=initial_cutoff)

# Функція для оновлення графіку
def update(val):
    amp = s_amplitude.val
    freq = s_frequency.val
    ph = s_phase.val
    noise_m = s_noise_mean.val
    noise_cov = s_noise_covariance.val
    show_noise = check.get_status()[0]
    
    l.set_ydata(harmonic_with_noise(t, amp, freq, ph, noise_m, noise_cov, show_noise))
    
    cutoff = s_cutoff.val
    filtered_signal = filter_signal(signal, cutoff, 100)
    l_filtered.set_ydata(filtered_signal)
    
    fig.canvas.draw_idle()

# Призначаємо функцію оновлення слайдерам
s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update)
s_noise_covariance.on_changed(update)
s_cutoff.on_changed(update)

# Додамо чекбокс для перемикання шуму
rax = plt.axes([0.8, 0.1, 0.1, 0.04], facecolor=axcolor)
check = CheckButtons(rax, ('Show Noise',), (True,))
def func(label):
    update(None)
check.on_clicked(func)

# Додамо кнопку для скидання параметрів
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_covariance.reset()
    s_cutoff.reset()
button.on_clicked(reset)

plt.show()
