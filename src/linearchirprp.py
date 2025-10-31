import time
import numpy as np
# from matplotlib import pyplot as plt
from rp_overlay import overlay
import rp
import os

# parameterlist
chirp_freq_low = np.float64(1e4) # Hz
chirp_freq_high = np.float64(1e5) # Hz
chirp_duration = np.float64(1e-4) # seconds
chirp_amp = np.float64(0.1) # Volts
chirp_reprate = np.float64(30) # Hz

# initialize FPGA and Red Pitaya
fpga = overlay()
rp.rp_Init()

# generator parameters
channel = rp.RP_CH_1
channel2 = rp.RP_CH_2
waveform = rp.RP_WAVEFORM_ARBITRARY


# Arbitrary Waveforms
N = 16384  # number of samples, buffer (max 16384)
t = np.arange(N, dtype=np.float64) * chirp_duration

x = rp.arbBuffer(N)
x2 = rp.arbBuffer(N)
phi_over_2pi = t * (chirp_freq_low + 0.5 * t * 
                    (chirp_freq_high - chirp_freq_low)/chirp_duration)
n_full_cycles = np.floor(phi_over_2pi[-1])
phi_over_2pi[phi_over_2pi>n_full_cycles] = n_full_cycles

x_temp = 0.5 * (1 - np.cos(2 * np.pi * phi_over_2pi))

for i in range(N):
    x[i] = float(x_temp[i])
    x2[i] = float(x_temp[i])


# burst mode settings
ncyc = 1     # only 1 cycle in the burst
nor = 65536        # 65536 -> burst repeats forever
period = int(np.round((np.float64(1e6)/chirp_reprate))) # period between bursts, not used for single burst
freq = float(1.0 / chirp_duration)

# reset the generator and acquisition system
rp.rp_GenReset()
rp.rp_AcqReset()

###### Generation #####
print("Gen_start")
rp.rp_GenWaveform(channel, waveform)
rp.rp_GenArbWaveform(channel, x.cast(), N)  # load the custom waveform into the generator
rp.rp_GenFreqDirect(channel, freq)
rp.rp_GenAmp(channel, chirp_amp)

# set burst mode properties
rp.rp_GenMode(channel, rp.RP_GEN_MODE_BURST)
rp.rp_GenBurstCount(channel, ncyc)  # single cycle burst
rp.rp_GenBurstRepetitions(channel, nor)  # forever repetition
rp.rp_GenBurstPeriod(channel, period)  

# repeate for channel 2
rp.rp_GenWaveform(channel2, waveform)
rp.rp_GenArbWaveform(channel2, x2.cast(), N)  # load the custom sine wave into the generator
rp.rp_GenFreqDirect(channel2, freq)
rp.rp_GenAmp(channel2, chirp_amp)

rp.rp_GenMode(channel2, rp.RP_GEN_MODE_BURST)
rp.rp_GenBurstCount(channel2, ncyc)  # single cycle burst
rp.rp_GenBurstRepetitions(channel2, nor)  # single repetition
rp.rp_GenBurstPeriod(channel2, period)  

# trigger source for the generator
rp.rp_GenTriggerSource(channel, gen_trig_sour)
rp.rp_GenOutEnableSync(True)

rp.rp_GenSynchronise()
#need to click ctrl c to capture 
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("acquisition loop interrupted.")

rp.rp_Release()
