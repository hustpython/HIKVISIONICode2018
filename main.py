
# -*- coding:utf-8 -*-
import sys
import socket
import json
# python main.py 47.95.243.246 32178 bda4e23e-5a4f-41e7-9f25-f7bc10f63a4d
# 0,F1,100
# 1,F3,20
# 2,F3,20
# 3,F4,30
# 4,F4,30
# 5,F2,50
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
    ret = hSocket.sendall(str_all.encode())
    if ret == None:
        ret = 0
    return ret

# 用户自定义函数, 返回字典FlyPlane, 需要包括 "UAV_info", "purchase_UAV" 两个key.

class task_uav(object):
    def __init__(self):
        self.charge = True
        self.occupy = False
        self.directkill = False
        self.upwithnogood = False
        self.downtogetgood = False
        self.upwithgood = False 
        self.downtoputgood = False
        self.getgoodxy = False
        self.putgoodxy = False
        self.preenemyattackno = -1
        self.electricitycost = -1
        self.end_x = -1
        self.end_y = -1
        self.goodno = -1
        self.uavno = -1
    #===占据别停机坪
    def setpreenemyattackno(self,no):
        self.preenemyattackno = no 
    def getpreenemyattackno(self):
        return self.preenemyattackno
    def setoccupy(self,state):
        self.occupy = state
    def getoccupy(self):
        return self.occupy
    def setdirectkill(self,state):
        self.directkill = state
    def getdirectkill(self):
        return self.directkill
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
        self.tasklist = [task_uav() for i in range(6)]
        self.enemyparking = [-1,-1,-1]
        self.goodnohasbeendetected = []
        self.enemygoodno = []
        self.chargeinfo = {}
        self.uavtypeinfo = []
        self.z_status = []
        self.killdutynum = 0
        self.occupydutynum = 0
        self.parkingenemynum = 0
    # def MovetoAttack(self,i):
    #     dis_we_enemy = [(enemy["x"] - self.FlyPlane[i]["x"])**2 + (enemy["y"] - self.FlyPlane[i]["y"])**2 \
    #                     + (enemy["z"] - self.FlyPlane[i]["z"])**2 if (self.FlyPlane[i]["load_weight"]<=enemy["load_weight"] or enemy["goods_no"]!=-1)\
    #                     and enemy["no"] not in self.enemyhasbeenchoose \
    #                     else float("inf") for enemy in self.uavenemy]
    #     # 如果敌军只有最后一架飞机则一个选择一个与其价值相当的无人机继续撞击任务
    #     if not dis_we_enemy or min(dis_we_enemy) == float("inf"):
    #         if self.FlyPlane[i]["z"] <= self.flyhlow:
    #             self.FlyPlane[i]["z"] += 1
    #         else:
    #             self.parkingrandmove(i)
    #         return
    #     min_index = dis_we_enemy.index(min(dis_we_enemy))
    #     if self.uavenemy[min_index]["no"] not in self.enemyhasbeenchoose:
    #         self.enemyhasbeenchoose.append(self.uavenemy[min_index]["no"])
    #     enemyx = self.uavenemy[min_index]["x"]
    #     enemyy = self.uavenemy[min_index]["y"]
    #     x_dis = enemyx - self.FlyPlane[i]["x"]
    #     y_dis = enemyy - self.FlyPlane[i]["y"]
    #     z_dis = self.uavenemy[min_index]["z"] - self.FlyPlane[i]["z"]
    #     if x_dis == 0 and y_dis == 0 and z_dis != 0:
    #         self.FlyPlane[i]["z"] += int(z_dis/(abs(z_dis)))
    #     else:
    #         self.movexy(i,enemyx,enemyy)
    def MovetoAttack(self,i):
        notinfogenemy = [uav for uav in self.uavenemy if uav["x"] != -1]
        dis_we_enemy = [abs(enemy["x"] - self.FlyPlane[i]["x"])+ abs(enemy["y"] - self.FlyPlane[i]["y"]) \
                        + 4*(enemy["z"]-self.flyhlow) if (self.FlyPlane[i]["load_weight"]<=enemy["load_weight"] or enemy["goods_no"]!=-1)\
                        and enemy["no"] not in self.enemyhasbeenchoose and enemy["no"] not in self.uavonme\
                        else float("inf") for enemy in notinfogenemy]
        # by mxq 2018 06 11
        enemynolist = [uav["no"] for uav in notinfogenemy]
        enemyalivenolist = [uav["no"] for uav in self.uavenemy]
        if self.tasklist[i].getpreenemyattackno() != -1 and self.tasklist[i].getpreenemyattackno() not in enemynolist and self.tasklist[i].getpreenemyattackno() in enemyalivenolist and self.FlyPlane[i]["z"] <= self.flyhlow:
            if self.FlyPlane[i]["z"] - 1 >= 0:
               self.FlyPlane[i]["z"] -= 1
            if self.FlyPlane[i]["z"] == 0:
               self.tasklist[i].setpreenemyattackno(-1)
            return
        # ==================
        if not dis_we_enemy or min(dis_we_enemy) == float("inf"):
            if self.FlyPlane[i]["z"] <= self.flyhlow:
                self.FlyPlane[i]["z"] += 1
            else:
                self.parkingrandmove(i)
            return
        min_index = dis_we_enemy.index(min(dis_we_enemy))
        if notinfogenemy[min_index]["no"] not in self.enemyhasbeenchoose:
            self.enemyhasbeenchoose.append(notinfogenemy[min_index]["no"])
        # by mxq 2018 06 11
        self.tasklist[i].setpreenemyattackno(notinfogenemy[min_index]["no"])
        # =================
        enemyx = notinfogenemy[min_index]["x"]
        enemyy = notinfogenemy[min_index]["y"]
        x_dis = enemyx - self.FlyPlane[i]["x"]
        y_dis = enemyy - self.FlyPlane[i]["y"]
        z_dis = notinfogenemy[min_index]["z"] - self.FlyPlane[i]["z"]
        if (x_dis != 0 or y_dis != 0) and self.FlyPlane[i]["z"]+1<=self.flyhlow:
            self.tasklist[i].setpreenemyattackno(-1)
            self.FlyPlane[i]["z"] += 1
            return 
        if x_dis == 0 and y_dis == 0 and z_dis != 0:
            self.FlyPlane[i]["z"] += int(z_dis/(abs(z_dis)))
        else:
            self.movexy(i,enemyx,enemyy)
    def movexy(self,i,x,y):
        x_dis = x - self.FlyPlane[i]["x"]
        y_dis = y - self.FlyPlane[i]["y"]
        temp_flyx = self.FlyPlane[i]["x"]
        flag_x = 0
        flag_y = 0
        if self.FlyPlane[i]["z"] <= self.flyhlow:
            self.FlyPlane[i]["z"] += 1
            return
        if x_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:                     
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) <= buildsize["x_end"] and \
            buildsize["y_start"] <= self.FlyPlane[i]["y"] <= buildsize["y_end"] and self.FlyPlane[i]["z"] < buildsize["z_end"] else True for \
            buildsize in self.buildings] 
            if False not in res and ([self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))),self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status) and (0 <= self.FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) < self.map_x):
                self.FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                flag_x = 1
            elif y_dis == 0 and self.FlyPlane[i]["z"] + 1 <= self.flayhhight and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]+1] not in self.xyz_status):
                 self.FlyPlane[i]["z"] += 1
                 return
        if y_dis != 0 and self.FlyPlane[i]["z"] > self.flyhlow:
            res = [False if buildsize["x_start"] <= self.FlyPlane[i]["x"]<= buildsize["x_end"] and \
                    buildsize["y_start"] <= self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) <= buildsize["y_end"] \
                    and self.FlyPlane[i]["z"] <  buildsize["z_end"] else True for buildsize in self.buildings]
            if False not in res and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))),self.FlyPlane[i]["z"]] not in self.xyz_status) and (0 <= self.FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) < self.map_y):
                self.FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                falg = 1
            else:
                if flag_x or flag_y or x_dis == 0:
                    if self.FlyPlane[i]["z"] + 1 <= self.flayhhight and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]+1] not in self.xyz_status):
                       self.FlyPlane[i]["z"] += 1
                    self.FlyPlane[i]["x"] = temp_flyx
                return
    def recorduavxyz(self,i):
        self.xyz_status[i] = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]]
    def recorduavz(self,i):
        self.z_status[i] = self.FlyPlane[i]["z"]
    def getgoodinfofromno(self,no):
        return [good for good in totalgoods if good["no"] == no]
    def freeuavavoidgood(self,i):
        currentpositionxy = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]]
        if currentpositionxy not in self.goodposition:
            return 
        else:
            if (0 <= self.FlyPlane[i]["x"] + 1 < self.map_x) and ([self.FlyPlane[i]["x"] + 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
            and (self.FlyPlane[i]["z"] > self.flyhlow):
                self.FlyPlane[i]["x"] += 1                             
            elif (0 <= self.FlyPlane[i]["x"] - 1 < self.map_x) and ([self.FlyPlane[i]["x"] - 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
            and (self.FlyPlane[i]["z"] > self.flyhlow):
                self.FlyPlane[i]["x"] -= 1
            elif (0 <= self.FlyPlane[i]["y"] + 1 < self.map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
            and (self.FlyPlane[i]["z"] > self.flyhlow):
                self.FlyPlane[i]["y"] += 1
            elif (0 <= self.FlyPlane[i]["y"] - 1 < self.map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]-1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
            and (self.FlyPlane[i]["z"] > self.flyhlow):
                self.FlyPlane[i]["y"] -= 1
    def parkingrandmove(self,i):
        if self.FlyPlane[i]["x"] != self.parking_x or self.FlyPlane[i]["y"] != self.parking_y:
            return
        if (0 <= self.FlyPlane[i]["x"] + 1 < self.map_x) and ([self.FlyPlane[i]["x"] + 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
        and ([self.FlyPlane[i]["x"] + 1,self.FlyPlane[i]["y"]] not in self.goodposition) and (self.FlyPlane[i]["z"] > self.flyhlow):
            self.FlyPlane[i]["x"] += 1
            self.z_status[i] = -1                              
        elif (0 <= self.FlyPlane[i]["x"] - 1 < self.map_x) and ([self.FlyPlane[i]["x"] - 1,self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]] not in self.xyz_status)\
        and ([self.FlyPlane[i]["x"] - 1,self.FlyPlane[i]["y"]] not in self.goodposition) and (self.FlyPlane[i]["z"] > self.flyhlow):
            self.FlyPlane[i]["x"] -= 1
            self.z_status[i] = -1
        elif (0 <= self.FlyPlane[i]["y"] + 1 < self.map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
        and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]+1] not in self.goodposition) and (self.FlyPlane[i]["z"] > self.flyhlow):
            self.FlyPlane[i]["y"] += 1
            self.z_status[i] = -1
        elif (0 <= self.FlyPlane[i]["y"] - 1 < self.map_y) and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]-1,self.FlyPlane[i]["z"]] not in self.xyz_status)\
        and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"]-1] not in self.goodposition) and (self.FlyPlane[i]["z"] > self.flyhlow):
            self.FlyPlane[i]["y"] -= 1
            self.z_status[i] = -1
        elif self.FlyPlane[i]["z"] + 1 <= self.flayhhight and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]+1] not in self.xyz_status):
            self.FlyPlane[i]["z"] += 1
            self.recorduavz(i)
        elif self.flyhlow < self.FlyPlane[i]["z"] - 1 and ([self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]-1] not in self.xyz_status):
            self.FlyPlane[i]["z"] -= 1
            self.recorduavz(i)
    # =========================== by mxq =====================
    def makepairforgoodanduav(self):
        pairsuccesslist = [0 if uavtask.getgetgoodxy() else -1 for uavtask in self.tasklist]
        findlist = [-1 for i in range(len(self.FlyPlane))]
        makepairsign = False
        from copy import deepcopy
        self.tempgoodlist = deepcopy(self.tempgoodlast)
        self.tempuavlist = deepcopy(self.FlyPlane)
        self.tempuavlist = [-1 if pairsuccesslist[i] == -1 else uav for (i,uav) in enumerate(self.tempuavlist)]
        while not makepairsign:
            goodres = list(map(self.goodchooseuav,self.tempgoodlist))
            uavres = list(map(self.uavchoosegood,self.tempuavlist))
            # 对于无人机选择的为 -1 的无人机,则无法分配物品,因为没有满足其运送重量的无人机
            # 找出那些物品选择无人机和无人机选择的物品相同的无人机
            pairsuccesslist = [uav if  uav == -1 or i == goodres[uav] else -2 for (i,uav) in enumerate(uavres)]
            findlist = [i if  i !=-2 and i!= -1 else findlist[_] for (_,i) in enumerate(pairsuccesslist)]
            # [1,3,4,20,-1,0]
            self.tempuavlist = [-1 if pairsuccesslist[i] != -2 else uav for (i,uav) in enumerate(self.tempuavlist)]
            # 对于无人机选择的物品与物品选择的无人机不对应的情况,则应该删除这个无人机选择的物品,让无人机重新选择
            resgood = [good if good == -1 or i == uavres[good] else -2 for (i,good) in enumerate(goodres)]
            self.tempgoodlist = [-1 if resgood[i] != -2 else good for (i,good) in enumerate(self.tempgoodlist)]
            if len(self.tempuavlist) == self.tempuavlist.count(-1) or len(self.tempgoodlist)==self.tempuavlist.count(-1):
                makepairsign = True
        return findlist
    def goodchooseuav(self,good):
        dis=[good["value"]/(3*(abs(good["start_x"] - FlyPlane["x"])+abs(good["start_y"] - FlyPlane["y"])+\
            abs(good["end_x"] - good["start_x"])+abs(good["end_y"] - good["start_y"]))+FlyPlane["load_weight"])\
            if FlyPlane != -1 and good != -1 and FlyPlane["status"] !=1 \
            and good["weight"]<=FlyPlane["load_weight"] and good["left_time"]>max([abs(good["start_x"] - FlyPlane["x"]),abs(good["start_y"] - FlyPlane["y"])])+FlyPlane["z"]\
            and (FlyPlane["remain_electricity"] - good["weight"] >= good["weight"] * (2*FlyPlane["z"] + abs(good["end_x"] - good["start_x"]) + abs(good["end_y"] - good["start_y"]))) \
            else -1 for FlyPlane in self.tempuavlist]
        if not dis or max(dis) == -1:
            return -1
        return dis.index(max(dis))
    def uavchoosegood(self,uav):
        dis=[good["value"]/(abs(good["start_x"] - uav["x"])+abs(good["start_y"] - uav["y"])+\
            abs(good["end_x"] - good["start_x"])+abs(good["end_y"] - good["start_y"])+uav["load_weight"])\
            if good != -1 and uav != -1 and uav["status"] != 1\
            and good["weight"]<=uav["load_weight"] and good["left_time"]>max([abs(good["start_x"] - uav["x"]),abs(good["start_y"] - uav["y"])])+uav["z"]\
            and (uav["remain_electricity"] - good["weight"] >= good["weight"] * (2*uav["z"] + abs(good["end_x"] - good["start_x"]) + abs(good["end_y"] - good["start_y"]))) \
            else -1 for good in self.tempgoodlist]
        if not dis or max(dis) == -1:
            return -1
        return dis.index(max(dis))

    # =========================== by mxq =====================
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
        self.map_x = a["map"]["x"]
        self.map_y = a["map"]["y"]
        self.parking_x = a["parking"]["x"]
        self.parking_y = a["parking"]["y"]
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
            self.uavtypeinfo = a["UAV_price"]
            return c["astUav"]
        else:
            if b["time"] == 1:
                self.enemyparking = [b["UAV_enemy"][0]["x"],b["UAV_enemy"][0]["y"],0]   
            self.uavenemy = [uavenemy for uavenemy in b["UAV_enemy"] if [uavenemy["x"],uavenemy["y"],uavenemy["z"]] != self.enemyparking and uavenemy["status"]!=1]
            self.parkingenemynum = len([enemyuav for enemyuav in self.uavenemy if (enemyuav["x"] == self.parking_x and enemyuav["y"]==self.parking_y)])
            self.FlyPlane = b["UAV_we"]
            #======================
            enemylast = [enemy for enemy in b["UAV_enemy"] if enemy["status"] != 1 and enemy["goods_no"]!=-1]
            welast = [we for we in self.FlyPlane if we["status"] != 1]
            self.uavonme = []
            for me in welast:
               self.uavonme.extend([uav["no"] for uav in b["UAV_enemy"] if (uav["x"] == me["x"] and uav["y"] == me["y"] and uav["z"]>uav["z"] and uav["z"] <= self.flyhlow)])
            #======================
            # 对无人机按照运输能力进行排序
            # self.FlyPlane = sorted(b["UAV_we"] ,key = lambda uav:uav["load_weight"],reverse = True)
            # 将购买成功的无人机添加到任务列表中，初始化为0
            chargeunm = len([task for task in self.tasklist if task.getcharge()])
            len_cha = len(self.FlyPlane) - len(self.tasklist)
            if len_cha > 0:
               self.tasklist.extend([task_uav() for i in range(len_cha)])
            goods = b["goods"]
            self.totalgoods = goods
            # ===========================test mxq ============================================
            self.tempgoodlast = [good for good in goods if good["no"] not in self.enemygoodno and good["no"] not in self.goodnohasbeendetected]
            pairlist = self.makepairforgoodanduav()  
            # ======================================end=======================================
            # 垂直上升,一架一架的离开，直达所有飞机到达最低高度
            self.z_status = [sin_z["z"] if(sin_z["x"]==self.parking_x and sin_z["y"]==self.parking_y) and sin_z["status"]!=1 and sin_z["z"] <= self.flyhlow \
                            else -1 for sin_z in self.FlyPlane ]
            self.xyz_status = [[uavxy["x"],uavxy["y"],uavxy["z"]] if uavxy["status"]!=1 else [-1,-1,-1] for uavxy in self.FlyPlane]
            
            self.killdutynum = len([i for (i,uav) in enumerate(self.FlyPlane) if self.tasklist[i].getdirectkill() and uav["status"] !=1])
            self.occupydutynum = len([i for (i,uav) in enumerate(self.FlyPlane) if self.tasklist[i].getoccupy() and uav["status"] !=1])
            for enemy in self.uavenemy:
                if enemy["goods_no"] != -1 and enemy["goods_no"] not in self.enemygoodno:
                    self.enemygoodno.append(enemy["goods_no"])
            self.goodposition = [[good["start_x"],good["start_y"]] for good in goods if good["status"] == 0 and good["no"] not in self.enemygoodno]
            self.goodposition.extend([[good["end_x"],good["end_y"]] for good in goods if good["status"] == 0 and good["no"] not in self.enemygoodno])
            for i,_ in enumerate(self.FlyPlane): 
                # 毁掉的飞机直接跳过
                if self.FlyPlane[i]["status"] == 1:
                    continue
                # 根据self.FlyPlane的编号找到相对应的uavtask
                uavtask = [uav for uav in self.tasklist if uav and uav.getuavno() == self.FlyPlane[i]["no"]]
                if uavtask:
                    uavtask = uavtask[0]
                else:
                    uavtask = task_uav()
                    uavtask.setuavno(self.FlyPlane[i]["no"])
                # 如果无人机的状态为需要充电并且无人机当前位置在停机坪则进行充电
                if len(enemylast) == 1 and len(welast) == 1 and self.FlyPlane[i]["status"] !=1 and self.FlyPlane[i]["goods_no"] == -1:
                    uavtask.setdirectkill(True)
                    uavtask.setcharge(False)
                    uavtask.setgetgoodxy(False)
                    uavtask.setupwithgood(False)
                    uavtask.setputgoodxy(False)
                    uavtask.setdowntogetgood(False)
                    uavtask.setdowntoputgood(False)
                if uavtask.getcharge():
                    # 如果观测到停机坪有充电后的飞机起飞则需要进行避让
                    # 对F3飞机直接进行飞行
                    if self.FlyPlane[i]["type"] == "F3":
                        if (self.FlyPlane[i]["z"]+1) not in self.z_status:
                            uavtask.setcharge(False)
                            uavtask.setupwithnogood(True)
                            self.FlyPlane[i]["z"] += 1
                            self.recorduavz(i) 
                            self.FlyPlane[i]["status"] == 0
                            self.tasklist[i] = uavtask
                            continue
                    x_dis = self.parking_x - self.FlyPlane[i]["x"] 
                    y_dis = self.parking_y - self.FlyPlane[i]["y"]
                    if abs(x_dis)==1 or abs(y_dis)==1:
                        needvoiduav = len([i for i in self.z_status if i != -1])
                        if needvoiduav or self.parkingenemynum != 0:
                            continue
                    if x_dis == 0 and y_dis == 0:
                        #needvoiduav = len([i for i in self.z_status if i != -1])
                        if self.FlyPlane[i]["z"] != 0 and (self.FlyPlane[i]["z"]-1 == 0 or \
                        [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"]-1] not in self.xyz_status):
                            self.FlyPlane[i]["z"] -= 1
                        if self.FlyPlane[i]["z"] == 0:
                            type = self.FlyPlane[i]["type"]
                            chargespeed = self.chargeinfo[type][1]
                            capacity = self.chargeinfo[type][0]
                            if self.FlyPlane[i]["remain_electricity"] + chargespeed < capacity:
                                self.FlyPlane[i]["remain_electricity"] += chargespeed 
                            else:
                                self.FlyPlane[i]["remain_electricity"] = capacity
                                uavtask.setcharge(False)
                                uavtask.setupwithnogood(True) 
                        self.recorduavz(i)  
                    elif x_dis != 0 or y_dis != 0:
                        self.movexy(i,self.parking_x,self.parking_y)
                    self.recorduavxyz(i)           
                # 充电完毕飞到最低高度
                elif uavtask.getupwithnogood() and ((self.FlyPlane[i]["z"]+1 not in self.z_status) or (self.FlyPlane[i]["x"] != self.parking_x or self.FlyPlane[i]["y"] != self.parking_y)):
                    self.FlyPlane[i]["z"] += 1
                    if self.FlyPlane[i]["x"] == self.parking_x and self.FlyPlane[i]["y"] == self.parking_y:
                       self.recorduavz(i)
                    if self.FlyPlane[i]["z"] > self.flyhlow:
                        if self.FlyPlane[i]["type"] == "F3":
                            if self.killdutynum <len(self.uavenemy):
                                uavtask.setdirectkill(True)
                                self.killdutynum += 1
                            else:
                                uavtask.setoccupy(True)
                                self.occupydutynum += 1
                        else:
                            uavtask.setgetgoodxy(True)
                        uavtask.setupwithnogood(False)
                    self.recorduavxyz(i)
                elif uavtask.getgetgoodxy():
                    if pairlist[i] == -1:
                        tempcapacity = self.chargeinfo[self.FlyPlane[i]["type"]][0] 
                        if self.FlyPlane[i]["remain_electricity"] <= 0.5 * tempcapacity:
                            if chargeunm <= 2:
                                self.freeuavavoidgood(i)
                                uavtask.setcharge(True)
                                uavtask.setgetgoodxy(False)
                            else:
                                self.MovetoAttack(i)
                            self.recorduavxyz(i)
                            continue
                        if self.FlyPlane[i]["x"] == self.parking_x and self.FlyPlane[i]["y"] == self.parking_y:
                            self.parkingrandmove(i)
                            self.recorduavxyz(i)
                        else:
                             self.MovetoAttack(i)
                             self.recorduavxyz(i)
                        continue
                    choosegood = self.tempgoodlast[pairlist[i]]
                    goodstartx = choosegood["start_x"]
                    goodstarty = choosegood["start_y"]
                    x_dis = goodstartx - self.FlyPlane[i]["x"]
                    y_dis = goodstarty - self.FlyPlane[i]["y"]
                    if x_dis == 0 and y_dis == 0:
                        if choosegood["no"] not in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.append(choosegood["no"])
                        nextposition = [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"] -1]
                        if  choosegood["remain_time"] > self.FlyPlane[i]["z"] and (nextposition not in self.xyz_status):
                            uavtask.setend(choosegood["end_x"],choosegood["end_y"])
                            uavtask.setgoodno(choosegood["no"])
                            uavtask.setelectricitycost(choosegood["weight"])
                            uavtask.setdowntogetgood(True)
                            uavtask.setgetgoodxy(False)
                            self.FlyPlane[i]["z"] -= 1
                    else:
                        self.movexy(i,goodstartx,goodstarty)
                    self.recorduavxyz(i)
                elif uavtask.getdowntogetgood():
                    if  self.FlyPlane[i]["z"] == 0:
                        uavtask.setdowntogetgood(False)
                        if uavtask.getgoodno() in [good["no"] for good in goods]:
                            self.FlyPlane[i]["goods_no"] = uavtask.getgoodno()
                            self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                            uavtask.setupwithgood(True)
                        else:
                            uavtask.setupwithnogood(True)
                    else:
                        self.FlyPlane[i]["z"] -= 1
                    self.recorduavxyz(i)
                elif uavtask.getupwithgood():
                    self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                    self.FlyPlane[i]["z"] += 1
                    if self.FlyPlane[i]["z"] > self.flyhlow:
                        uavtask.setupwithgood(False)
                        uavtask.setputgoodxy(True)
                    self.recorduavxyz(i)
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
                    self.recorduavxyz(i)
                elif uavtask.getdowntoputgood():
                    self.FlyPlane[i]["remain_electricity"] -= uavtask.getelectricitycost()
                    if  self.FlyPlane[i]["z"] == 0:
                        if uavtask.getgoodno() in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.remove(uavtask.getgoodno())
                        uavtask.setdowntoputgood(False)
                        uavtask.setupwithnogood(True)
                    else:
                        self.FlyPlane[i]["z"] -= 1
                    self.recorduavxyz(i)
                elif uavtask.getoccupy():
                    x_dis = abs(self.enemyparking[0] - self.FlyPlane[i]["x"])
                    y_dis = abs(self.enemyparking[1] - self.FlyPlane[i]["y"])
                    end_x = self.enemyparking[0]
                    end_y = self.enemyparking[1]
                    if x_dis == 0 and y_dis == 0:
                        if self.FlyPlane[i]["z"] - 1 >=2 and [self.FlyPlane[i]["x"],self.FlyPlane[i]["y"],self.FlyPlane[i]["z"] - 1] not in self.xyz_status:
                           self.FlyPlane[i]["z"] -= 1
                    else:
                        self.movexy(i,end_x,end_y)
                    self.recorduavxyz(i)
                elif uavtask.getdirectkill():
                    self.MovetoAttack(i)
                    self.recorduavxyz(i)
                self.tasklist[i] = uavtask
        aviavlePlane = [uav for uav in self.FlyPlane if uav["status"] != 1]
        self.z_status = [sin_z["z"] if (sin_z["x"]==self.parking_x and sin_z["y"]==self.parking_y) and sin_z["status"] !=1 else -1 for sin_z in self.FlyPlane]
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
        carrygoodnum = len([uav for uav in FlyPlane if uav["type"]!="F3"])
        purchaselist = []
        FlyPlane_send["purchase_UAV"] = []
        if pstMatchStatus["time"] == 0:
            enemyaviable = []
            wevalue = 0
            enemyinmyparkingnum = 0
        else:
            wevalue = pstMatchStatus["we_value"]
            enemyaviable = [enemy for enemy in  pstMatchStatus["UAV_enemy"] if enemy["status"] != 1]
            enemyinmyparkingnum = Algo_main.parkingenemynum
        if carrygoodnum <=1 and wevalue>= F4pri  and enemyinmyparkingnum == 0:
            purchaselist = [{"purchase":"F4"} for i in range(int(wevalue/F4pri))]
            # if wevalue >= (F2pri + F4pri):
            #    purchaselist = [{"purchase":"F2"},{"purchase":"F4"}]
            # elif wevalue >= F2pri:
            #    purchaselist = [{"purchase":"F2"}]
            # elif wevalue >= F4pri:
            #    purchaselist = [{"purchase":"F4"}]
        elif enemyinmyparkingnum > 0:
            if enemyinmyparkingnum * F3pri > wevalue:
                purchaselist = [{"purchase":"F3"} for i in range(int(wevalue/F3pri))]
            else:
                purchaselist = [{"purchase":"F3"} for i in range(enemyinmyparkingnum)]
        elif (len(FlyPlane) <=13 and wevalue >= F3pri):
            purchaselist = [{"purchase":"F3"} for i in range(int(wevalue/F3pri))]
        elif (wevalue >= F1pri and avatypes.count("F1") <=1):
            purchaselist.append({"purchase":"F1"})
        elif (wevalue >= F5pri and avatypes.count("F5") <= 1):
            purchaselist.append({"purchase":"F5"})
        elif (wevalue >= F2pri):
            purchaselist = [{"purchase":"F2"} for i in range(int(wevalue/F2pri))]
        #elif (len(enemyaviable) <= 2 and wevalue >= F3pri and avatypes.count("F3") <=1):
            #purchaselist.append({"purchase":"F3"})
        #elif (wevalue >= F3pri and avatypes.count("F3") <= len(enemyaviable)):
            #purchaselist.append({"purchase":"F3"})
        if purchaselist and len([i for i in Algo_main.z_status if i != -1])==0:
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
            totalvalue = sum([uavpridict[type["type"]] for type in FlyPlane])
            print("剩余飞机数量:",len(FlyPlane),"飞机编号:",[i["no"] for i in FlyPlane],"总价值:",pstMatchStatus["we_value"]+totalvalue)
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