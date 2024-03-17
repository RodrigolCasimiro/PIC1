import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import numpy as np

# Setup the serial connection
Uno = serial.Serial("/dev/cu.usbmodemF412FA75E7882", 9600)

# Buffer para armazenar os tempos entre deteções
time_differences = deque(maxlen=100)  # Ajuste o maxlen conforme necessário

# Contador para acompanhar o número de valores recebidos
count = 49

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

def update_histogram(frame):
    global count  # Use a variável global 'count'
    try:
        while True:  # Loop para ler múltiplos valores se disponíveis
            if Uno.inWaiting() > 0:  # Se há dados esperando para serem lidos
                line = Uno.readline().decode("utf-8").rstrip()
                _, time_since_last_pulse, _ = line.split(" ")
                print(line)
                time_differences.append(float(time_since_last_pulse))
                count += 1

                if count >= 10:  # Atualiza o gráfico a cada 10 valores lidos
                    ax.clear()
                    ax.hist(time_differences, bins=30, color='#88CCEE')  # Ajuste os bins conforme necessário
                    ax.set_title("Histograma do Tempo Entre Detecções")
                    ax.set_xlabel("Tempo (ms)")
                    ax.set_ylabel("Frequência")
                    count = 0  # Reset o contador após atualizar o gráfico
                    break  # Sair do loop após atualizar o gráfico
    except Exception as e:
        print(f"Error: {e}")

ani = animation.FuncAnimation(fig, update_histogram, interval=100, cache_frame_data=False)  # Ajuste o intervalo conforme necessário

plt.show()
