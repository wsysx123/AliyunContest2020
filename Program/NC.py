# coding=utf-8
import globalvar as gl
class NC:
    def __init__(self,id, type,CPU,Memory,Price,status,createTime):
        self.NCid = id
        self.type = type
        self.totalCPU = CPU
        self.totalMemory = Memory
        self.CanUseCPU = CPU
        self.CanUseMemory = Memory
        self.Price = Price
        self.status = status
        self.createTime = createTime
        self.c1Num = 0
        self.g1Num = 0
        self.r1Num = 0
        self.wantANum = 0
        self.wantBNum = 0
        self.wantCNum = 0

    # 从该物理机器内分配资源，成功返回True
    def create1Vm(self,Vm):
        if self.CanUseCPU >= Vm.CPU and self.CanUseMemory >= Vm.Memory:
            self.CanUseCPU = self.CanUseCPU - Vm.CPU
            self.CanUseMemory = self.CanUseMemory - Vm.Memory
            if Vm.TypeA == 2:#c1型
                self.c1Num = self.c1Num + Vm.TypeB * Vm.TypeA
                self.wantCNum =  self.wantCNum + 0.09
                self.wantANum =  self.wantANum - 1
            elif Vm.TypeA == 4:#g1型
                self.g1Num = self.g1Num + Vm.TypeB * Vm.TypeA
                self.wantCNum =  self.wantCNum + 0.09
                self.wantBNum =  self.wantBNum - 1
            elif Vm.TypeA == 8:#r1型
                self.r1Num = self.r1Num + Vm.TypeB * Vm.TypeA
                self.wantANum =  self.wantANum + 10
                self.wantBNum =  self.wantBNum + 1
            return True
        else:
            return False

    def release1Vm(self,Vm):
        self.CanUseCPU = self.CanUseCPU + Vm.CPU
        self.CanUseMemory = self.CanUseMemory + Vm.Memory
        if Vm.TypeA == 2:#c1型
            self.c1Num = self.c1Num + Vm.TypeB * Vm.TypeA
            self.wantCNum =  self.wantCNum - 0.09
            self.wantANum =  self.wantANum + 1
        elif Vm.TypeA == 4:#g1型
            self.g1Num = self.g1Num + Vm.TypeB * Vm.TypeA
            self.wantCNum =  self.wantCNum - 0.09
            self.wantBNum =  self.wantBNum + 1
        elif Vm.TypeA == 8:#r1型
            self.r1Num = self.r1Num + Vm.TypeB * Vm.TypeA
            self.wantANum =  self.wantANum - 10
            self.wantBNum =  self.wantBNum - 1