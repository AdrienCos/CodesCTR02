# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 11:05:38 2017

@author: adrien
"""


import os, time
#import threading, Queue
from multiprocessing import Process , Queue , Manager
from Queue import Empty
from math import sin


def BusProcess(input_q,output_q_list):
    """ A thread dedicated to polling a given bus, receiving polling requests
        from an input queue
        
        input_q is the queue of polling requests for the bus. It's elements are
        structured like : [adress_to_poll , queue_to_output_the data]
        
        It outputs data on the output_queue, following the structure : 
        [adress_to_poll, data_collected, timestamp_of_data, name_of_thread]
    """
    print "Hey ;)"
    while(1) : 
        try: 
            request = input_q.get(True, 0.1)
            adress = request[0]
            output_q = output_q_list[request[1]-1]
            data = get_data(adress)
            timestamp = time.clock()
            output_q.put([adress, data, timestamp, Process.name])
        except Empty:
            continue

def FrequencyProcess(frequency, sensors , id_q):
    """ A thread dedicated to requesting data from BusProcess instances,
        based on the sensors data given in self.sensors and its frequency
        
        frequency is in Hertz\n
        sensors is a list composed of the required informations to poll the 
        sensors : [queue_of_sensors_bus , adress_of_sensor_on_bus]\n
        input_q is the queue from where to read the data sampled by the polled
        BusProcesss \n
        filename is the name of the file where data is written\n
        NB : filename might be deduced from frequency, thus becoming redundant
    """

    # Set the parametrers
    period = 1./frequency
    # Set the clock
    lastAcquistionTime = time.clock()
    currentTime = lastAcquistionTime
    # Start the loop
    while (1):
        if ((currentTime - lastAcquistionTime) >= period):
            try:
                # Update the acquistion time
                lastAcquistionTime = time.clock()
                # Loop on sensors
                for sensor in sensors :
                    # Create the data request
                    request = [sensor[1] , id_q]
                    # Get the bus queue
                    bus_q = sensor[0]
                    # Send the request
                    bus_q.put(request)  
            except Empty:
                continue
        currentTime = time.clock()


def WriterProcess(input_q , filename):
    """ A thread dedicated to requesting data from BusProcess instances,
        based on the sensors data given in self.sensors and its frequency
        
        frequency is in Hertz\n
        sensors is a list composed of the required informations to poll the 
        sensors : [queue_of_sensors_bus , adress_of_sensor_on_bus]\n
        input_q is the queue from where to read the data sampled by the polled
        BusProcesss \n
        filename is the name of the file where data is written\n
        NB : filename might be deduced from frequency, thus becoming redundant
    """
    # Set the parameters
    jobsCount = 0
    # Open the file and create its header
    with open(filename , 'w') as f:
        f.write("Sensor adress ; Data value ; Timestamp ; Bus\n")
    f = open(filename , "a")
    # Start the loop
    while(1) :
        try:
            result = input_q.get(True,0.05) # blocking get() with 0.05s timeout
            #result = [1,"toto",0.2,"BusName"]
            # write data in file
            adress = result[0]
            data = result[1]
            timestamp = result[2]
            busName = result[3]
            jobsCount += 1
            output = "%d ;  %f ; %f ; %s\n" % (adress, timestamp, data, busName)
            #with open(filename , 'a') as f :
            f.write(output)
            
        except Empty:
            continue

def get_data(adress):
    """ Given an adress, returns the latest data available on this adress
    """
    data = "Dummy data"
    return sin(time.clock() * 100.)

#def main():
if __name__ == "__main__" : 
    
    # Create the manager
    manager = Manager()    
    
    # Create the input queues of the threads
    bus_1_q = manager.Queue()
    bus_2_q = manager.Queue()
    freq_1_q = manager.Queue()
    freq_2_q = manager.Queue()
    
    # Create the sensors list
    freq_1_sensors = [[bus_1_q , 0x19]]
    freq_2_sensors = [[bus_1_q , 0x11] , [bus_1_q , 0x31]]
    
    # Create the freq_q list
    freq_q_list = [freq_1_q , freq_2_q]

    #Create the buses & frequency threads
    bus_1_process = Process(target=BusProcess , args = (bus_1_q, freq_q_list,))
    bus_2_process = Process(target=BusProcess , args = (bus_2_q, freq_q_list, ))
    freq_1_process = Process(target = FrequencyProcess , args = (1600, freq_1_sensors, 1,))
    freq_2_process = Process(target = FrequencyProcess , args = (800, freq_2_sensors, 2,))
    writ_1_process = Process(target = WriterProcess , args = (freq_1_q , "file1.csv",))
    writ_2_process = Process(target = WriterProcess , args = (freq_2_q , "file2.csv",))


    # Start all threads   
    freq_1_process.start()    
    freq_2_process.start() 
    writ_1_process.start()
    writ_2_process.start()
    #time.sleep(1.)
    bus_1_process.start()    
    bus_2_process.start() 
    

    print 'Assigned work to do to the threads'

    time.sleep(1.0)
    #time.sleep(2.0)
    
    print 'Stopping the threads'
    # Ask threads to die and wait for them to do it
    # NB : Always join the frequency threads before the bus threads
    freq_1_process.terminate()
    freq_1_process.join()
    freq_2_process.terminate()
    freq_2_process.join()
    writ_1_process.terminate()
    writ_1_process.join()
    writ_2_process.terminate()
    writ_2_process.join()
    bus_1_process.terminate()
    bus_1_process.join()
    bus_2_process.terminate()
    bus_2_process.join()
    
    print 'Threads stopped'
    


#if __name__ == '__main__':
#    main()
