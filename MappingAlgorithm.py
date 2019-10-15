from MappingAlgBase import MappingAlgBase
from ApplicationManager import ApplicationManager
from VirtualApplication import VirtualApplication
from  MapTriple import MapTriple

import VirtualMachine

class MappingAlgorithm(MappingAlgBase):

    vcpu_map = []




    def get_vpcu_map(self, mon, vmlist, metrics, threshold,time):
        appManager = ApplicationManager(time)
        apps=appManager.initVirtualApplication(mon, vmlist)
        appManager.save(mon, apps)
        appsMapped = appManager.decide( metrics, threshold)
        mem_map=[]
        for app in appsMapped:
            self.mapVM(app)
            if app.migrate==1:
                mem_map.append(app)



        return self.vcpu_map, mem_map
    #This uses the default KVM scheduler and the puprose of the method is the save monitoring data
    def vanila(self,mon, vmlist,time):
        appManager = ApplicationManager(time)
        apps=appManager.initVirtualApplication(mon, vmlist)
        appManager.save(mon, apps)


    def mapVM(self, app ):
         cores = app.cpus
         noCpus= len(app.cpus)
         self.saveConfig("VMCPU_MAP.csv",app.name+ str(app.cpus))

         for c in range(0,noCpus):
            core_alloc = cores[c]
            mapTriple = MapTriple(app.domainID, c, int(core_alloc))
            print "Mapping vcpu "+str(c)+" to core "+str(core_alloc)
            self.vcpu_map.append(mapTriple)
    
    def saveConfig(self,fileName, data):
        f = open(fileName, "a+")
        f.write(data)
        f.write("\n")
        f.close()

    def get_mem_map(self,mon, vmlist, time):
        #print vmlist


        appManager = ApplicationManager(time)
        appManager.initVirtualApplication(mon,vmlist)
        apps = appManager.loadBalance()
        #appManager.save(mon, apps)
        for app in apps:
            self.mapVM(app)

        memMap=self.mem_map(apps)

        return self.vcpu_map, memMap

    def mem_map(self, apps):
        memMap={}

        for app in apps:
            print app.name +" " +str(app.memoryNumaNodes) +" " +str(app.memorySize) + "\n"
            n=app.getMemoryNumaNodes()

            if len(n) >1:
                n.sort()
                min=n[0]
                max=n[len(n)-1]
                nodeset= str(min) +"-"+str(max)
            else:
                nodeset=n[0]
            memMap[app.name]=nodeset
        return memMap

    def checkNewVM(self, vmList):
        if self.vmList == None:
            self.vmList=vmList
            return False
        for vm in vmList:
            ret=False
            for v in self.vmList:
                if vm.domain == v.domain:
                    ret=True
            if ret== False:
                return False

        return True



