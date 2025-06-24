import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
from pulseCompression import pulseCompress, simplePulseCompress

#Runs a simulated linear chirp and return signal with noise and performs pulse compression

def linear_chirp(center_freq, bandwidth, chirp_length):
    start_freq = center_freq - bandwidth/2
    end_freq = center_freq + bandwidth/2
    chirp_rate = (end_freq - start_freq)/chirp_length/2
    t = np.arange(chirp_length)
    freq = 2*np.pi * (chirp_rate * t + start_freq)
    return np.exp(1j * freq*t)


#Initial Parameters
N = 2048 #Data size
center_freq = 500
bandwidth = 300
chirp_length = 50

#Create signal out
tx_signal = linear_chirp(center_freq, bandwidth, chirp_length)

#Create received signal
delay = 1000
rx_amplitude = 0.5
noise_amplitude = 0.3
rx_signal = 1j * np.zeros(N)
rx_signal[delay:delay+chirp_length]=rx_amplitude * tx_signal
rx_signal += noise_amplitude * np.random.randn(N)

#Perform pulse compression
compressed_signal = pulseCompress(tx_signal, rx_signal.real)

#Plot
plt.figure()
plt.plot(compressed_signal)
plt.savefig('compressed.png')
plt.figure()
plt.plot(rx_signal.real)
plt.savefig('rx_signal.png')
plt.figure()
plt.plot(tx_signal.real)
plt.savefig('tx_signal.png')

# plt.figure()
# plt.plot(np.abs(res))
# plt.savefig('temp.png')