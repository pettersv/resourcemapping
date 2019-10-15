import threading
from Monitoring import Monitoring
from Interference import Interference
from Mapping import Mapping
from PMLoadDetection import PMLoadDetection
from config import Config
from Notification import Notification

class MonitoringThread (threading.Thread):
    def run(self):
        monitoringInstance = Monitoring()
        monitoringInstance.start(1)

class PerformanceAlertThread (threading.Thread):
    def run(self):
        performanceInstance = Performance()
        performanceInstance.start()

class InterferenceThread (threading.Thread):
    def run(self):
        interferenceInstance = Interference()
        interferenceInstance.start()

class MappingThread(threading.Thread):
    def run(self):
        mon = Monitoring()
        import time
        time=time.time()
        mon.probeWPerformance()
        mappingInstance = Mapping(mon)

       # mappingInstance.start_mem_pin(time);

        #
        algorithm = "alg" # vanila or alg
        mappingInstance.start(algorithm,time)

class LoadDetectionThread (threading.Thread):
    def run(self):
        config = Config('./credentials.properties')
        exchangeName = "test"
        notification = Notification(config, exchangeName)
        interval = 10 #this is the time interval in second where the system load is check (i.e., control Interval)
        loadDetectionInstance = PMLoadDetection(interval, notification)
        loadDetectionInstance.start()

print "Actimanager internal started!"

#start the monitoring thread
#monitoringThread = MonitoringThread()
#monitoringThread.start()

#start the load detection thread
#loadDetectionThread = LoadDetectionThread()
#loadDetectionThread.start()
#start the mapping thread
mappingThread = MappingThread()
mappingThread.start()

#sysdescr example
# sysdescr = SysDescr.SysDescr()
# #sysdescr.printMe()
# node = sysdescr.servernodes[1].sockets[1].numanodes[1]
# node2 = sysdescr.getNodeByID(11)
# node3 = sysdescr.getNodeByCoreID(287)
#
# print "Node "+str(node3.ID)
#
# dist = node.getDistance(node2)
# print "Distance "+str(dist)