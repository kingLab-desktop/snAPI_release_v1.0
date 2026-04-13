from snAPI.Main import *

if(__name__ == "__main__"):

    start = 0
    length = 10
    
    sn = snAPI()
    sn.getDevice()
    
    #sn.getFileDevice(r"C:\Data\PicoQuant\default.ptu")
    sn.initDevice(MeasMode.T3)
    sn.loadIniConfig("C:\\Users\\1037 Lab\\Documents\\GitHub\\King-Lab\\Quyen\\snAPI_Lab\\demos\\config\\PH330_Edge.ini")
    
    # 1GB 
    sn.raw.measure(1000, 1024*1024*1024, True, False)
    data  = sn.raw.getData()
    sn.logPrint("from raw data")
    sn.logPrint("channel   | timetag") 
    sn.logPrint("-------------------")
    
    for i in range(start,start+length):
        sn.logPrint(f"{sn.raw.channel(data[i]):9} | {sn.raw.dTime_T3(data[i]):7}")