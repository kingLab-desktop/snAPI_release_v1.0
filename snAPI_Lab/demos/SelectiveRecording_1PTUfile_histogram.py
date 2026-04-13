from datetime import datetime
from pathlib import Path
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
    # ============ Scan Grid Setup =============
    # Micro -> Voltage
    x_scale = 0.025      # volts per micron in X  #0.025
    y_scale = 0.009      # volts per micron in Y

    #Setting for multiple points scanning:
    scan_size =  10  #total scan size in micron
    half_range = scan_size/2      #+- 5 micron
    step = .5           # size of a step
    num_points = int(scan_size / step)            #21 points total (0,0) in the middle
    
    #Setting for one point scanning:
    # scan_size =  0  #total scan size in micron
    # half_range = scan_size/2      #+- 5 micron
    # step = .5           # size of a step
    # num_points = 1

    x_min_volt = -half_range * x_scale
    x_max_volt = +half_range * x_scale
    y_min_volt = -half_range * y_scale
    y_max_volt = +half_range * y_scale

    x_range = np.linspace(x_min_volt, x_max_volt, num_points)                #np.linspace(min x, max x, N) # N is how many evenly spaced points you want in interval [min x, max x]
    y_range = np.linspace(y_min_volt, y_max_volt, num_points)                #same for y  #create a NxN grid
    num_x = len(x_range)
    num_y = len(y_range)
    print()

    # ============ Initialize snAPI (Picoharp) =========
    sn = snAPI()
    sn.getDevice()

    sn.setLogLevel(LogLevel.DataFile, True)
    sn.initDevice(MeasMode.T3)
    sn.setLogLevel(LogLevel.Config, True)
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")

    # sn.histogram.setRefChannel(0)
    #sn.histogram.setBinWidth(1)  #num in picoseconds
    # #sn.histogram.setNumBins(30000)
    #sn.histogram.setHistorySize(1)

    # ================= PTU File Setup ===============================

    # Capture the current time ONCE (important for overnight runs)
    now = datetime.now()

    # Base directory for all PTU selective recordings
    ptu_base_dir = r"D:\\PTU Selective Recordings"

    # Create a subfolder named with today's date: DDMMYYYY
    today_folder = now.strftime("%m%d%Y")
    ptu_dir = Path(ptu_base_dir) / today_folder
    ptu_dir.mkdir(parents=True, exist_ok=True)

    # Experiment description and identifier
    # Change ONLY this line between runs
    experiment_description = "20260316_Alexa350_5Mhz_20x20_300s_QL" #TODO

    experiment_dir = ptu_dir / experiment_description
    experiment_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct the full PTU file path
    # Format: DDMMYYYY_<experiment>_HHMMSS.ptu
    ptu_path = str(
        experiment_dir /
        f"{now.strftime('%m%d%Y')}_{experiment_description}_{now.strftime('%H%M%S')}.ptu"
    )

    # Tell snAPI where to save the PTU file
    sn.setPTUFilePath(ptu_path)

    # === Start Continuous PTU Recording ===
    total_scan_time_ms = 10000000  # miliseconds
    sn.histogram.measure(total_scan_time_ms, waitFinished=False, savePTU=True)
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
                sn.histogram.clearMeasure()
                time.sleep(0.5)
                data, bins = sn.histogram.getData()
                sum_counts = sum([sum(c) for c in data])

                if sum_counts >= 10: #adjusted ben experiment to 0 from 8
                    time_per_point = 300 #in_seconds       #TO_DO
                    print(f"[{x:.3f},{y:.3f}]  → High signal! Staying {time_per_point}s..")
                    
                    collected_points += 1
                    #high_signal_coords.append((x, y))  # save point
                    ### ======== Set record time for each pixel ======== ###
                    time.sleep(time_per_point)          #in seconds
                else:
                    print(f"[{x:.3f},{y:.3f}]  → Low signal. Moving to next point.")
                    continue


    sn.histogram.stopMeasure()
    time.sleep(0.5)

    print(f"Scan complete. PTU saved at: {ptu_path}")
    print(f"Total points collected: {collected_points} out of {num_x * num_y}")

# ######## ==== Plot histogram ==== #########
#     if len(data):
#         plt.clf()
#         plt.plot(bins, data[1], linewidth=2.0, label='sync')
#         for c in range(1, 1+sn.deviceConfig["NumChans"]):
#             plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')
#         plt.xlabel('Time [ps]')
        
#         plt.ylabel('Counts')
#         plt.legend()
#         plt.title("Counts / Time")
#         plt.pause(1000)

####### ===== Slack Notification ===== ######
    import requests
    import json
    import sys

    SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

    def send_slack_message(message_text):
        slack_message = {
            'text': message_text
        }
    
        try:
            response = requests.post(
                SLACK_WEBHOOK_URL,
                data=json.dumps(slack_message),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print("Notification sent to Slack successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack notification: {e}")

    if __name__ == "__main__":
        # Example usage: wrap your main script logic or call this function at the end
        try:
            # Your main Python script logic goes here
            print("Script is running...")
            # ... some long-running task ...
            print("Script finished successfully.")
            send_slack_message("Your Python script has finished running successfully.")
        
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            send_slack_message(f"Your Python script encountered an error: {error_message}")
            # Re-raise the exception if needed
            # raise       