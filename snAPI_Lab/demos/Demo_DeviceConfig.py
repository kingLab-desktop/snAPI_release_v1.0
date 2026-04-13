from snAPI.Main import *

if(__name__ == "__main__"):
    
    # set the library for your device type
    sn = snAPI()
    sn.getDevice()
    sn.initDevice()
    
    # set the configuration for your device type
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")
    
    # print complete device config structure
    sn.logPrint(json.dumps(sn.deviceConfig, indent=2))
    sn.logPrint()
    
    # device serial number (name)
    sn.logPrint("----------------------------------------------")
    sn.logPrint("Serial Number:", sn.deviceConfig["ID"])
    
    # trigger/ discriminator level of all channels 
    sn.logPrint("----------------------------------------------")
    for channel in sn.deviceConfig["ChansCfg"]:
        if channel["TrigMode"] == "Edge":
            sn.logPrint("Chan", channel["Index"], "- TrigLvl:", channel["TrigLvl"])
        elif channel["TrigMode"] == "CFD":
            sn.logPrint("Chan", channel["Index"], "- DiscrLvl :", channel["DiscrLvl"])

    # print enable state channel 2 (this is the second channel - the first one has index 0)
    sn.logPrint("----------------------------------------------")
    sn.logPrint("Chan 1:", "enabled" if sn.deviceConfig["ChansCfg"][0]["ChanEna"] else "disabled")
