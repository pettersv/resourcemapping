import VirtualCpu

class VirtualMachine(object):

    def __init__(self, domain, name, id, host, type):
        self.domain = domain
        self.name = name
        self.id = id
        self.host = host
        self.type = type
        self.placed = False


    def setVcpus(self, vCpus):
        self.vCpus = vCpus

    def setNodeset(self, nodeset):
        self.nodeset = nodeset

    def setMemorySize(self, memorySize):
        self.memorySize = memorySize

    def printMe(self):
        print "Name: " + self.name + " id " + str(self.id) + " host: " + self.host + " type: " + self.type + " domain: " + self.domain
        for vcpu in self.vCpus:
            print "VCPU: " + vcpu.no + " " + vcpu.state + " on core: " + vcpu.affinity + " pinned: " + vcpu.pinned