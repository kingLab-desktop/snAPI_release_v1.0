import nidaqmx
from nidaqmx.constants import AcquisitionType
import numpy as np

xp = np.linspace(0,0,1)
yp = np.linspace(0,0,1)

scan_points = [(x,y) for y in yp for x in xp]

with nidaqmx.Task() as ao_task:
    ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
    ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao1")

    for x, y in scan_points:
        ao_task.write([x,y])