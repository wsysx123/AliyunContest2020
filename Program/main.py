# coding=utf-8
from Config import Config
from GetVm import GetVm
from NCPool import NCPool
from Schedule import Schedule

if __name__ == '__main__':
    Conf = Config("./config.json")
    myS = Schedule(Conf.readFile())
    myS.run()