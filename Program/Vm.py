# coding=utf-8
from Config import Config
import pulp as pulp


class Vm:
    def __init__(self, NameId,Type,start,end):
        conf = Config("./config.json")
        self.name = NameId
        self.Type = Type
        self.TypeA = None
        self.TypeB = None
        self.CPU = conf.readVM(Type)["cpu"]
        self.Memory = conf.readVM(Type)["memory"]
        self.Income = conf.readVM(Type)["incomePerHour"]*24
        self.createtime = start
        self.releasetime = end
        self.NC = None
        self.status = ""


    
    

