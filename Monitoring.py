'''
Implements different methods/classes to get static as well as dynamic state of the physical machine and VMs
'''
from __future__ import print_function
import os
import subprocess
import Driver
import libvirt
import VirtualMachine
import re
import DriverVirsh
import psutil # requires installation of psutil library i.e., sudo apt-get install python-psutil
from PerfCounter import PerfCounter

from xml.dom import minidom
from xml.etree import ElementTree
qemuUri='qemu:///system'
hostname="numaserver"


# returns the total number of cores in the Machine
class Monitoring:
    #self.perfCounter

    def __init__(self):
        ''' Constructor for this class. '''
        print( "Calling Monitoring constructor")
        self.perfCounter = PerfCounter()
        print(" Monitoring constructor Called")


    #probe hardware performance (this method should be called every period before calling getIPC and  getMisses methods) to get latest values
    def probeWPerformance(self ):
        self.perfCounter.probe()

    #returns the  IPC for a VM given the list of cores that the VM is running
    def getIPC(self, cores):
            return self.perfCounter.getIPC(cores)


    #returns the  MPI for a VM given the list of cores that the VM is running
    def getMPI(self, cores):
        return self.perfCounter.getMPI( cores)



    def getDomainInfo(self, domain):
        dom = Driver.getDomainByID(domain)
        name = dom.name()
        id = domain
        host = hostname
        type = "silver"
        if name.lower().startswith("g"):
            type = "gold"
        vm = VirtualMachine.VirtualMachine(domain, name, id, host, type)
        return vm

    def getCurrentState(self):
        domains = Driver.getActiveDomains()
        virtualMachines = []


        for domain in domains:
            dom = Driver.getDomainByID(domain)
            if dom.name() != "loadgen_sigmetrics":
                vm = self.getDomainInfo(domain)
                vm.setVcpus(self.getVcpusInfo(domain))
                vm.setNodeset(self.getNodeSet(domain))
                vm.setMemorySize(self.getMemorySize(domain))
                virtualMachines.append(vm)
        return virtualMachines

    def monitor_system(self):
        virtualMachines = self.getCurrentState()
        #numatop = self.getNumaState()
        #Actuator.performMapping(virtualMachines, numatop)

    def getHostCPUMap():
        try:
            return Driver.getHostCPUMap()

        except libvirt.libvirtError:
            print('Failed to get host CPU Map')
            sys.exit(1)

    def getVcpusCpuMaps(domainID):
        try:
            return Driver.getVcpusCpuMaps(domainID)

        except libvirt.libvirtError:
            print('Failed to get vcpu map')
            sys.exit(1)

    def start(self, q):
        print("Monitoring started")
        self.monitor_system()
        print("Monitoring finished")

    def getNodeSet(self, domainID):
        try:
            return DriverVirsh.getNodeSet(domainID)

        except libvirt.libvirtError:
            print('Failed to get Node info')
            sys.exit(1)

    def getMemorySize(self, domainID):
        try:
            return DriverVirsh.getMemorySize(domainID)

        except libvirt.libvirtError:
            print('Failed to get memory size info')
            sys.exit(1)

    def getVcpusInfo(self, domainID):
        try:
            return Driver.getVcpusInfo(domainID)

        except libvirt.libvirtError:
            print('Failed to get vcpu info')
            sys.exit(1)

    def getTotalCores(self):
        """ Number of available virtual or physical CPUs on this system, i.e.
        user/real as output by time(1) when called with an optimally scaling
        userspace-only program"""

        # cpuset
        # cpuset may restrict the number of *available* processors
        try:
            m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                          open('/proc/self/status').read())
            if m:
                res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
                if res > 0:
                    return res
        except IOError:
            pass
        # Python 2.6+
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except (ImportError, NotImplementedError):
            pass
        # Windows
        try:
            res = int(os.environ['NUMBER_OF_PROCESSORS'])
            if res > 0:
                return res
        except (KeyError, ValueError):
            pass
        # BSD
        try:
            sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'],
                                      stdout=subprocess.PIPE)
            scStdout = sysctl.communicate()[0]
            res = int(scStdout)
            if res > 0:
                return res
        except (OSError, ValueError):
            pass
        # Linux
        try:
            res = open('/proc/cpuinfo').read().count('processor\t:')
            if res > 0:
                return res
        except IOError:
            pass
        # Solaris
        try:
            pseudoDevices = os.listdir('/devices/pseudo/')
            res = 0
            for pd in pseudoDevices:
                if re.match(r'^cpuid@[0-9]+$', pd):
                    res += 1
            if res > 0:
                return res
        except OSError:
            pass
        # Other UNIXes (heuristic)
        try:
            try:
                dmesg = open('/var/run/dmesg.boot').read()
            except IOError:
                dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
                dmesg = dmesgProcess.communicate()[0]

            res = 0
            while '\ncpu' + str(res) + ':' in dmesg:
                res += 1
            if res > 0:
                return res
        except OSError:
            pass
        raise Exception('Can not determine number of CPUs on this system')


    ##return the Physical machine  memory stat, swap memory stat
    # Memory stat
        #     'Total:    ' stats[0] --total physical memory.
        #     'available:  '+ stats[1]-- the memory that can be given instantly to processes without the system going into swap.
        #                              #This is calculated by summing different memory values depending on the platform and it is supposed to be used to monitor actual memory usage in a cross platform fashion.
        #     'percentage:   '+stats[2]
        #     'used:    '+stats[3] ---memory used, calculated differently depending on the platform and designed for informational purposes only. total - free does not necessarily match used.
        #     'free:   '+stats[4]---memory not being used at all (zeroed) that is readily available; note that this doesnt reflect the actual memory available (use available instead). total - used does not necessarily match free.
        #     'active: '+stats[5]---memory currently in use or very recently used, and so it is in RAM.
        #     'inactive:  '+stats[6]-- memory that is marked as not used.
        #     'buffers:   '+stats[7]--cache for things like file system metadata.
        #     'cached:   '+stats[8]---cache for various things.
    #Swap memory stat
        # total: swap[0]--total swap memory in bytes
        # used: swap[1]--used swap memory in bytes
        # free: swap[2]--free swap memory in bytes
        # percent: swap[3]--the percentage usage calculated as (total - available) / total * 100
        # sin: swap[4]--the number of bytes the system has swapped in from disk (cumulative)
        # sout: swap[5]--the number of bytes the system has swapped out from disk (cumulative)

    def getPMMemoryStat(self):

        stats =psutil.virtual_memory()
        swap=psutil.swap_memory()
        return stats, swap


    # Return system-wide network I/O statistics as a named tuple including the following attributes:
        # bytes_sent:stat[0] number of bytes sent
        # bytes_recv: stat[1]--number of bytes received
        # packets_sent: stat[2]--number of packets sent
        # packets_recv: stat[3] --number of packets received
        # errin:stat[4]--total number of errors while receiving
        # errout:stat[5]-- total number of errors while sending
        # dropin:stat[6]-- total number of incoming packets which were dropped
        # dropout:stat[7]-- total number of outgoing packets which were dropped (always 0 on OSX and BSD)

    def NetIOStat(self):

        stat=psutil.net_io_counters()
        return stat

     #return  the physical machine CPU cores stat and  utilization as percentage

    #  Return system CPU times as a named tuple. Every attribute represents the seconds the CPU has spent in the given mode. The attributes availability varies depending on the platform:

        # user: time spent by normal processes executing in user mode; on Linux this also includes guest time
        # system: time spent by processes executing in kernel mode
        # idle: time spent doing nothing
    # When percpu is True return a list of named tuples for each logical CPU on the system. First element of the list refers to first CPU, second element to second CPU and so on.
    # The order of the list is consistent across calls.

    # psutil.cpu_percent(interval=None, percpu=False)
    # Return a float representing the current system-wide CPU utilization as a percentage.
    #  When interval is > 0.0 compares system CPU times elapsed before and after the interval (blocking). When interval is 0.0 or None compares system CPU times elapsed since last call or module import, returning immediately.
    #  That means the first time this is called it will return a meaningless 0.0 value which you are supposed to ignore. In this case it is recommended for accuracy that this function be called with at least 0.1 seconds between calls.
    #  When percpu is True returns a list of floats representing the utilization as a percentage for each CPU. First element of the list refers to first CPU, second element to second CPU and so on. The order of the list is consistent across calls.
    def getCPUStat(self,perCPU=False):
        stat=psutil.cpu_times(percpu=perCPU)
        percent = psutil.cpu_percent(percpu=perCPU);

        return stat, percent;




    '''
    get hardware temperature
    requires  installation of lm-sensors library (i.e., sudo apt-get install lm-sensors)
    Return hardware temperatures. 
    Each entry is a named tuple representing a certain hardware temperature sensor 
    (it may be a CPU, an hard disk or something else, depending on the OS and its configuration).
     All temperatures are expressed in celsius unless fahrenheit is set to True. 
     If sensors are not supported by the OS an empty dict is returned. Example:
    '''
    def getTemp(self):
        if not hasattr(psutil, "sensors_temperatures"):
          sys.exit("platform not supported or upgrade your psutil version")
          temps = psutil.sensors_temperatures()# availble starting from version  5.1.0.
          return temps

    #returns the NUMA topology as a list(per NUMA Node): 
         #NUMA node id--
         #distance--relative distance from the rest NUMA Nodes including itself
         #memory size--the total memory size in that NUMA node (in kb)
        #cores--List of cores in the node
    def getNUMATopology(self):
        capsXML = Driver.getNUMATopology()
        caps = minidom.parseString(capsXML)
        host = caps.getElementsByTagName('host')[0]
        cells = host.getElementsByTagName('cell')
        print (cells.length)
        numa = []
        # iterate through the xml object to get the NUMA topology
        for cell in cells:
            node_id = cell.getAttribute('id')
            print (cell.firstChild.nodeValue)
            memory = cell.getElementsByTagName('memory')[0].firstChild.nodeValue
            distances = {proc.getAttribute('id'): proc.getAttribute('value')
                         for proc in cell.getElementsByTagName('sibling')
                         }  # if proc.getAttribute('id'): proc.getAttribute('value') not in distances }
            cores = [proc.getAttribute('id')
                     for proc in cell.getElementsByTagName('cpu')
                     ]
            node = {node_id: [memory, distances, cores]}
            numa.append(node)

        return numa

            
    #return VM memory stat
    def getVMMemoryStat(domainName):
        
        conn,dom = Driver.connectToDomain(domainName)
        
        stats = dom.memoryStats()
       
        conn.close()
        return stats

    #return VM CPU stat
    '''
    The getCPUStats takes one parameter, a boolean. 
    When False is used the statistics are reported as an aggregate of all the CPUs. 
    When True is used then each CPU reports its individual statistics. 
    Either way a list is returned. The statistics are reported in nanoseconds. 
    If a host has four CPUs, there will be four entries in the cpu_stats list.
    For more: https://libvirt.org/docs/libvirt-appdev-guide-python/en-US/html/libvirt_application_development_guide_using_python-Guest_Domains-Monitoring-vCPU.html 
    '''
    def getVMCPUStat(domainName, perCPUStat=True):
        
        conn, dom = Driver.connectToDomain(domainName)
        
        stats = dom.getCPUStats(perCPUStat)
       
        conn.close()
        return stats


    #Returns Network stat for a domain as a list:
    #     'read bytes:    ' stats[0]
    #     'read packets:  '+ stats[1]
    #     'read errors:   '+stats[2]
    #     'read drops:    '+stats[3]
    #     'write bytes:   '+stats[4]
    #     'write packets: '+stats[5]
    #     'write errors:  '+stats[6]
    #     'write drops:   '+stats[7]
    def getNetworkIOStat(domainName):
        
        conn, dom = Driver.connectToDomain(domainName)
        
        tree = ElementTree.fromstring(dom.XMLDesc())
        iface = tree.find('devices/interface/target').get('dev')
        stats = dom.interfaceStats(iface)
        
        conn.close()
        return stats

        #get cpu and momory info about the domain
    def getDomainStat(self, domainName):
        conn, dom = Driver.connectToDomain(domainName)

        if dom == None:
            print('Failed to find the domain '+domainName, file=sys.stderr)
            exit(1)

        state, maxmem, mem, cpus, cpuTime = dom.info()
        

        conn.close()

        return state, maxmem, mem, cpus, cpuTime

   



    





