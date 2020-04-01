# coding=utf-8
from NC import NC
from Config import Config
from Vm import Vm
import ilp
import pulp as pulp
import datetime
import globalvar as gl

class NCPool:
    def __init__(self,StartTime):
        conf = Config("./config.json")
        NCList = conf.conf["ContestConfig"]["NC"]
        self.Pool = {}
        self.NCResource = {}
        self.NCResource["NT-1-2"] = {}
        self.NCResource["NT-1-4"] = {}
        self.NCResource["NT-1-8"] = {}
        self.CPUNum = 0
        self.MachineNum = 0
        self.LoseNum = 0
        self.BuyServerCost = 0
        self.NewBuyList = []
        self.NewResource = {}
        self.NewResource["NT-1-2"] = {"CPU":0,"Memory":0}
        self.NewResource["NT-1-4"] = {"CPU":0,"Memory":0}
        self.NewResource["NT-1-8"] = {"CPU":0,"Memory":0}
        # 遍历每种机型
        for NTRaw in NCList:
            self.NCResource[NTRaw] = {"TotalCPU":0,"TotalMemory":0,"CanUseCPU":0,"CanUseMemory":0,"Num":0}
            # 遍历每种机型内每台机器
            for i in range(NCList[NTRaw]["initNum"]):
                if i==0:
                    self.Pool[NTRaw] = []
                NewNT = NC("nc_"+str(self.MachineNum+1),NTRaw,NCList[NTRaw]["maxCPU"],NCList[NTRaw]["maxMemory"],NCList[NTRaw]["price"],"free",StartTime)
                self.BuyServerCost = self.BuyServerCost + NewNT.Price
                self.Pool[NTRaw].append(NewNT)
                if "TotalCPU" in self.NCResource[NTRaw]:
                    self.NCResource[NTRaw]["TotalCPU"] = NewNT.totalCPU +self.NCResource[NTRaw]["TotalCPU"]
                    self.NCResource[NTRaw]["TotalMemory"] = NewNT.totalMemory + self.NCResource[NTRaw]["TotalMemory"]
                    self.NCResource[NTRaw]["Num"] = self.NCResource[NTRaw]["Num"] +1
                self.MachineNum = self.MachineNum + 1
                gl.get_value('OP').writenewnc((gl.get_value("NowDate"),NewNT.NCid,"running",NewNT.totalCPU,NewNT.totalMemory,NewNT.type,NewNT.totalCPU-NewNT.CanUseCPU,NewNT.totalMemory-NewNT.CanUseMemory,NewNT.createTime))
            self.CPUNum = self.CPUNum + self.NCResource[NTRaw]["TotalCPU"]

    def GetNCCanUseSum(self,type):
        cpu = 0
        mem = 0
        for NC in self.Pool[type]:
            cpu = cpu + NC.CanUseCPU
            mem = mem + NC.CanUseMemory
        return cpu,mem
    
    def UpdateNCCanUseSum(self):
        cpu,mem = self.GetNCCanUseSum("NT-1-2")
        self.NCResource["NT-1-2"]["CanUseCPU"] = cpu
        self.NCResource["NT-1-2"]["CanUseMemory"] = mem

        cpu,mem = self.GetNCCanUseSum("NT-1-4")
        self.NCResource["NT-1-4"]["CanUseCPU"] = cpu
        self.NCResource["NT-1-4"]["CanUseMemory"] = mem

        cpu,mem = self.GetNCCanUseSum("NT-1-8")
        self.NCResource["NT-1-8"]["CanUseCPU"] = cpu
        self.NCResource["NT-1-8"]["CanUseMemory"] = mem

    def GetNT4_Want(self):
        A = 0
        B = 0
        C = 0
        for NC in self.Pool["NT-1-4"]:
            A = A + NC.wantANum
            B = B + NC.wantBNum
            C = C + NC.wantCNum

        return A,B,C


    # CPU数量，用于计算维护成本
    def GetCPUNum(self):
        return self.CPUNum

    # 机器数量，用于计算购买运费
    def GetMachineNum(self):
        return self.MachineNum

    # 断供数量
    def GetLoseNum(self):
        return self.LoseNum

    def GetBuyServerCost(self):
        return self.BuyServerCost
            
    def SortNCPool(self,NC):
        return NC.CanUseMemory

    def SortN4Pool_A(self,NC):
        return NC.wantANum

    def SortN4Pool_B(self,NC):
        return NC.wantBNum
    
    def SortN4Pool_C(self,NC):
        return NC.wantCNum

    def SortPool(self):
        #self.Pool["NT-1-4"].sort(key=self.SortNCPool,reverse=False)#True为可用量从大到小
        self.Pool["NT-1-2"].sort(key=self.SortNCPool,reverse=False)
        self.Pool["NT-1-8"].sort(key=self.SortNCPool,reverse=False)

    def create1Vm(self,NewECS,DisPlan):        
        # 物理主机资源分配算法
        # # 判断虚拟机型号，设定不同的物理主机
        PlaceNC = None
        A,B,C = self.GetNT4_Want()
        if NewECS.TypeA==2:
            if DisPlan[1]>0:# 将1型虚机分配给2型主机
                # 2型主机按对A的需求量进行升序排序
                self.Pool["NT-1-4"].sort(key=self.SortN4Pool_A,reverse=True)
                for NC in self.Pool["NT-1-4"]:
                    if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                        PlaceNC = NC
                        break
                DisPlan[1] = DisPlan[1] - NewECS.TypeB         
            elif DisPlan[0] >0:# 将1型虚机分配给1型主机
                DisPlan[0] = DisPlan[0] - NewECS.TypeB
                for NC in self.Pool["NT-1-2"]:
                    if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                        PlaceNC = NC
                        break
        elif NewECS.TypeA==4:
            if DisPlan[2]>0:# 将2型虚机分配给2型主机
                DisPlan[2] = DisPlan[2] - NewECS.TypeB
                self.Pool["NT-1-4"].sort(key=self.SortN4Pool_B,reverse=True)
                for NC in self.Pool["NT-1-4"]:
                    if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                        PlaceNC = NC
                        break
        elif NewECS.TypeA==8:
            if C > NewECS.TypeB:
                if DisPlan[3]>0:# 将3型虚机分配给2型主机
                    DisPlan[3] = DisPlan[3] - NewECS.TypeB
                    self.Pool["NT-1-4"].sort(key=self.SortN4Pool_C,reverse=True)
                    for NC in self.Pool["NT-1-4"]:
                        if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                            PlaceNC = NC
                            break
                elif DisPlan[4]>0:# 将3型虚机分配给3型主机
                    DisPlan[4] = DisPlan[4]- NewECS.TypeB
                    for NC in self.Pool["NT-1-8"]:
                        if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                            PlaceNC = NC
                            break
            else:
                if DisPlan[4]>0:# 将3型虚机分配给3型主机
                    DisPlan[4] = DisPlan[4]- NewECS.TypeB
                    for NC in self.Pool["NT-1-8"]:
                        if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                            PlaceNC = NC
                            break
                elif DisPlan[3]>0:# 将3型虚机分配给2型主机
                    DisPlan[3] = DisPlan[3] - NewECS.TypeB
                    self.Pool["NT-1-4"].sort(key=self.SortN4Pool_C,reverse=True)
                    for NC in self.Pool["NT-1-4"]:
                        if NC.CanUseMemory > NewECS.Memory and NC.CanUseCPU >NewECS.CPU:
                            PlaceNC = NC
                            break
            
        
        # 该机器不是新机，为待移动机器，先释放之前的资源
        if NewECS.NC != None:
            # 要判断一下新旧版块是否相同，相同就不用移动了
            # 因此self.NCResource[Type]["CanUseMemory"]可能会产生负数，但是不影响整体结果
            if NewECS.NC.type == PlaceNC.type:
                # 不需要移动，输出当前的位置
                gl.get_value('OP').writevm((gl.get_value('NowDate'),NewECS.name,NewECS.status,NewECS.NC.NCid,NewECS.Type,NewECS.CPU,NewECS.Memory,NewECS.createtime,"\\N" if NewECS.releasetime == datetime.datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date() else NewECS.releasetime))
                return None,NewECS.Income
            else:
                # 需要移动
                # 此时先要先判断一下要移动去的地方有没有资源，要是没有就不移动了
                OldNC = NewECS.NC
                if PlaceNC.create1Vm(NewECS) == True:
                    OldNC.release1Vm(NewECS)
                    NewECS.NC = PlaceNC
                    #self.release1Vm(NewECS,False)
                else:
                    return NewECS,NewECS.Income
        if PlaceNC != None and PlaceNC.create1Vm(NewECS) == True:
            # 物理主机中分配资源成功，从资源池中再次进行记录
            NewECS.status = "running"
            NewECS.NC = PlaceNC
        else:
            #物理机资源不够了，分配失败
            self.LoseNum = self.LoseNum+NewECS.TypeA
            NewECS.status = "lose"
            NewECS.Income = 0
        
        return NewECS,NewECS.Income


    def release1Vm(self,VM,output = True):
        VM.status = "release"
        VM.NC.release1Vm(VM)

        # 物理主机回收算法
        # 释放日志
        if output ==False:
            return
        gl.get_value('OP').writevm((gl.get_value('NowDate'),VM.name,VM.status,VM.NC.NCid,VM.Type,VM.CPU,VM.Memory,VM.createtime,"\\N" if VM.releasetime == datetime.datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date() else VM.releasetime))

    def Classify_ecs(self,EcsList):
        # 判断虚拟机型号，设定不同的物理主机
        ProClass = {"1v2":0,"1v4":0,"1v8":0}
        for NewECS in EcsList:
            if NewECS.Type.endswith('.large'):# 必须加上点，否则无法区分
                NewECS.TypeB = 2
            elif NewECS.Type.endswith('.xlarge'):
                NewECS.TypeB = 4
            elif NewECS.Type.endswith('.2xlarge'):
                NewECS.TypeB = 8
            

            if NewECS.Type.startswith('ecs.c1'):
                ProClass["1v2"] = ProClass["1v2"] +NewECS.TypeB
                NewECS.TypeA = 2
            elif NewECS.Type.startswith('ecs.g1'):
                ProClass["1v4"] = ProClass["1v4"] +NewECS.TypeB
                NewECS.TypeA = 4
            elif NewECS.Type.startswith('ecs.r1'):
                ProClass["1v8"] = ProClass["1v8"] +NewECS.TypeB
                NewECS.TypeA = 8
        return ProClass

    # 百分比数据的分段转换函数
    def PercentTrans(self,val):
        if val >= 0.9:
            return val
        elif val>= 0.7:
            return val*0.9
        elif val>=0.5:
            return val*0.7
        else:
            return val*0.3

    def NewNCpercent(self):
        Percent = []
        CPUPercent = self.NCResource["NT-1-2"]["CanUseCPU"] / self.NCResource["NT-1-2"]["TotalCPU"]
        MemPercent = self.NCResource["NT-1-2"]["CanUseMemory"] / self.NCResource["NT-1-2"]["TotalMemory"]
        Percent.append(self.PercentTrans((CPUPercent*MemPercent)))

        CPUPercent = self.NCResource["NT-1-4"]["CanUseCPU"] / self.NCResource["NT-1-4"]["TotalCPU"]
        MemPercent = self.NCResource["NT-1-4"]["CanUseMemory"] / self.NCResource["NT-1-4"]["TotalMemory"]
        Percent.append(self.PercentTrans((CPUPercent*MemPercent)))
        Percent.append(self.PercentTrans((CPUPercent*MemPercent)))
        Percent.append(self.PercentTrans((CPUPercent*MemPercent)))

        CPUPercent = self.NCResource["NT-1-8"]["CanUseCPU"] / self.NCResource["NT-1-8"]["TotalCPU"]
        MemPercent = self.NCResource["NT-1-8"]["CanUseMemory"] / self.NCResource["NT-1-8"]["TotalMemory"]
        Percent.append(self.PercentTrans((CPUPercent*MemPercent)))
            
        return Percent

    def SumN(self):
        N1 = self.NCResource["NT-1-2"]["Num"]
        N2 = self.NCResource["NT-1-4"]["Num"]
        N3 = self.NCResource["NT-1-8"]["Num"]
        return N1,N2,N3

    def SumT(self,EcsList):
        ProClassify = self.Classify_ecs(EcsList)
        T1 = ProClassify["1v2"]
        T2 = ProClassify["1v4"]
        T3 = ProClassify["1v8"]
        return T1,T2,T3


    # 线性规划无解时，断供某些机器
    def DeleteEcs(self,NewList):
        delta = [0,0,0]# 新增的三种虚拟机型的台数
        NT1,NT2,NT3 = self.SumT(NewList)
        # 当前主机剩余量/新增虚拟主机的需求量  越小则越紧缺
        if NT1 != 0:
            delta[0] = min(self.NCResource["NT-1-2"]["CanUseCPU"]/NT1,self.NCResource["NT-1-2"]["CanUseMemory"]/(NT1*2))
        if NT2 != 0:
            delta[1] = min(self.NCResource["NT-1-4"]["CanUseCPU"]/NT2,self.NCResource["NT-1-4"]["CanUseMemory"]/(NT2*4))
        if NT3 != 0:
            delta[2] = min(self.NCResource["NT-1-8"]["CanUseCPU"]/NT3,self.NCResource["NT-1-8"]["CanUseMemory"]/(NT3*8))
        # 找到最小的 ，将该类型的虚拟机删除一部分
        type = delta.index(min(delta))
        if type ==0:
            canput = min(self.NCResource["NT-1-2"]["CanUseCPU"],self.NCResource["NT-1-2"]["CanUseMemory"]/2)
            return self.RemoveVM(NewList,(type+1)*2,NT1 - canput)
        elif type ==1:
            canput = min(self.NCResource["NT-1-4"]["CanUseCPU"],self.NCResource["NT-1-4"]["CanUseMemory"]/4)
            return self.RemoveVM(NewList,(type+1)*2,NT2 - canput)
        elif type ==2:
            canput = min(self.NCResource["NT-1-8"]["CanUseCPU"],self.NCResource["NT-1-8"]["CanUseMemory"]/8)
            return self.RemoveVM(NewList,(type+1)*2,NT3 - canput)
        

    def RemoveVM(self,ECSList,type,num):
        loseVm = []
        num = num * 0.8
        for NewVM in ECSList:
            if NewVM.TypeA == type:
                loseVm.append(NewVM)
                #gl.get_value('OP').writevm((gl.get_value('NowDate'),NewVM.name,"lose",None,NewVM.Type,NewVM.CPU,NewVM.Memory,NewVM.createtime,"\\N" if NewVM.releasetime == datetime.datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date() else NewVM.releasetime,None,None,None))
                num = num- NewVM.TypeB
            if num == 0:
                break
        # 此处直接释放即可，因为处理的均为当日新机，还没有加入正式队列里
        for vm in loseVm:
            self.LoseNum = self.LoseNum + vm.TypeA
            ECSList.remove(vm)

        
        

    def Distribute_ECS(self,EcsList):
        T1,T2,T3 = self.SumT(EcsList)
        N1,N2,N3 = self.SumN()

        V_NUM = 5
        #变量，直接设置下限
        variables = [pulp.LpVariable('X%d'%i , lowBound = 0 , cat = pulp.LpInteger) for i in range(0 , V_NUM)]
        #目标函数
        PerC = self.NewNCpercent()
        c = [3.9*PerC[0],3.9*PerC[1],6.1*PerC[2],6.65*PerC[3],4.7*PerC[4]]
        objective = sum([c[i]*variables[i] for i in range(0 , V_NUM)])
        #约束条件
        constraints = []

        a1 = [1,0,0,0,0]
        constraints.append(sum([a1[i]*variables[i] for i in range(0 , V_NUM)]) <= 64*N1)
        a2 = [0,1,1,1,0]
        constraints.append(sum([a2[i]*variables[i] for i in range(0 , V_NUM)]) <= 96*N2)
        a3 = [0,2,4,8,0]
        constraints.append(sum([a3[i]*variables[i] for i in range(0 , V_NUM)]) <= 256*N2)
        a4 = [0,0,0,0,1]
        constraints.append(sum([a4[i]*variables[i] for i in range(0 , V_NUM)]) <= 64*N3)
        a5 = [1,1,0,0,0]
        constraints.append(sum([a5[i]*variables[i] for i in range(0 , V_NUM)]) >= T1)
        a6 = [0,0,1,0,0]
        constraints.append(sum([a6[i]*variables[i] for i in range(0 , V_NUM)]) >= T2)
        a7 = [0,0,0,1,1]
        constraints.append(sum([a7[i]*variables[i] for i in range(0 , V_NUM)]) >= T3)
        #print (constraints)

        res = ilp.solve_ilp(objective , constraints)
        return res

    def AddNT1(self,today,num):
        conf = Config("./config.json")
        NCList = conf.conf["ContestConfig"]["NC"]
        for i in range(num):
            NewNT = NC("nc_"+str(self.MachineNum+1),"NT-1-2",NCList["NT-1-2"]["maxCPU"],NCList["NT-1-2"]["maxMemory"],NCList["NT-1-2"]["price"],"init",today)
            self.BuyServerCost = self.BuyServerCost + NewNT.Price
            self.NewBuyList.append(NewNT)
            self.NewResource["NT-1-2"]["CPU"] = self.NewResource["NT-1-2"]["CPU"] +NewNT.totalCPU
            self.NewResource["NT-1-2"]["Memory"] = self.NewResource["NT-1-2"]["Memory"] +NewNT.totalMemory            
            self.MachineNum = self.MachineNum+1
            self.CPUNum = self.CPUNum + NewNT.totalCPU
            gl.get_value('OP').writenewnc((today,NewNT.NCid,NewNT.status,NewNT.totalCPU,NewNT.totalMemory,NewNT.type,NewNT.totalCPU-NewNT.CanUseCPU,NewNT.totalMemory-NewNT.CanUseMemory,NewNT.createTime))
    
    def AddNT2(self,today,num):
        conf = Config("./config.json")
        NCList = conf.conf["ContestConfig"]["NC"]
        for i in range(num):
            NewNT = NC("nc_"+str(self.MachineNum+1),"NT-1-4",NCList["NT-1-4"]["maxCPU"],NCList["NT-1-4"]["maxMemory"],NCList["NT-1-4"]["price"],"init",today)
            self.BuyServerCost = self.BuyServerCost + NewNT.Price
            self.NewBuyList.append(NewNT)
            self.NewResource["NT-1-4"]["CPU"] = self.NewResource["NT-1-4"]["CPU"] +NewNT.totalCPU
            self.NewResource["NT-1-4"]["Memory"] = self.NewResource["NT-1-4"]["Memory"] +NewNT.totalMemory
            self.MachineNum = self.MachineNum+1
            self.CPUNum = self.CPUNum + NewNT.totalCPU
            gl.get_value('OP').writenewnc((today,NewNT.NCid,NewNT.status,NewNT.totalCPU,NewNT.totalMemory,NewNT.type,NewNT.totalCPU-NewNT.CanUseCPU,NewNT.totalMemory-NewNT.CanUseMemory,NewNT.createTime))
    
    
    def AddNT3(self,today,num):
        conf = Config("./config.json")
        NCList = conf.conf["ContestConfig"]["NC"]
        for i in range(num):
            NewNT = NC("nc_"+str(self.MachineNum+1),"NT-1-8",NCList["NT-1-8"]["maxCPU"],NCList["NT-1-8"]["maxMemory"],NCList["NT-1-8"]["price"],"init",today)
            self.BuyServerCost = self.BuyServerCost + NewNT.Price
            self.NewBuyList.append(NewNT)
            self.NewResource["NT-1-8"]["CPU"] = self.NewResource["NT-1-8"]["CPU"] +NewNT.totalCPU
            self.NewResource["NT-1-8"]["Memory"] = self.NewResource["NT-1-8"]["Memory"] +NewNT.totalMemory
            self.MachineNum = self.MachineNum+1
            self.CPUNum = self.CPUNum + NewNT.totalCPU
            gl.get_value('OP').writenewnc((today,NewNT.NCid,NewNT.status,NewNT.totalCPU,NewNT.totalMemory,NewNT.type,NewNT.totalCPU-NewNT.CanUseCPU,NewNT.totalMemory-NewNT.CanUseMemory,NewNT.createTime))
    
    
    
    def sortNC(self,tmp):
        return tmp.createTime

    def StartTodayNC(self,today):
        self.NewBuyList.sort(key=self.sortNC)
        while len(self.NewBuyList)>0 and (self.NewBuyList[0].createTime + datetime.timedelta(days=10)) == today:
            NC = self.NewBuyList[0]
            self.NCResource[NC.type]["TotalCPU"] = NC.totalCPU +self.NCResource[NC.type]["TotalCPU"]
            self.NCResource[NC.type]["TotalMemory"] = NC.totalMemory + self.NCResource[NC.type]["TotalMemory"]
            self.NCResource[NC.type]["Num"] = self.NCResource[NC.type]["Num"] +1
            NC.status = "free"
            self.NewResource[NC.type]["CPU"] = self.NewResource[NC.type]["CPU"] - NC.totalCPU
            self.NewResource[NC.type]["Memory"] = self.NewResource[NC.type]["Memory"] - NC.totalMemory
            self.Pool[NC.type].append(NC)
            self.NewBuyList.remove(NC)
