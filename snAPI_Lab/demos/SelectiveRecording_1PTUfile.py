import os
import time
import numpy as np
import matplotlib.pyplot as plt
import nidaqmx
from nidaqmx.constants import VoltageUnits
from snAPI.Main import *
import smtplib
from email.mime.text import MIMEText

if __name__ == "__main__":
    # === Scan Grid Setup ===
    x_range = np.linspace(-0.1,0.1,1)                     #np.linspace(min x, max x, N) # N is how many evenly spaced points you want in interval [min x, max x]
    y_range = np.linspace(-0.1,0.1,5)                     #same for y  #create a NxN grid
    num_x = len(x_range)
    num_y = len(y_range)

    # === Initialize snAPI (Picoharp) ===
    sn = snAPI()
    sn.getDevice()

    sn.setLogLevel(LogLevel.DataFile, True)
    sn.initDevice(MeasMode.T3)
    sn.setLogLevel(LogLevel.Config, True)
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")

    sn.timeTrace.setNumBins(10000)
    sn.timeTrace.setHistorySize(1)

    # === PTU File Setup ===
    ptu_path = "D:\Quyen(temp)\Python\\11062025_StrepAlexa350\\SelectiveRecording_1PTU_trash.ptu"
    os.makedirs(os.path.dirname(ptu_path), exist_ok=True)
    if os.path.exists(ptu_path):
        os.remove(ptu_path)
    sn.setPTUFilePath(ptu_path)

    # === Start Continuous PTU Recording ===
    total_scan_time_ms = 10000000  # miliseconds
    sn.timeTrace.measure(total_scan_time_ms, waitFinished=False, savePTU=True)
    print(f"Started 2-min PTU recording")

    collected_points = 0
    #high_signal_coords = []  # store (x, y) positions with signal

    # === Galvo Scan ===
    with nidaqmx.Task() as ao_task:
        ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)
        ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=-10.0, max_val=10.0, units=VoltageUnits.VOLTS)

        for i, y in enumerate(y_range):
            x_seq = x_range if i % 2 == 0 else x_range[::-1]
            for j, x in enumerate(x_seq):
                ao_task.write([x, y])
                time.sleep(0.01)  # galvo settle

                # === 0.5s Signal Check (non-interruptive)
                sn.timeTrace.setHistorySize(1)
                time.sleep(0.5)
                counts, _ = sn.timeTrace.getData()
                max_counts = sum([sum(c) for c in counts])

                if max_counts >= 130000:
                    print(f"[{x:.3f},{y:.3f}]  → High signal! Staying 2s..")
                    
                    collected_points += 1
                    #high_signal_coords.append((x, y))  # save point
                    ### === Set record time for each pixel ===
                    time.sleep(30) #in seconds
                else:
                    print(f"[{x:.3f},{y:.3f}]  → Low signal. Moving to next point.")
                    continue

    sn.timeTrace.stopMeasure()
    time.sleep(0.5)

    print(f"Scan complete. PTU saved at: {ptu_path}")
    print(f"Total points collected: {collected_points} out of {num_x * num_y}")

    # # === Plot collected points ===
    # if high_signal_coords:
    #     xs, ys = zip(*high_signal_coords)
    #     plt.figure(figsize=(5, 5))
    #     plt.scatter(xs, ys, color='red', s=80, label='High signal')
    #     plt.scatter(x_range, y_range, color='gray', alpha=0.3, label='Scan range')
    #     plt.title("High-signal points in XY scan")
    #     plt.xlabel("X voltage (V)")
    #     plt.ylabel("Y voltage (V)")
    #     plt.legend()
    #     plt.grid(True)
    #     plt.axis('equal')
    #     plt.show()
    # else:
    #     print("No high-signal points detected, nothing to plot.")

    def send_email_notification():
        sender = "lb.quyen@gmail.com"
        receiver = "lb.quyen@gmail.com"
        password = "qkmo vrnk knqm skgc" 
        subject = "✅ Python Script Completed"
        body = "Your scan script has finished running successfully!"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email notification sent!")

    send_email_notification()