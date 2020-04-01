# coding=utf-8
from GetVm import GetVm
from NCPool import NCPool
from OutPut import writeCsv
from VmQueue import VmQueue
import datetime
from Config import Config
from Vm import Vm
import math
import globalvar as gl

class Schedule:
    def __init__(self,Files):
        gl._init()        
        self.NewVm = GetVm(Files)
        gl.set_value('NowDate',self.NewVm.starttime)
        #gl.set_value('Debug',True)
        gl.set_value('OP',writeCsv())
        gl.set_value('LastDate',None)
        self.NCPool = NCPool(gl.get_value('NowDate'))
        self.VQ = VmQueue()        
        self.AllCPUCost = 0
        self.AllBuyCost = 0
        self.AllLoseCost = 0
        self.NowMachineNum = 0
        self.AllEarnMoney = 0
        self.AllBuyServerCost = 0
        self.wantUseList = []
        conf = Config("./config.json")
        # 初始化保有量
        gl.set_value("NCKeepNum",{"NT-1-2":conf.readNC("NT-1-2")["initNum"],"NT-1-4":conf.readNC("NT-1-4")["initNum"],"NT-1-8":conf.readNC("NT-1-8")["initNum"]}) 

    def run(self):
        while self.NewVm.IsListNULL()==False or gl.get_value('NowDate') <= gl.get_value('LastDate') :     
            gl.set_value("TodayWantUse",{"NT-1-2":0,"NT-1-4":0,"NT-1-8":0})        
            print("Now Date:"+str(gl.get_value('NowDate')))
            gl.set_value('TodayEarnMoney',0)
            self.NCPool.StartTodayNC(gl.get_value('NowDate'))           # 开启新的物理主机    
            self.NCPool.UpdateNCCanUseSum()                             # 更新当前的可用资源数据   
            #self.NCPool.SortPool()
            self.AcceptNewECS()                                         # 处理新的虚拟主机
            self.ReleaseTodayECS()                                      # 释放虚拟主机
            self.AllEarnMoney = self.AllEarnMoney + gl.get_value('TodayEarnMoney') # 总收益
            self.AddNC()                                                # 报备主机
            self.Cal_Day_Money()                    # 计算金额,要放在报备后面，否则今日新报备主机的运营费用会减小
            self.WriteAllECSLog()                                       # 输出文件
            self.wantUseList.append(gl.get_value("TodayWantUse"))
            self.cal_WantUse() # 更新每种机型的最低保有量
            gl.set_value('NowDate',gl.get_value('NowDate')+datetime.timedelta(days=1))
        Final = self.AllEarnMoney - self.AllCPUCost - self.AllBuyCost - self.AllLoseCost
        info1 = " Maintenance Cost\t Freight Cost \t Lose Cost \t Income \t Profit"
        info2 = " %d \t\t %d \t\t %d \t %d \t %d"%(self.AllCPUCost,self.AllBuyCost,self.AllLoseCost,self.AllEarnMoney,Final)
        info3 = "Final Earn Rate: "+ str((Final)/(self.AllCPUCost + self.AllBuyCost + self.AllLoseCost))
        print(info1)
        print(info2)
        print(info3)
    
    # 计算近十天的各个机型需求量，修订保底策略
    def cal_WantUse(self):
        lastpos = 15
        if len(self.wantUseList)>16:
            self.wantUseList.remove(self.wantUseList[0])
        elif len(self.wantUseList)<=15:
            lastpos = len(self.wantUseList) - 1
        # 新增需求增速变大时，更新保有量
        gl.get_value("NCKeepNum")["NT-1-2"] = max((self.wantUseList[lastpos]["NT-1-2"] - self.wantUseList[0]["NT-1-2"])*2,gl.get_value("NCKeepNum")["NT-1-2"])
        gl.get_value("NCKeepNum")["NT-1-4"] = max((self.wantUseList[lastpos]["NT-1-4"] - self.wantUseList[0]["NT-1-4"])*2,gl.get_value("NCKeepNum")["NT-1-4"])
        gl.get_value("NCKeepNum")["NT-1-8"] = max((self.wantUseList[lastpos]["NT-1-8"] - self.wantUseList[0]["NT-1-8"])*2,gl.get_value("NCKeepNum")["NT-1-8"])
        print(self.wantUseList[lastpos])
        print(gl.get_value("NCKeepNum"))

    #读入今日新增虚机
    def AcceptNewECS(self):
        #读取现有所有机器
        OldList = self.VQ.q
        OldResource = self.NCPool.NCResource
        NewList = []
        while True:
            NewEcs = self.NewVm.get1vm(gl.get_value('NowDate'))
            if NewEcs!=None:#列表里还有机器
                #EcsListTmp.append(NewEcs)
                NewVm = Vm(NewEcs["vmid"],NewEcs["vmtype"],NewEcs["createtime"],NewEcs["releasetime"])
                # 添加今日新机至机器列表
                NewList.append(NewVm)
            else:#所有机器读完，释放所有资源
                break

        EcsListTmp = OldList+NewList
        
        # 机器排序
        # 线性规划
        while True:
            DisAns = self.NCPool.Distribute_ECS(EcsListTmp)
            if DisAns == None:
                # 无解，要删机器了
                self.NCPool.NCResource = OldResource # 恢复资源使用量，避免出现负数
                self.NCPool.DeleteEcs(NewList)
                EcsListTmp = OldList+NewList
            else:
                break
        loseVm = []
        # 依次给每个机器安排资源
        for NewECS in EcsListTmp:
            NewVM = self.NCPool.create1Vm(NewECS,DisAns)#给这一块ECS分配内存
            
            if NewVM != None:
                if NewVM.status == "running":#可以分配成功，计算收益
                    #self.gl.get_value('OP')writevm((gl.get_value('NowDate'),NewVM.name,NewVM.status,NewVM.NC.NCid,NewVM.Type,NewVM.CPU,NewVM.Memory,NewVM.createtime,NewVM.releasetime))
                    gl.get_value('OP').writevm((gl.get_value('NowDate'),NewVM.name,NewVM.status,NewVM.NC.NCid,NewVM.Type,NewVM.CPU,NewVM.Memory,NewVM.createtime,"\\N" if NewVM.releasetime == datetime.datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date() else NewVM.releasetime))
                    gl.set_value('TodayEarnMoney',gl.get_value('TodayEarnMoney')+NewVM.Income)
                else:#分配不成功，直接输出，正式答案里不输出
                    #self.VQ.delete(NewVM)#从现存队列中删除,删除以后队列自动向前移动，会漏数据
                    loseVm.append(NewVM)
                    #self.gl.get_value('OP')writevm((gl.get_value('NowDate'),NewVM.name,NewVM.status,NewVM.NC.NCid,NewVM.Type,NewVM.CPU,NewVM.Memory,NewVM.createtime,NewVM.releasetime))
                    #gl.get_value('OP').writevm((gl.get_value('NowDate'),NewVM.name,NewVM.status,None,NewVM.Type,NewVM.CPU,NewVM.Memory,NewVM.createtime,"\\N" if NewVM.releasetime == datetime.datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date() else NewVM.releasetime,None,None,None))
        self.VQ.q = EcsListTmp
        self.VQ.delete(loseVm)
        self.VQ.sortMyself()
                

    # 当日释放虚机
    def ReleaseTodayECS(self,AllRelease = False):
        while True:
            # 机器队列中弹出
            if AllRelease == False:
                VM = self.VQ.pop(gl.get_value('NowDate'))
            else:
                VM = self.VQ.pop(None)
            if VM != None:
                # 释放资源
                self.NCPool.release1Vm(VM)
            else:
                break

    def AddNC(self):
        conf = Config("./config.json")
        Num = gl.get_value("NCKeepNum")["NT-1-2"]
        Cpu = conf.readNC("NT-1-2")["maxCPU"]
        Mem = conf.readNC("NT-1-2")["maxMemory"]
        if (self.NCPool.NCResource["NT-1-2"]["CanUseCPU"] + self.NCPool.NewResource["NT-1-2"]["CPU"]<Num*Cpu or self.NCPool.NCResource["NT-1-2"]["CanUseMemory"] + self.NCPool.NewResource["NT-1-2"]["Memory"]<Num*Mem):
            CpuNeed = (Num*Cpu - self.NCPool.NCResource["NT-1-2"]["CanUseCPU"] - self.NCPool.NewResource["NT-1-2"]["CPU"])/64
            MemoryNeed = (Num*Mem - self.NCPool.NCResource["NT-1-2"]["CanUseMemory"]- self.NCPool.NewResource["NT-1-2"]["Memory"])/128
            self.NCPool.AddNT1(gl.get_value('NowDate'),max(math.ceil(CpuNeed),math.ceil(MemoryNeed)))
        Num = gl.get_value("NCKeepNum")["NT-1-4"]
        Cpu = conf.readNC("NT-1-4")["maxCPU"]
        Mem = conf.readNC("NT-1-4")["maxMemory"]
        if (self.NCPool.NCResource["NT-1-4"]["CanUseCPU"] + self.NCPool.NewResource["NT-1-4"]["CPU"]<Num*Cpu or self.NCPool.NCResource["NT-1-4"]["CanUseMemory"] + self.NCPool.NewResource["NT-1-4"]["Memory"]<Num*Mem):
            CpuNeed = (Num*Cpu - self.NCPool.NCResource["NT-1-4"]["CanUseCPU"]- self.NCPool.NewResource["NT-1-4"]["CPU"])/96
            MemoryNeed = (Num*Mem - self.NCPool.NCResource["NT-1-4"]["CanUseMemory"] -self.NCPool.NewResource["NT-1-4"]["Memory"])/256
            self.NCPool.AddNT2(gl.get_value('NowDate'),max(math.ceil(CpuNeed),math.ceil(MemoryNeed)))
        Num = gl.get_value("NCKeepNum")["NT-1-8"]
        Cpu = conf.readNC("NT-1-8")["maxCPU"]
        Mem = conf.readNC("NT-1-8")["maxMemory"]
        if (self.NCPool.NCResource["NT-1-8"]["CanUseCPU"] + self.NCPool.NewResource["NT-1-8"]["CPU"]<Num*Cpu or self.NCPool.NCResource["NT-1-8"]["CanUseMemory"] + self.NCPool.NewResource["NT-1-8"]["Memory"]<Num*Mem):
            CpuNeed = (Num*Cpu - self.NCPool.NCResource["NT-1-8"]["CanUseCPU"]- self.NCPool.NewResource["NT-1-8"]["CPU"])/104
            MemoryNeed = (Num*Mem - self.NCPool.NCResource["NT-1-8"]["CanUseMemory"]-self.NCPool.NewResource["NT-1-8"]["Memory"])/512
            self.NCPool.AddNT3(gl.get_value('NowDate'),max(math.ceil(CpuNeed),math.ceil(MemoryNeed)))


    
    # 计算当日成本
    def Cal_Day_Money(self):
        CPUNum = self.NCPool.GetCPUNum()
        MachineNum = self.NCPool.GetMachineNum()
        LoseNum = self.NCPool.GetLoseNum()
        conf = Config("./config.json")
        self.AllCPUCost = self.AllCPUCost +CPUNum * conf.XN
        self.AllBuyCost = self.AllBuyCost + (MachineNum - self.NowMachineNum)*conf.XP
        self.NowMachineNum = MachineNum
        self.AllLoseCost = self.AllLoseCost + LoseNum*conf.XD

    # 当日日志输出
    def WriteAllECSLog(self):            
        for Type in self.NCPool.Pool:
            for NC in self.NCPool.Pool[Type]:
                gl.get_value('OP').writenc((gl.get_value('NowDate'),NC.NCid,NC.status,NC.totalCPU,NC.totalMemory,NC.type,NC.totalCPU-NC.CanUseCPU,NC.totalMemory-NC.CanUseMemory,NC.createTime))
        gl.get_value('OP').writeMoney((gl.get_value('NowDate'),self.NCPool.BuyServerCost,self.AllCPUCost,self.AllBuyCost,self.AllLoseCost,self.AllEarnMoney))
        for NCRes in self.NCPool.NCResource:
            CPUPercent = 1 - (self.NCPool.NCResource[NCRes]["CanUseCPU"] / self.NCPool.NCResource[NCRes]["TotalCPU"])
            MemPercent = 1 - (self.NCPool.NCResource[NCRes]["CanUseMemory"] / self.NCPool.NCResource[NCRes]["TotalMemory"])
            gl.get_value('OP').writeResourece((gl.get_value('NowDate'),NCRes,self.NCPool.NCResource[NCRes]["TotalCPU"],self.NCPool.NCResource[NCRes]["TotalMemory"],self.NCPool.NCResource[NCRes]["CanUseCPU"],self.NCPool.NCResource[NCRes]["CanUseMemory"],CPUPercent,MemPercent))


        
