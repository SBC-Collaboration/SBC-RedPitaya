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


import numpy as np
from scipy.signal import fftconvolve

def pulse_compress(tx, rx):
    #remove DC offsets 
    tx = tx - np.mean(tx)
    rx = rx - np.mean(rx)

    #matched filter: time-reversed, conjugated chirp
    h = np.conj(tx[::-1])

    #linear convolution (matched filtering)
    y = fftconvolve(rx, h, mode="same")

    #rnvelope (magnitude)
    envelope = np.abs(y)

    return envelope

#Catrina's CODE (version 4 lol)
import numpy as np

def pulse_compress_fft(tx, rx):

    #remove DC offsets
    tx = tx - np.mean(tx)
    rx = rx - np.mean(rx)

    N = len(rx)

    #matched filter = time-reversed, conjugated 
    #so u can "slide it backwards"
    h = np.conj(tx[::-1])

    #FFTs (zero padding to be safe, h to rx length)
    H = np.fft.fft(h, n=N)
    R = np.fft.fft(rx, n=N)

    #multiplying ffts
    Y = R * H

    # inverse fft of multiplied
    y = np.fft.ifft(Y)

    #envelope (might want to remove abs later on)
    envelope = np.abs(y)

    return envelope
