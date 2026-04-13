from snAPI.Main import *
import pandas as pd
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
print("Switched to:",matplotlib.get_backend())
import smtplib
from email.mime.text import MIMEText

if(__name__ == "__main__"):
    
    # select the device library
    sn = snAPI()
    # get first available device
    sn.getDevice()
    sn.setLogLevel(logLevel=LogLevel.DataFile, onOff=True)
    
    #initialize the device
    sn.initDevice(MeasMode.T2)
    
    # set the configuration for your device type
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")
    sn.histogram.setRefChannel(0)
    sn.histogram.setBinWidth(1)  #num in picoseconds
    sn.histogram.setNumBins(250000)

    # start histogram measurement
    sn.histogram.measure(acqTime=10000, waitFinished=True, savePTU=False) #num in miliseconds
    
    # get the data
    data, bins = sn.histogram.getData()
    
    # plot the histogram
    if len(data):
        plt.clf()
        plt.plot(bins, data[1], linewidth=2.0, label='sync')
        for c in range(1, 1+sn.deviceConfig["NumChans"]):
            plt.plot(bins, data[c], linewidth=2.0, label=f'chan{c}')
        plt.xlabel('Time [ps]')
        plt.ylabel('Counts')
        #plt.yscale('log', base =10, nonpositive = 'clip')
        plt.legend()
        plt.title("Counts / Time")
        plt.pause(0.001)

    plt.show(block=True)

    # === If using script to get IRF ===
    df = pd.DataFrame({'Time_ps': bins})
    for c in range(1, len(data)):
        df[f'Chan{c}'] = data[c]

    save_path = "C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\Result\\12012025_40MHz_IRF_T3_long.csv"
    df.to_csv(save_path, index=False)
    print(f"CSV saved to: {save_path}")

    # === Ignore ===
    #print(len(bins))        #should be 4096
    #print(len(data[0]))     #same44
    #print(df.shape) 

    # def send_email_notification():
    #     sender = "lb.quyen@gmail.com"
    #     receiver = "lb.quyen@gmail.com"
    #     password = "qkmo vrnk knqm skgc" 
    #     subject = "✅ IRF Python Script Completed"
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