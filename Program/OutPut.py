# coding=utf-8
import csv
import globalvar as gl

class writeCsv:
    def __init__(self):
        vm =open('./output/vm.csv','w+',newline='')
        writer=csv.writer(vm)
        writer.writerow(('outputDate','vmId','status','ncId','vmType','cpu','memory','createTime','releaseTime'))
        vm.close()

        nc =open('./output/nc.csv','w+',newline='')
        writer=csv.writer(nc)
        writer.writerow(('outputDate','ncId','status','totalCpu','tocalMemory','machineType','usedCpu','usedMemory','createTime'))
        nc.close()

        newnc =open('./output/new_nc.csv','w+',newline='')
        writer=csv.writer(newnc)
        writer.writerow(('outputDate','ncId','status','totalCpu','tocalMemory','machineType','usedCpu','usedMemory','createTime'))
        newnc.close()

        # Money =open('./output/Money.csv','w+',newline='')
        # writer=csv.writer(Money)
        # writer.writerow(('outputDate','BuyServerCost','CPUCost','BuyCost','LoseCost','EarnMoney'))
        # Money.close()

        
        # Resource =open('./output/Resource.csv','w+',newline='')
        # writer=csv.writer(Resource)
        # writer.writerow(('outputDate','MachineType','TotalCPU','TotalMem','CPU','Mem','CPU%','Mem%'))
        # Resource.close()

        # Resource =open('./output/Debug.csv','w+',newline='')
        # writer=csv.writer(Resource)
        # writer.writerow(('title'))
        # Resource.close()

    # 'outputDate','vmId','status','ncId','vmType','cpu','memory','createTime','releaseTime'
    def writevm(self,data):
        vm =open('./output/vm.csv','a+',newline='')
        writer=csv.writer(vm)
        if(data!=None):
            writer.writerow(data)
            
        vm.close()

    # 'outputDate','ncId','status','totalCpu','tocalMemory','machineType','usedCpu','usedMemory','createTime'
    def writenc(self,data):
        nc =open('./output/nc.csv','a+',newline='')
        writer=csv.writer(nc)
        if(data!=None):
            writer.writerow(data)
        
        nc.close()

    # 'outputDate','ncId','status','totalCpu','tocalMemory','machineType','usedCpu','usedMemory','createTime'
    def writenewnc(self,data):
        newnc =open('./output/new_nc.csv','a+',newline='')
        writer=csv.writer(newnc)
        if(data!=None):
            writer.writerow(data)
        newnc.close()

    # 'outputDate','BuyServerCost','CPUCost','BuyCost','LoseCost','EarnMoney'
    def writeMoney(self,data):
        # Money =open('./output/Money.csv','a+',newline='')
        # writer=csv.writer(Money)
        # if(data!=None):
        #     writer.writerow(data)               
        # Money.close()
        return

    # 'outputDate','MachineType','TotalCPU','TotalMem','CPU','Mem','CPU %','Mem %'
    def writeResourece(self,data):
        # Resource =open('./output/Resource.csv','a+',newline='')
        # writer=csv.writer(Resource)
        # if(data!=None):
        #     writer.writerow(data)               
        # Resource.close()
        return

    def writeDebug(self,data):
        # Resource =open('./output/Debug.csv','a+',newline='')
        # writer=csv.writer(Resource)
        # if(data!=None):
        #     writer.writerow(data)               
        # Resource.close()
        return