# coding=utf-8
from GetVm import GetVm
from Vm import Vm
import datetime

class VmQueue:
    def __init__(self):
        self.q = []

    def sortbyreleasetime(self,Vm):
        return Vm.releasetime

    def sortMyself(self):
        self.q.sort(key=self.sortbyreleasetime)
    
    def pop(self,date):
        if len(self.q)>0:
            if (date!= None and self.q[0].releasetime == date) or date == None:
                    # 释放当前资源
                    re = self.q[0]  
                    self.q.remove(self.q[0])
                    return re
        return None
    
    def delete(self,vms):
        for vm in vms:
            self.q.remove(vm)