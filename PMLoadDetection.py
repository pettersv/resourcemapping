
from Utilization import Utilization
from Notification import Notification
from helper import *
import time


class PMLoadDetection:


    def __init__(self,intervalInSec,notification):
        self.overloadThreshold = 80
        self.underLoadThreshold = 10
        self.reportingInterval=10
        self.imbalanceRatio=5
        self.util=Utilization()
        self.interval=intervalInSec
        self.notification=notification
        self.loggingTime=time.time()


    #uses simple threshold based on CPU Utilization
    def isOverload(self):

        if float(self.util.getPMUtilization().cpuPercent) >= float(self.overloadThreshold):
            return True
        else:
            return False

    # uses simple threshold based on CPU Utilization
    def isUnderload(self):

        if self.util.getPMUtilization().cpuPercent() <= self.underloadThreshold:
            return True
        else:
            return False


    # check weather there is memory-cpu imbalance

    def imbalance(self):
        pmInfo = self.util.getPMUtilization()
        cpuPercent = pmInfo.cpuPercent
        memPercent = pmInfo.memPercent
        imbRatio = max(cpuPercent/memPercent, memPercent/cpuPercent) #signals the applications are either cpu or memory bound (implies one of the resources is wasted)
        if imbRatio > self.imbalanceRatio:
            return True
        else:
            return False


    def log(self, name,cpus, cpuPercent, memSize, memPercent):
        fileneme="utilization"+str(self.loggingTime)+".csv"
        filename = "test"  #TODO: fixme
        f = open(filename,"a+")
        f.write(name + ", " + str(cpus) + ", " + str(cpuPercent) + ", " + str(memSize) + ", " +str(memPercent))
        f.close()



    def detectLoadStatus(self):
        intervalCountoverload=0
        intervalCountunderload=0
        while True:
            pmInfo = self.util.getPMUtilization()
            self.log(pmInfo.pmName, pmInfo.cpus, pmInfo.cpuPercent, pmInfo.memSize, pmInfo.memPercent)

            time.sleep(self.interval)
            if self.isOverload() and ++intervalCountoverload >= self.reportingInterval: #send notification about the overload

                message = Message(MessageType.Overload, pmInfo)
                self.notification.RabbitMQConnection()
                self.notification.notify(message)

            elif pmInfo.cpuPercent < self.underLoadThreshold and ++intervalCountunderload >= self.reportingInterval:
                message = Message(MessageType.Underload, pmInfo)
                self.notification.RabbitMQConnection()
                self.notification.notify(message)

            else:
                intervalCountoverload = 0
                intervalCountunderload = 0


    def start(self):
        print("underload/overload detection started")
        self.detectLoadStatus()





