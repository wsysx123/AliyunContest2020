# coding=utf-8
#在别的文件使用方法:
# conf = Config("./config.json")
# print(conf.readNC("NT-1-2"))
# print(conf.XN)
# print(conf.readVM("ecs.c1.large"))

import json

class Config:

    def __init__(self, configfile):
        self.filename = configfile
        with open(self.filename, 'r') as f:
            self.conf = json.loads(f.read())
        self.XN = self.conf["ContestConfig"]["XN"]
        self.XP = self.conf["ContestConfig"]["XP"]
        self.XD = self.conf["ContestConfig"]["XD"]
        self.Products = {}
        self.Product2NC()
        f.close()

    def Product2NC(self):
        NCList = self.conf["ContestConfig"]["NC"]
        for NC in NCList:
            Products = NCList[NC]["supportProductType"]
            for Product in Products:
                if Product in self.Products:
                    self.Products[Product].append(NC)
                else:
                    self.Products[Product] = []
                    self.Products[Product].append(NC)

    def readNC(self,NCname):
        return self.conf["ContestConfig"]["NC"][NCname]

    def readVM(self,VMname):
        return self.conf["ContestConfig"]["VM"][VMname]

    def readFile(self):
        return self.conf["ContestConfig"]["FileList"]