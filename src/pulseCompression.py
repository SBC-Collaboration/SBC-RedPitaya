import numpy as np
import scipy.signal as sp

def pulseCompress(tx_signal, rx_signal):
    #Performs pulse compression
    #Convolve time-reversed transmit signal with received signal by multiplying elementwise in Fourier space
    N = len(rx_signal)
    #FFTs (Fast Fourier Transform)
    TX_signal = np.fft.fft(np.flip(pad_length(tx_signal,rx_signal)),n=N)
    RX_signal = np.fft.fft(rx_signal,n=N)
    
    #Apply Hilbert transform (eliminate negative frequency components, double positive ones)
    #Hilbert transform: reconstructs complex signal from real-only signal
    H=1j * np.zeros(N)
    H[1:N//2]=1
    H[N//2:]=-1
    H[len(H)//2]=1 if N % 2 == 0 else 0
    analytic_signal = TX_signal * (RX_signal + RX_signal * H * 1j)

    #Transform back to time domain via inverse FFT
    analytic_time = np.fft.ifft(analytic_signal)
    envelope = sp.envelope(analytic_time)
    return np.abs(envelope[0,:])

def simplePulseCompress(txSignal, rxSignal):
    #Performs pulse compression using built-in SciPy signal processing functions
    compressed_signal = sp.correlate(rxSignal, txSignal,"same")
    env = sp.envelope(compressed_signal)
    return np.abs(env[0,:])   

def pad_length(tx_signal, rx_signal):
    if len(tx_signal) > len(rx_signal):
        print("Rx signal cannot be shorter than Tx signal")
        return
    elif len(tx_signal) == len(rx_signal):
        return tx_signal
    else:
        new_tx_signal = 1j * np.zeros(len(rx_signal))
        new_tx_signal[1:len(tx_signal)+1] = tx_signal
        return new_tx_signal