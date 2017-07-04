# -*- coding: utf-8 -*-

"""
Notes :
Besoin de séparer le thread de fréquence en deux ? Un qui poll le BusThread, 
un qui collecte et écrit les données fournies par le BusThread
"""

import os, time
import threading, Queue


class BusThread(threading.Thread):
    """ A thread dedicated to polling a given bus, receiving polling requests
        from an input queue
        
        input_q is the queue of polling requests for the bus. It's elements are
        structured like : [adress_to_poll , queue_to_output_the data]
        
        It outputs data on the output_queue, following the structure : 
        [adress_to_poll, data_collected, timestamp_of_data, name_of_thread]
    """
    def __init__(self, input_q):
        super(BusThread, self).__init__()
        self.input_q = input_q
        self.stoprequest = threading.Event()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                request = self.input_q.get(True, 0.1)
                adress = request[0]
                output_q = request[1]
                data = self.get_data(adress)
                timestamp = time.clock()
                output_q.put([adress, data, timestamp, self.name])
            except Queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(BusThread, self).join(timeout)

    def get_data(self, adress):
        """ Given an adress, returns the latest data available on this adress
        """
        data = self.name
        return data

class FrequencyThread(threading.Thread):
    """ A thread dedicated to requesting data from BusThread instances,
        based on the sensors data given in self.sensors and its frequency
        
        frequency is in Hertz\n
        sensors is a list composed of the required informations to poll the 
        sensors : [queue_of_sensors_bus , adress_of_sensor_on_bus]\n
        input_q is the queue from where to read the data sampled by the polled
        BusThreads \n
        filename is the name of the file where data is written\n
        NB : filename might be deduced from frequency, thus becoming redundant
    """
    def __init__(self, frequency, sensors, input_q):
        super(FrequencyThread, self).__init__()
        self.sensors = sensors
        self.frequency = frequency
        self.period = 1. / frequency
        self.input_q = input_q
        self.stoprequest = threading.Event()

    def run(self):
        # Set the clock
        lastAcquistionTime = time.clock()
        currentTime = lastAcquistionTime
        # Start the loop
        while not self.stoprequest.isSet():
            if ((currentTime - lastAcquistionTime) >= self.period):
                try:
                    # Update the acquistion time
                    lastAcquistionTime = time.clock()
                    # Loop on sensors
                    for sensor in self.sensors :
                        # Create the data request
                        request = [sensor[1] , self.input_q]
                        # Get the bus queue
                        bus_q = sensor[0]
                        # Send the request
                        bus_q.put(request)  
                except Queue.Empty:
                    continue
            currentTime = time.clock()

    def join(self, timeout=None):
        self.stoprequest.set()
        super(FrequencyThread, self).join(timeout)


class WriterThread(threading.Thread):
    """ A thread dedicated to requesting data from BusThread instances,
        based on the sensors data given in self.sensors and its frequency
        
        frequency is in Hertz\n
        sensors is a list composed of the required informations to poll the 
        sensors : [queue_of_sensors_bus , adress_of_sensor_on_bus]\n
        input_q is the queue from where to read the data sampled by the polled
        BusThreads \n
        filename is the name of the file where data is written\n
        NB : filename might be deduced from frequency, thus becoming redundant
    """
    def __init__(self, input_q, filename):
        super(WriterThread, self).__init__()
        self.input_q = input_q
        self.filename = filename
        self.stoprequest = threading.Event()
        self.jobsCount = 0

    def run(self):
        # Open the file and create its header
        file = open(self.filename , 'w')
        file.write("Sensor adress ; Data value ; Timestamp ; Bus\n")
        # Start the loop
        while not self.stoprequest.isSet():
            try:
                result = self.input_q.get(True,0.05) # blocking get() with 0.05s timeout
                # write data in file
                adress = result[0]
                data = result[1]
                timestamp = result[2]
                busName = result[3]
                self.jobsCount += 1
                output = "%d ;  %s ; %f ; %s\n" % (adress, data , timestamp, busName)
                file.write(output)
            except Queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(WriterThread, self).join(timeout)
        print "%s did %d jobs" % (self.name , self.jobsCount)

def main():
    # Create the input queues of the threads
    bus_1_q = Queue.Queue()
    bus_2_q = Queue.Queue()
    freq_1_q = Queue.Queue()
    freq_2_q = Queue.Queue()
    
    # Create the sensors list
    freq_1_sensors = [[bus_1_q , 0x18] , [bus_2_q , 0x21]]
    freq_2_sensors = [[bus_2_q , 0x11] , [bus_1_q , 0x11] ,  [bus_2_q , 0xb4]]

    #Create the buses & frequency threads
    bus_1_thread = BusThread(bus_1_q)
    bus_2_thread = BusThread(bus_2_q)
    freq_1_thread = FrequencyThread(50000, freq_1_sensors, freq_1_q)
    freq_2_thread = FrequencyThread(50000, freq_2_sensors, freq_2_q)
    writ_1_thread = WriterThread(freq_1_q , "file1.csv")
    writ_2_thread = WriterThread(freq_2_q , "file2.csv")


    # Start all threads   
    freq_1_thread.start()    
    freq_2_thread.start() 
    writ_1_thread.start()
    writ_2_thread.start()
    time.sleep(1.)
    bus_1_thread.start()    
    bus_2_thread.start() 
    

    print 'Assigned work to do to the threads'

    time.sleep(1.0)
    #time.sleep(2.0)
    
    print 'Stopping the threads'
    # Ask threads to die and wait for them to do it
    # NB : Always join the frequency threads before the bus threads
    freq_1_thread.join()
    freq_2_thread.join()
    writ_1_thread.join()
    writ_2_thread.join()
    bus_1_thread.join()
    bus_2_thread.join()
    
    print 'Threads stopped'
    


if __name__ == '__main__':
    main()
