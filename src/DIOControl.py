import time
import rp 
from rp_overlay import overlay

fpga = overlay()
rp.rp_Init()

rp.rp_DpinSetDirection(rp.RP_DIO2_P, rp.RP_OUT)

print(f"DIO2p Direction: {rp.rp_DpinGetDirection(rp.RP_DIO2_P)[1]}")

while True:
    rp.rp_DpinSetState(rp.RP_DIO2_P, rp.RP_HIGH)
    time.sleep(1)
    rp.rp_DpinSetState(rp.RP_DIO2_P, rp.RP_LOW)
    time.sleep(1)