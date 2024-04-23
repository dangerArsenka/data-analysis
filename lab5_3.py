import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Button, CheckboxGroup, Select
from bokeh.plotting import figure

# Власний фільтр
def custom_filter(signal):
    filtered_signal = np.convolve(signal, np.ones(10)/10, mode='same')  # Простий ковзний середній фільтр
    return filtered_signal

# Функція для генерації сигналу
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    clean_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if show_noise:
        noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
        return clean_signal + noise
    else:
        return clean_signal

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

source = ColumnDataSource(data=dict(t=t, signal=signal, filtered_signal=np.zeros_like(signal)))

plot = figure(title="Графік гармоніки зі шумом", height=300, width=600, y_range=(-3, 3))
line = plot.line('t', 'signal', source=source, line_width=3, line_alpha=0.6, color='red')
scatter = plot.scatter('t', 'signal', source=source, size=3, color='red', alpha=0.6)

plot_filtered = figure(title="Відфільтрована гармоніка", height=300, width=600, y_range=(-3, 3))
line_filtered = plot_filtered.line('t', 'filtered_signal', source=source, line_width=3, line_alpha=0.6, color='blue')
scatter_filtered = plot_filtered.scatter('t', 'filtered_signal', source=source, size=3, color='blue', alpha=0.6)

amplitude_slider = Slider(start=0.1, end=10.0, value=initial_amplitude, step=0.1, title="Amplitude")
frequency_slider = Slider(start=0.1, end=10.0, value=initial_frequency, step=0.1, title="Frequency")
phase_slider = Slider(start=0, end=2*np.pi, value=initial_phase, step=0.1, title="Phase")
noise_mean_slider = Slider(start=-1.0, end=1.0, value=initial_noise_mean, step=0.1, title="Noise Mean")
noise_covariance_slider = Slider(start=0.0, end=1.0, value=initial_noise_covariance, step=0.01, title="Noise Covariance")
cutoff_slider = Slider(start=0.1, end=5.0, value=initial_cutoff, step=0.1, title="Cutoff Frequency")

show_noise_checkbox = CheckboxGroup(labels=["Show Noise"], active=[0])

# Спадне меню для вибору типу графіку
plot_type_select = Select(title="Plot Type:", value="Line", options=["Line", "Scatter"])

def update_data(attrname, old, new):
    # Оновлюємо дані
    new_signal = harmonic_with_noise(t, amplitude_slider.value, frequency_slider.value, phase_slider.value,
                                     noise_mean_slider.value, noise_covariance_slider.value, 0 in show_noise_checkbox.active)
    source.data = dict(t=t, signal=new_signal, filtered_signal=custom_filter(new_signal))
    
    # Оновлюємо тип графіку
    if plot_type_select.value == "Line":
        line.visible = True
        scatter.visible = False
        line_filtered.visible = True
        scatter_filtered.visible = False
    elif plot_type_select.value == "Scatter":
        line.visible = False
        scatter.visible = True
        line_filtered.visible = False
        scatter_filtered.visible = True

for widget in [amplitude_slider, frequency_slider, phase_slider, noise_mean_slider, noise_covariance_slider, cutoff_slider]:
    widget.on_change('value', update_data)

def show_noise_checkbox_changed(attrname, old, new):
    update_data(None, None, None)

show_noise_checkbox.on_change('active', show_noise_checkbox_changed)

reset_button = Button(label="Reset", button_type="success")

def reset():
    amplitude_slider.value = initial_amplitude
    frequency_slider.value = initial_frequency
    phase_slider.value = initial_phase
    noise_mean_slider.value = initial_noise_mean
    noise_covariance_slider.value = initial_noise_covariance
    cutoff_slider.value = initial_cutoff

reset_button.on_click(reset)

controls = column(amplitude_slider, frequency_slider, phase_slider, noise_mean_slider, noise_covariance_slider,
                  cutoff_slider, show_noise_checkbox, reset_button, plot_type_select)

curdoc().add_root(row(column(plot, plot_filtered), controls))
curdoc().title = "Гармоніка зі шумом та фільтрацією"
