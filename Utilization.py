
from Monitoring import Monitoring
from VMMonData import VMMonData
from PMMonData import PMMonData
import time
import libvirt


class Utilization:

    def __init__(self):
        self.prevCpuTime = 0
        self.prevTimestamp = 0
        self.mon=Monitoring()



    def getVMUtilization(self, domainName):

        state, maxmem, mem, cpus, cputime=self.mon.getDomainStat(domainName)


        if not (state in [libvirt.VIR_DOMAIN_SHUTOFF,
                            libvirt.VIR_DOMAIN_CRASHED]):
            self.cpus = cpus

            curCPUTime = cputime - self.prevCpuTime
            self.prevCpuTime=cputime

            now= time.time()
            pcentbase = (((curCPUTime) * 100.0) /
                         ((now - self.prevTimestamp) * 1000.0 * 1000.0 * 1000.0))
            pcentGuestCpu = pcentbase / self.cpus

            self.prevTimestamp=now

            pcentCurrMem = mem * 100.0 / maxmem

        pcentGuestCpu = max(0.0, min(100.0, pcentGuestCpu))

        pcentCurrMem = max(0.0, min(pcentCurrMem, 100.0))

        vmUtil= VMMonData(domainName,cpus,pcentGuestCpu,maxmem, pcentCurrMem)
        return vmUtil



    def getPMUtilization(self):
        import platform
        name = platform.node()
        cpus=self.mon.getTotalCores()
        cpuStat, pcentHostCpu = self.mon.getCPUStat()
        memStat,swap = self.mon.getPMMemoryStat()
        pcentHostMem = memStat[2]
        memSize = memStat[0]

        mpUtil=PMMonData(name, cpus,pcentHostCpu,pcentHostMem,memSize)

        return mpUtil

# if __name__ == "__main__":
#
#     util = Utilization()
#     pm = util.getPMUtilization()
#     vm = util.getVMUtilization("sockshopubuntu")
#     print (pm.cpuPercent,pm.cpus, pm.memSize,pm.memPercent, pm.pmName)
#     print (vm.cpuPercent, vm.cpus, vm.memSize, vm.memPercent, vm.vmName)