# -*- coding:utf-8 -*-
import sys
import socket
import json
# python main.py 59.110.142.4 32245 31f565a3-33a1-49aa-a5b7-8c5e5f35ecfb
#从服务器接收一段字符串, 转化成字典的形式
def RecvJuderData(hSocket):
    nRet = -1
    Message = hSocket.recv(1024*1024*4)
    # 接收数据部分示例:b'00001980{"token":"1e49d75c-424c-4e50-9550-106b5b54db97"\
    # ,"notice":"step",
    len_json = int(Message[:8])
    # '00001980'表示服务器发送的完整数据的总长度 
    str_json = Message[8:].decode()
    # 实际接收到的数据的长度
    # 将接收到的数据与完整数据长度进行对比来判断
    # 数据接收是否完整，如果不完整则继续接收
    while len(str_json) != len_json :
        Message = hSocket.recv(1024*1024*4)
        str_json += Message.decode()
    nRet = 0
    Dict = json.loads(str_json)
    return nRet, Dict
# 接收一个字典,将其转换成json文件,并计算大小,发送至服务器
def SendJuderData(hSocket, dict_send):
    str_json = json.dumps(dict_send)
    len_json = str(len(str_json)).zfill(8)
    str_all = len_json + str_json
    #print(str_all)
    ret = hSocket.sendall(str_all.encode())
    if ret == None:
        ret = 0
    #print('sendall', ret)
    return ret

# 用户自定义函数, 返回字典FlyPlane, 需要包括 "UAV_info", "purchase_UAV" 两个key.

class task_uav(object):
    def __init__(self):
        self.charge = True
        self.upwithnogood = False
        self.downtogetgood = False
        self.upwithgood = False 
        self.downtoputgood = False
        self.attackenemy = False
        self.getgoodxy = False
        self.putgoodxy = False
        self.electricitycost = -1
        self.end_x = -1
        self.end_y = -1
        self.goodno = -1
        self.uavno = -1
    #===初始时要对无人机进行充电
    def setcharge(self,state):
        self.charge = state 
    def getcharge(self):
        return self.charge
    def setelectricitycost(self,num):
        self.electricitycost = num 
    def getelectricitycost(self):
        return self.electricitycost
    #===goodno为-1时请求上升
    def setuavno(self,no):
        self.uavno = no 
    def getuavno(self):
        return self.uavno
    def setupwithnogood(self,state):
        self.upwithnogood = state 
    #===派出飞机去攻击敌机
    #1,我方飞机应该处于空载求没有运输的物品目标
    #2,我方飞机的价值必须小于敌方飞机价值 + 货物价值
    #3,当敌方飞机正在下降去取货时,可赶至取货点上方进行拦截。
    #4,用价值量小的换取价值量较大的敌机

    def setattackenemy(self,state):
        self.attackenemy = state
    def getattackenemy(self):
        return self.attackenemy
    #===返回上升状态
    def getupwithnogood(self):
        return self.upwithnogood
    def setgetgoodxy(self,state):
        self.getgoodxy = state
    def getgetgoodxy(self):
        return self.getgoodxy
    def setputgoodxy(self,state):
        self.putgoodxy = state
    def getputgoodxy(self):
        return self.putgoodxy
    #===到达取货点请求下降
    def setdowntogetgood(self,state):
        self.downtogetgood = state
    #===返回下降状态
    def getdowntogetgood(self):
        return self.downtogetgood
    #===到达货物点后请求上升
    def setupwithgood(self,state):
        self.upwithgood = state 
    #===返回与物品上升状态
    def getupwithgood(self):
        return self.upwithgood 
    #===到达目的地上方请求下降
    def setdowntoputgood(self,state):
        self.downtoputgood = state 
    def getdowntoputgood(self):
        return self.downtoputgood
    def setend(self,x,y):
        self.end_x = x 
        self.end_y = y
    def getend(self):
        return self.end_x,self.end_y
    def setgoodno(self,no):
        self.goodno = no 
    def getgoodno(self):
        return self.goodno
class Algo():
    def __init__(self):
        self.tasklist = [0,0,0,0,0,0]
        self.goodnohasbeendetected = []
        self.enemygoodno = []
        self.chargeinfo = {}
    def MovetoAttack(self,i):
        dis_we_enemy = [(enemy["x"] - self.FlyPlane[i]["x"])**2 + (enemy["y"] - self.FlyPlane[i]["y"])**2 \
                        + (enemy["z"] - self.FlyPlane[i]["z"])**2 if self.FlyPlane[i]["load_weight"]<enemy["load_weight"]\
                        else float("inf") for enemy in self.uavenemy]
        # 如果敌军只有最后一架飞机则一个选择一个与其价值相当的无人机继续撞击任务
        if not dis_we_enemy or min(dis_we_enemy) == float("inf"):
            if self.FlyPlane[i]["z"] <= self.flyhlow:
                self.FlyPlane[i]["z"] += 1
            return
        min_index = dis_we_enemy.index(min(dis_we_enemy))
        if self.uavenemy[min_index]["no"] not in self.enemyhasbeenchoose:
            self.enemyhasbeenchoose.append(self.uavenemy[min_index]["no"])
        x_dis = self.uavenemy[min_index]["x"] - self.FlyPlane[i]["x"]
        y_dis = self.uavenemy[min_index]["y"] - self.FlyPlane[i]["y"]
        z_dis = self.uavenemy[min_index]["z"] - self.FlyPlane[i]["z"]
        flag_x = 0
        temp_flyx = self.FlyPlane[i]["x"]
        if (x_dis != 0 or y_dis !=0) and self.FlyPlane[i]["z"] <= self.flyhlow:
            self.FlyPlane[i]["z"] += 1
            return
        if x_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:                     
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) <= buildsize["x_end"] and \
            buildsize["y_start"] <= self.FlyPlane[i]["y"] <= buildsize["y_end"] and self.FlyPlane[i]["z"] < buildsize["z_end"] else True for \
            buildsize in self.buildings] 
            if False not in res and ([self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))),self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status):
                self.FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                flag_x = 1
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
            elif self.FlyPlane[i]["z"] + 1 <= self.flayhhight:
                self.FlyPlane[i]["z"] += 1
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                return
        if y_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]<= buildsize["x_end"] and \
                    buildsize["y_start"] <= self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) <= buildsize["y_end"] \
                    and self.FlyPlane[i]["z"] <  buildsize["z_end"] else True for buildsize in self.buildings]
            if False not in res and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))),self.FlyPlane[i]["z"]] not in self.xyz_status):
                self.FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
            else:
                if flag_x or x_dis == 0:
                    self.FlyPlane[i]["z"] += 1
                    self.FlyPlane[i]["x"] = temp_flyx
                    self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                return
        if x_dis == 0 and y_dis == 0 and z_dis != 0:
            self.FlyPlane[i]["z"] += int(z_dis/(abs(z_dis)))
    def movexy(self,i,x,y):
        x_dis = x - self.FlyPlane[i]["x"]
        y_dis = y - self.FlyPlane[i]["y"]
        temp_flyx = self.FlyPlane[i]["x"]
        flag_x = 0
        if self.FlyPlane[i]["z"] <= self.flyhlow:
            self.FlyPlane[i]["z"] += 1
            return
        if x_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:                     
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) <= buildsize["x_end"] and \
            buildsize["y_start"] <= self.FlyPlane[i]["y"] <= buildsize["y_end"] and self.FlyPlane[i]["z"] < buildsize["z_end"] else True for \
            buildsize in self.buildings] 
            if False not in res and ([self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))),self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status):
                self.FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                flag_x = 1
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
            elif self.FlyPlane[i]["z"] + 1 <= self.flayhhight:
                self.FlyPlane[i]["z"] += 1
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                return
        if y_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]<= buildsize["x_end"] and \
                    buildsize["y_start"] <= self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) <= buildsize["y_end"] \
                    and self.FlyPlane[i]["z"] <  buildsize["z_end"] else True for buildsize in self.buildings]
            if False not in res and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))),self.FlyPlane[i]["z"]] not in self.xyz_status):
                self.FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
            else:
                if flag_x or x_dis == 0:
                    self.FlyPlane[i]["z"] += 1
                    self.FlyPlane[i]["x"] = temp_flyx
                    self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                return
    def AlgorithmCalculationFun(self,a, b, c):
        #parse matchstatus
        # good_no 出现 -1 的情况：
        # 1.在停机坪或故意不运送货物
        # 2.运送途中出现撞机，且status = 1.
        # 3.将货物运送到目的地后，在寻找下一个货物地点中
        # 关于无人机最大电容量和充电速度的信息
        # example:{"F1":[9000,1000]} .index 0:总容量;index 1:每秒充电量
        for uavcharge in  a["UAV_price"]:
            self.chargeinfo[uavcharge["type"]] = [uavcharge["capacity"],uavcharge["charge"]]
        self.flyhlow = a["h_low"]
        self.flayhhight = a["h_high"]
        map_x = a["map"]["x"]
        map_y = a["map"]["y"]
        parking_x = a["parking"]["x"]
        parking_y = a["parking"]["y"]
        goodshasbeenchoose = []
        self.enemyhasbeenchoose = []
        #===============================一些限制条件=======================
        fogs = [{"x_start":foginfo["x"],"x_end":foginfo["x"]+foginfo["l"]-1,\
                "y_start":foginfo["y"],"y_end":foginfo["y"]+foginfo["w"]-1,
                "z_start":foginfo["b"],"z_end":foginfo["t"]}\
                for foginfo in a["fog"]]
        #===============================利用雾区==========================
        self.buildings = [{"x_start":buildinfo["x"],"x_end":buildinfo["x"]+buildinfo["l"],\
                    "y_start":buildinfo["y"],"y_end":buildinfo["y"]+buildinfo["w"],
                    "z_start":0,"z_end":buildinfo["h"]}\
                    for buildinfo in a["building"]]
        if b["time"] == 0:
            return c["astUav"]
        else:
            self.uavenemy = b["UAV_enemy"]
            self.FlyPlane = b["UAV_we"]
            #对无人机按照运输能力进行排序
            #self.FlyPlane = sorted(b["UAV_we"] ,key = lambda uav:uav["load_weight"],reverse = True)
            # 将购买成功的无人机添加到任务列表中，初始化为0
            len_cha = len(self.FlyPlane) - len(self.tasklist)
            if len_cha > 0:
               self.tasklist.extend([0 for i in range(len_cha)])
            goods = b["goods"]
            # 垂直上升,一架一架的离开，直达所有飞机到达最低高度
            z_status = [sin_z["z"] if(sin_z["x"]==parking_x and sin_z["y"]==parking_y and sin_z["z"]<=self.flyhlow) else -1 for sin_z in self.FlyPlane ]
            self.xyz_status = [[uavxy["x"],uavxy["y"],uavxy["z"]] for uavxy in self.FlyPlane]
            for enemy in self.uavenemy:
                if enemy["goods_no"] != -1 and enemy["goods_no"] not in self.enemygoodno:
                    self.enemygoodno.append(enemy["goods_no"])
            for i,_ in enumerate(self.FlyPlane):
                lastgoods = [good for good in goods if good["no"] not in goodshasbeenchoose \
                             and good["no"] not in self.goodnohasbeendetected and good["status"] == 0 and good["no"] not in self.enemygoodno]
                lastenemy = [enemy for enemy in self.uavenemy if enemy["no"] not in self.enemyhasbeenchoose and enemy["status"] != 1] 
                # 如何处理毁掉的uav,待修改
                if self.FlyPlane[i]["status"] == 1:
                    self.FlyPlane[i] = 0
                    continue
                # 根据self.FlyPlane的编号找到相对应的uavtask
                uavtask = [uav for uav in self.tasklist if uav and uav.getuavno() == self.FlyPlane[i]["no"]]
                if uavtask:
                    uavtask = uavtask[0]
                else:
                    uavtask = task_uav()
                    uavtask.setuavno(self.FlyPlane[i]["no"])
                # 如果无人机的状态为需要充电并且无人机当前位置在停机坪则进行充电
                if uavtask.getcharge():
                    x_dis = parking_x - self.FlyPlane[i]["x"] 
                    y_dis = parking_y - self.FlyPlane[i]["y"]
                    if x_dis == 0 and y_dis == 0:
                        if self.FlyPlane[i]["z"] != 0:
                            self.FlyPlane[i]["z"] -= 1
                        if self.FlyPlane[i]["z"] == 0:
                            type = self.FlyPlane[i]["type"]
                            chargespeed = self.chargeinfo[type][1]
                            capacity = self.chargeinfo[type][0]
                            # 充电至最大容量还是充到够货物?
                            # 若中途结束充电状态:self.FlyPlane[i]["status"] = 0
                            if self.FlyPlane[i]["remain_electricity"] + chargespeed < capacity:
                                self.FlyPlane[i]["remain_electricity"] += chargespeed 
                            elif self.FlyPlane[i]["remain_electricity"] + chargespeed >= capacity:
                                self.FlyPlane[i]["remain_electricity"] = capacity
                                uavtask.setcharge(False)
                                uavtask.setupwithnogood(True)   
                    elif x_dis != 0 or y_dis != 0:
                        self.movexy(i,parking_x,parking_y)           
                # 充电完毕飞到最低高度
                elif uavtask.getupwithnogood() and ((self.FlyPlane[i]["z"]+1) not in z_status or (self.FlyPlane[i]["x"] != parking_x or self.FlyPlane[i]["y"] != parking_y)) :
                    self.FlyPlane[i]["z"] += 1
                    z_status[i] += 1
                    if self.FlyPlane[i]["z"] > self.flyhlow:
                        uavtask.setupwithnogood(False)
                        uavtask.setgetgoodxy(True)
                elif uavtask.getgetgoodxy():
                    #dis = [(good["start_x"] - self.FlyPlane[i]["x"])**2 + (good["start_y"] - self.FlyPlane[i]["y"])**2 + (self.FlyPlane[i]["z"])**2\
                           #if good["weight"]<=self.FlyPlane[i]["load_weight"] else float("inf") for good in lastgoods]
                    dis = [(good["start_x"] - self.FlyPlane[i]["x"])**2 + (good["end_x"] - good["start_x"])**2 +\
                           (good["start_y"] - self.FlyPlane[i]["y"])**2 + (good["end_y"] - good["start_y"])**2 +\
                           (self.FlyPlane[i]["z"])**2 - good["value"]\
                           if good["weight"]<=self.FlyPlane[i]["load_weight"] else float("inf") for good in lastgoods]
                    #dis = [good["weight"] if good["weight"]<=self.FlyPlane[i]["load_weight"] else -float("inf") for good in lastgoods]
                    #如果没有找到物品目标保持不动即可
                    #if not dis or max(dis) == -float("inf"):
                    if not dis or min(dis) == float("inf"):
                        if self.FlyPlane[i]["x"] == parking_x and self.FlyPlane[i]["y"] == parking_y:
                            if (0 <= self.FlyPlane[i]["x"] + 1 < map_x) and ([self.FlyPlane[i]["x"] + 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
                            and (self.FlyPlane[i]["z"] > self.flyhlow):
                                self.FlyPlane[i]["x"] += 1
                                z_status[i] = -1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            elif (0 <= self.FlyPlane[i]["x"] - 1 < map_x) and ([self.FlyPlane[i]["x"] - 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
                            and (self.FlyPlane[i]["z"] > self.flyhlow):
                                self.FlyPlane[i]["x"] -= 1
                                z_status[i] = -1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            elif (0 <= self.FlyPlane[i]["y"] + 1 < map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
                            and (self.FlyPlane[i]["z"] > self.flyhlow):
                                self.FlyPlane[i]["y"] += 1
                                z_status[i] = -1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            elif (0 <= self.FlyPlane[i]["y"] - 1 < map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]-1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
                            and (self.FlyPlane[i]["z"] > self.flyhlow):
                                self.FlyPlane[i]["y"] -= 1
                                z_status[i] = -1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            elif self.FlyPlane[i]["z"] + 1 <= self.flayhhight and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]+1] not in self.xyz_status):
                                self.FlyPlane[i]["z"] += 1
                                z_status[i] = -1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            elif self.flyhlow < self.FlyPlane[i]["z"] - 1 and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]-1] not in self.xyz_status):
                                self.FlyPlane[i]["z"] -= 1
                                z_status[i] = self.FlyPlane[i]["z"] - 1
                                self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
                            continue
                        else:
                            self.MovetoAttack(i)
                            continue
                    #min_dis_index = dis.index(max(dis))
                    min_dis_index = dis.index(min(dis))
                    if lastgoods[min_dis_index]["no"] not in goodshasbeenchoose:
                       goodshasbeenchoose.append(lastgoods[min_dis_index]["no"])
                    goodstartx = lastgoods[min_dis_index]["start_x"]
                    goodstarty = lastgoods[min_dis_index]["start_y"]
                    # 粗略计算获取目的地距离当前位置需要移动的距离
                    goodendx = lastgoods[min_dis_index]["end_x"] 
                    goodendy = lastgoods[min_dis_index]["end_y"]
                    from math import sqrt
                    distance = 2*self.FlyPlane[i]["z"] + 1 + abs(goodendx - goodstartx) + abs(goodendy - goodstarty) 
                    if self.FlyPlane[i]["remain_electricity"] - uavtask.getelectricitycost() < distance * uavtask.getelectricitycost():
                        uavtask.setcharge(True)
                        uavtask.setdowntogetgood(False)
                        continue
                    #========================================
                    x_dis = goodstartx - self.FlyPlane[i]["x"]
                    y_dis = goodstarty - self.FlyPlane[i]["y"]
                    if x_dis == 0 and y_dis == 0:
                        if lastgoods[min_dis_index]["no"] not in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.append(lastgoods[min_dis_index]["no"])
                        if  lastgoods[min_dis_index]["remain_time"] > self.FlyPlane[i]["z"]:
                            uavtask.setend(lastgoods[min_dis_index]["end_x"],lastgoods[min_dis_index]["end_y"])
                            uavtask.setgoodno(lastgoods[min_dis_index]["no"])
                            uavtask.setelectricitycost(lastgoods[min_dis_index]["weight"])
                            uavtask.setdowntogetgood(True)
                            uavtask.setgetgoodxy(False)
                            self.FlyPlane[i]["z"] -= 1
                    else:
                        self.movexy(i,goodstartx,goodstarty)
                elif uavtask.getdowntogetgood():
                    if  self.FlyPlane[i]["z"] == 0:
                        if uavtask.getgoodno() in [good["no"] for good in goods]:
                            self.FlyPlane[i]["goods_no"] = uavtask.getgoodno()
                            self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                            uavtask.setdowntogetgood(False)
                            uavtask.setupwithgood(True)
                        else:
                            uavtask.setdowntogetgood(False)
                            uavtask.setupwithnogood(True)
                    else:
                        self.FlyPlane[i]["z"] -= 1
                elif uavtask.getupwithgood():
                    self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                    self.FlyPlane[i]["z"] += 1
                    if self.FlyPlane[i]["z"] > self.flyhlow:
                        uavtask.setupwithgood(False)
                        uavtask.setputgoodxy(True)
                elif uavtask.getputgoodxy():
                    self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                    goodendx = uavtask.getend()[0] 
                    goodendy = uavtask.getend()[1] 
                    x_dis = goodendx - self.FlyPlane[i]["x"]
                    y_dis = goodendy - self.FlyPlane[i]["y"]
                    if x_dis == 0 and y_dis == 0:
                        uavtask.setputgoodxy(False)
                        uavtask.setdowntoputgood(True)
                    else:
                        self.movexy(i,goodendx,goodendy)
                elif uavtask.getdowntoputgood():
                    self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                    if  self.FlyPlane[i]["z"] == 0:
                        if uavtask.getgoodno() in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.remove(uavtask.getgoodno())
                        uavtask.setdowntoputgood(False)
                        uavtask.setupwithnogood(True)
                    else:
                        self.FlyPlane[i]["z"] -= 1
                self.tasklist[i] = uavtask 
        #print(self.FlyPlane[5]) 
        aviavlePlane = [uav for uav in self.FlyPlane if uav != 0]   
        return aviavlePlane


def main(szIp, nPort, szToken):
    print("server ip %s, prot %d, token %s\n", szIp, nPort, szToken)

    #Need Test // 开始连接服务器
    hSocket = socket.socket()

    hSocket.connect((szIp, nPort))
    #接受数据  连接成功后，Judger会返回一条消息：
    #=======================yzw============
    #收到的第一条消息
    
    nRet, _ = RecvJuderData(hSocket)
    if (nRet != 0):
        return nRet
    

    # // 生成表明身份的json
    token = {}
    token['token'] = szToken        
    token['action'] = "sendtoken"   

    #==================mxq====================
    #向服务器发送验证信息========================
    #// 选手向裁判服务器表明身份(Player -> Judger)
    nRet = SendJuderData(hSocket, token)
    if nRet != 0:
        return nRet

    #=================mxq==========================
    #收到的第二条消息
    
    #//身份验证结果(Judger -> Player), 返回字典Message
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    if Message["result"] != 0:
        print("token check error\n")
        return -1

    # // 选手向裁判服务器表明自己已准备就绪(Player -> Judger)
    #================mxq================================
    #发送第二条消息。表明准备就绪===========================
    stReady = {}
    stReady['token'] = szToken
    stReady['action'] = "ready"

    nRet = SendJuderData(hSocket, stReady)
    if nRet != 0:
        return nRet

    # //对战开始通知(Judger -> Player)
    #===================mxq==============
    #收到的第三条消息
    
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    #初始化地图信息
    pstMapInfo = Message["map"]  
    #初始化比赛状态信息
    pstMatchStatus = {}
    pstMatchStatus["time"] = 0

    #初始化飞机状态信息
    pstFlayPlane = {}
    pstFlayPlane["nUavNum"] = len(pstMapInfo["init_UAV"])
    pstFlayPlane["astUav"] = []

    #每一步的飞行计划
    FlyPlane_send = {}
    FlyPlane_send["token"] = szToken
    FlyPlane_send["action"] = "flyPlane"

    for i in range(pstFlayPlane["nUavNum"]):
        pstFlayPlane["astUav"].append(pstMapInfo["init_UAV"][i])

    # // 根据服务器指令，不停的接受发送数据
    uavprice = pstMapInfo["UAV_price"]
    uavpridict = {}
    for singleuav in uavprice:
        uavpridict[singleuav["type"]] = singleuav["value"]
    F1pri,F2pri,F3pri,F4pri,F5pri = uavpridict["F1"],uavpridict["F2"],uavpridict["F3"],uavpridict["F4"],uavpridict["F5"]
    Algo_main = Algo()
    while True:

        # // 进行当前时刻的数据计算, 填充飞行计划，注意：1时刻不能进行移动，
        # //即第一次进入该循环时,此时pstMatchStatus只有 "time" 信息
        # pstMapInfo 在一场比赛中是固定的，不会变
        # pstMatchStatus 服务器根据用户发送的数据经过处理后返回的信息
        # pstFlayPlane 是用户根据服务器的数据，经过自己的算法计算后得到的作战计划，需要发送给服务器
        FlyPlane = Algo_main.AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane)
        FlyPlane_send['UAV_info'] = FlyPlane
        print("current time:",pstMatchStatus["time"])
        # 购买uav info
        #{ "type": "F1", "load_weight": 100, "value": 600 },uavpricelist[0]
        #{ "type": "F2","load_weight": 50, "value": 350 },uavpricelist[1]
        #{ "type": "F3","load_weight": 20, "value": 130 },uavpricelist[2]
        #{ "type": "F4","load_weight": 30, "value": 190 },uavpricelist[3]
        #{ "type": "F5","load_weight": 360, "value": 1000 },uavpricelist[4]
        avatypes = [uav["type"] for uav in FlyPlane]
        purchaselist = []
        FlyPlane_send["purchase_UAV"] = []
        if pstMatchStatus["time"] == 0:
            enemyaviable = []
            wevalue = 0
        else:
            wevalue = pstMatchStatus["we_value"]
            enemyaviable = [enemy for enemy in  pstMatchStatus["UAV_enemy"] if enemy["status"] != 0]
        if (len(FlyPlane) <=2 and wevalue >= F3pri):
            purchaselist.append({"purchase":"F3"})
        elif (wevalue >= F1pri and avatypes.count("F1") <=1):
            purchaselist.append({"purchase":"F1"})
        elif (wevalue >= F5pri and avatypes.count("F5") <= 1):
            purchaselist.append({"purchase":"F5"})
        elif (len(enemyaviable) <= 2 and wevalue >= F3pri and avatypes.count("F3") <=1):
            purchaselist.append({"purchase":"F3"})
        elif (wevalue >= F3pri and avatypes.count("F3") <= len(enemyaviable)):
            purchaselist.append({"purchase":"F3"})

        if purchaselist: 
           FlyPlane_send["purchase_UAV"] = purchaselist
        #==================mxq=====================
        #发送作战路线
        # //发送飞行计划
        nRet = SendJuderData(hSocket, FlyPlane_send)
        if nRet != 0:
            return nRet
        
        # // 接受当前比赛状态
        #=====================mxq===================
        #接收当前状态
        
        nRet, pstMatchStatus = RecvJuderData(hSocket)
        if nRet != 0:
            return nRet
        
        if pstMatchStatus["match_status"] == 1:
            print("game over, we value %d, enemy value %d\n", pstMatchStatus["we_value"], pstMatchStatus["enemy_value"])
            print(FlyPlane)
            hSocket.close()
            return 0

if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Server Host: " + sys.argv[1])
        print("Server Port: " + sys.argv[2])
        print("Auth Token: " + sys.argv[3])
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        print("need 3 arguments")