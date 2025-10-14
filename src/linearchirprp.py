import time
import numpy as np
# from matplotlib import pyplot as plt
from rp_overlay import overlay
import rp
import os

# parameterlist
chirp_freq_low = 1e4 # Hz
chirp_freq_high = 1e5 # Hz
chirp_duration = 1e-4 # seconds
chirp_amp = 0.1 # Volts
chirp_reprate = 30 # Hz

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
x_temp = 0.5 * (1 - np.cos(2 * np.pi *
                           t *
                           (chirp_freq_low + t *
                            ((chirp_freq_high - chirp_freq_low)/chirp_duration))
                           ))
for i in range(N):
    x[i] = float(x_temp[i])
    x2[i] = float(x_temp[i])


# burst mode settings
ncyc = 1     # only 1 cycle in the burst
nor = 1        # burst repeats only once
period = 10 # period between bursts, not used for single burst

# other generator parameters
gen_trig_sour = rp.RP_GEN_TRIG_SRC_INTERNAL
sample_rate_gen = 125e6 # / dec 

##### Acquisition parameters #####
trig_lvl = 0.5
trig_dly = 0
dec = rp.RP_DEC_8    # 125 MHz / 8 = 15.625 MHz sample rate not much but i think this can increase the amount we capture for a little longer 
sample_rate = 125e6 / dec # / dec 
acq_trig_sour = rp.RP_TRIG_SRC_AWG_PE  # using AWG (generator) as the trigger source

# reset the generator and acquisition system
rp.rp_GenReset()
rp.rp_AcqReset()

###### Generation #####
print("Gen_start")
rp.rp_GenWaveform(channel, waveform)
rp.rp_GenArbWaveform(channel, x.cast(), N)  # load the custom sine wave into the generator
rp.rp_GenFreqDirect(channel, 1 / chirp_duration)
rp.rp_GenAmp(channel, chirp_amp)

rp.rp_GenWaveform(channel2, waveform)
rp.rp_GenArbWaveform(channel2, x2.cast(), N)  # load the custom sine wave into the generator
rp.rp_GenFreqDirect(channel2, 1 / chirp_duration)
rp.rp_GenAmp(channel2, chirp_amp)

# set burst mode properties
rp.rp_GenMode(channel, rp.RP_GEN_MODE_BURST)
rp.rp_GenBurstCount(channel, ncyc)  # single cycle burst
rp.rp_GenBurstRepetitions(channel, nor)  # single repetition
rp.rp_GenBurstPeriod(channel, period)  

rp.rp_GenMode(channel2, rp.RP_GEN_MODE_BURST)
rp.rp_GenBurstCount(channel2, ncyc)  # single cycle burst
rp.rp_GenBurstRepetitions(channel2, nor)  # single repetition
rp.rp_GenBurstPeriod(channel2, period)  

# trigger source for the generator
rp.rp_GenTriggerSource(channel, gen_trig_sour)
rp.rp_GenOutEnableSync(True)

##### Acquisition #####
rp.rp_AcqSetDecimation(dec)

# Set trigger level and delay
rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trig_lvl)
rp.rp_AcqSetTriggerDelay(trig_dly)

# Start Acquisition
print("Acq_start")

# start acquisition --> trigger based on the AWG burst
rp.rp_AcqStart()


# Specify trigger - input 1 positive edge
rp.rp_AcqSetTriggerSrc(acq_trig_sour)

time.sleep(1)

rp.rp_GenSynchronise()
# rp.rp_GenTriggerOnly(channel)       # Trigger generator
# rp.rp_GenTriggerOnly(channel2)       # Trigger generator
# rp.rp_GenTriggerOnlyBoth()

print(f"Trigger state: {rp.rp_AcqGetTriggerState()[1]}")


# wait until the buffer is filled then empty before capturing the next sequence
while True:
    trig_state = rp.rp_AcqGetTriggerState()[1]
    if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
        break
print(f"Fill state: {rp.rp_AcqGetBufferFillState()[1]}")


while True:
    if rp.rp_AcqGetBufferFillState()[1]:
        break

time.sleep(1/chirp_reprate)

data_VA = np.zeros(N, dtype=float)
data_VB = np.zeros(N, dtype=float)

#need to click ctrl c to capture 
try:
    while True:
        # fetch the data for the previous record
        fbuff_A = rp.fBuffer(N)
        rp.rp_AcqGetOldestDataV(rp.RP_CH_2, N, fbuff_A)
        for i in range(N):
            data_VB[i] = data_VA[i]
            data_VA[i] = fbuff_A[i]
        
        # next acquisition
        rp.rp_AcqStart()
        # Specify trigger - input 1 positive edge
        rp.rp_AcqSetTriggerSrc(acq_trig_sour)
        
        rp.rp_GenSynchronise()
        # rp.rp_GenTriggerOnly(channel)
        # rp.rp_GenTriggerOnly(channel2)
        # rp.rp_GenTriggerOnlyBoth()
        
        # wait for the trigger event for sequence B
        while rp.rp_AcqGetTriggerState()[1] != rp.RP_TRIG_STATE_TRIGGERED:
            pass
        
        # wait for the buffer to fill for sequence B
        while not rp.rp_AcqGetBufferFillState()[1]:
            pass
        
        time.sleep(1/chirp_reprate)

except KeyboardInterrupt:
    print("acquisition loop interrupted.")


save_dir = r"stick_tube1"

#/tmp/
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Save the arrays
np.save(os.path.join(save_dir, "data_VA.npy"), data_VA)
np.save(os.path.join(save_dir, "data_VB.npy"), data_VB)



print(f"Data and plot saved to: {save_dir}")
print("Files created: data_VA.npy, data_VB.npy, last_capture1.png")

rp.rp_Release()
