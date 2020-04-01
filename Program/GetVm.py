# coding=utf-8

import csv
import json
from datetime import datetime
from Config import Config
from Vm import Vm
import globalvar as gl

class GetVm:
    def __init__(self, Files):
        self.starttime = None
        self.Files = Files
        self.result = None
        self.readNewFile()
    
    def IsListNULL(self):
        if (gl.get_value("LastDate") == None) or len(self.result)>0 and len(self.Files) > 0:
            return False
        return True

    def readNewFile(self):
        if len(self.Files) > 0:
            filename = self.Files[0]["filename"]
            with open(filename, 'r') as csvFile:
                self.reader = csv.reader(csvFile)
                self.result = []
                for item in self.reader:
                # 忽略第一行
                    if self.reader.line_num == 1:
                        continue
                    if self.starttime == None:
                        self.starttime = datetime.strptime(item[2], "%Y-%m-%d").date()
                    if item[3] == '\\N':
                        self.result.append({"vmid":item[0],"vmtype":item[1],"createtime":(datetime.strptime(item[2], "%Y-%m-%d").date()),"releasetime":datetime.strptime("2099-12-31 00:00:00",'%Y-%m-%d %H:%M:%S').date(),"AType":"","BType":0})
                    else:
                        self.result.append({"vmid":item[0],"vmtype":item[1],"createtime":(datetime.strptime(item[2], "%Y-%m-%d").date()),"releasetime":(datetime.strptime(item[3], "%Y-%m-%d").date()),"AType":"","BType":0})
                        if gl.get_value('LastDate') == None:
                            gl.set_value('LastDate',datetime.strptime(item[3], "%Y-%m-%d").date())
                        elif gl.get_value('LastDate') < datetime.strptime(item[3], "%Y-%m-%d").date():
                            gl.set_value('LastDate',datetime.strptime(item[3], "%Y-%m-%d").date())
            self.Files.remove(self.Files[0])
            return True
        else:
            return False

    def get1vm(self,date):
        try:
            if len(self.result)>0:
                if self.result[0]["createtime"] == date:
                    ret = self.result.pop(0)
                else:
                    return None
            else:
                if self.readNewFile() == True:
                    return self.get1vm(date)
                else:
                    return None
        except:
            return None
        return ret

        
