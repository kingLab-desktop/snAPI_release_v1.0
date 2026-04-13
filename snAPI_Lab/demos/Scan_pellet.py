import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
from nidaqmx.constants import VoltageUnits
from snAPI.Main import *
import time
import smtplib
from email.mime.text import MIMEText

if(__name__ == "__main__"):
    # === Define scan grid ===
    x_range = np.linspace(-2, 2, 5)  #np.linspace(min x, max x, N) # N is how many evenly spaced points you want in interval [min x, max x]
    y_range = np.linspace(-0.5, 0.5, 5)   #same for y  #create a NxN grid
    num_x = len(x_range)
    num_y = len(y_range)

    intensity_map = np.zeros((num_y, num_x))

    # === Initialize snAPI (Picoharp) ===
    sn = snAPI()
    sn.getDevice()
    sn.setLogLevel(LogLevel.DataFile, True)
    sn.initDevice(MeasMode.T3)
    sn.setLogLevel(logLevel=LogLevel.Config, onOff=True)
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")

    # Optional trigger mode setup
    numChans = sn.deviceConfig["NumChans"]
    triggerMode = TrigMode.Edge if sn.deviceConfig["SyncTrigMode"] == "Edge" else TrigMode.CFD
    if False:
        if triggerMode == TrigMode.CFD:
            sn.device.setSyncTrigMode(TrigMode.CFD)
            sn.device.setInputTrigMode(-1, TrigMode.CFD)
            sn.device.setSyncCFD(100, 0)
            sn.device.setInputCFD(-1, 100, 0)
        elif triggerMode == TrigMode.Edge:
            sn.device.setInputTrigMode(-1, TrigMode.Edge)
            sn.device.setSyncEdgeTrig(-100, 0)
            sn.device.setInputEdgeTrig(-1, -50, 0)

    sn.histogram.setNumBins(10000)

    sn.histogram.measure(500, waitFinished=False, savePTU=False)  #in milisecs #num can be changed

    # === Begin scan ===
    with nidaqmx.Task() as ao_task:
        ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)
        ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)

        # === Scan in snake pattern ===
        for i, y in enumerate(y_range):
            x_seq = x_range if i % 2 == 0 else x_range[::-1]
            for j, x in enumerate(x_seq):
                x_idx = j if i % 2 == 0 else num_x - 1 - j

                print(f"[Scanning] X: {x:.3f}, Y: {y:.3f}")
                ao_task.write([x, y])

                sn.histogram.clearMeasure()
                time.sleep(0.1)
                data, bins = sn.histogram.getData()
                sum_counts = sum([sum(c) for c in data])

                intensity_map[i, x_idx] = sum_counts

    # def send_email_notification():
    #     sender = "lb.quyen@gmail.com"
    #     receiver = "lb.quyen@gmail.com"
    #     password = "qkmo vrnk knqm skgc" 
    #     subject = "✅ Python Script Completed"
    #     body = "Your scan script has finished running successfully!"

    #     msg = MIMEText(body)
    #     msg["Subject"] = subject
    #     msg["From"] = sender
    #     msg["To"] = receiver

    #     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #         server.login(sender, password)
    #         server.send_message(msg)
    #     print("Email notification sent!")

    # send_email_notification()

    # === Plot final heatmap ===
    plt.figure()
    plt.imshow(intensity_map, extent=[x_range[0], x_range[-1], y_range[0], y_range[-1]], origin='lower', aspect='auto', cmap='viridis')
    plt.colorbar(label="Integrated Intensity [cts]")
    plt.xlabel("X Voltage (V)")
    plt.ylabel("Y Voltage (V)")
    plt.title("Final Time Trace Intensity Map")
    plt.tight_layout()
    plt.show()

