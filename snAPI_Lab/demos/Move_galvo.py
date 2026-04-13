import nidaqmx
from nidaqmx.constants import VoltageUnits
import numpy as np

x = np.linspace(0,0,1)
y = np.linspace(0, 0, 1)


with nidaqmx.Task() as ao_task:
    ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)
    ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)

    ao_task.write([x,y])