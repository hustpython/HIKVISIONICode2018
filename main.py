# -*- coding:utf-8 -*-
import sys
import socket
import json
# python main.py 47.95.243.246 31430 03007105-159b-4027-8edb-dcd8e5c95eeb
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
        self.upwithnogood = True
        self.downtogetgood = False
        self.upwithgood = False 
        self.downtoputgood = False
        self.climbbuilding = False
        self.getgoodxy = False
        self.putgoodxy = False
        self.end_x = -1
        self.end_y = -1
        self.goodno = -1
        self.uavno = -1
    #===goodno为-1时请求上升
    def setuavno(self,no):
        self.uavno = no 
    def getuavno(self):
        return self.uavno
    def setupwithnogood(self,state):
        self.upwithnogood = state 
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
    def setclimbbuilding(self,state):
        self.climbbuilding = state 
    def getclimbbuilding(self):
        return self.climbbuilding
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
    def AlgorithmCalculationFun(self,a, b, c):
        #parse matchstatus
        # good_no 出现 -1 的情况：
        # 1.在停机坪或故意不运送货物
        # 2.运送途中出现撞机，且status = 1.
        # 3.将货物运送到目的地后，在寻找下一个货物地点中
        flayhlow = a["h_low"]
        flayhhight = a["h_high"]
        goodshasbeenchoose = []
        buildings = [{"x_start":buildinfo["x"],"x_end":buildinfo["x"]+buildinfo["l"],\
                    "y_start":buildinfo["y"],"y_end":buildinfo["y"]+buildinfo["w"],
                    "z_start":0,"z_end":buildinfo["h"]}\
                    for buildinfo in a["building"]]
        if b["time"] == 0:
            FlyPlane = c["astUav"]
        else:
            FlyPlane = b["UAV_we"]
            goods = b["goods"]
            # 垂直上升,一架一架的离开，直达所有飞机到达最低高度
            z_status = [sin_z["z"] for sin_z in FlyPlane ]
            #waitinguav = []
            xyz_status = [[uavxy["x"],uavxy["y"],uavxy["z"]] for uavxy in FlyPlane]
            for i,_ in enumerate(FlyPlane):
                lastgoods = [good for good in goods if good["no"] not in goodshasbeenchoose \
                             and good["no"] not in self.goodnohasbeendetected]
                # 如何处理毁掉的uav,待修改
                if FlyPlane[i]["status"] == 1:
                    continue
                #根据FlyPlane的编号找到相对应的uavtask
                uavtask = [uav for uav in self.tasklist if uav and uav.getuavno() == FlyPlane[i]["no"]]
                if uavtask:
                    uavtask = uavtask[0]
                else:
                    uavtask = task_uav()
                    uavtask.setuavno(FlyPlane[i]["no"])

                if uavtask.getupwithnogood() and ((FlyPlane[i]["z"]+1) not in z_status or (FlyPlane[i]["x"] != a["parking"]["x"] or FlyPlane[i]["y"] != a["parking"]["y"])) :
                    FlyPlane[i]["z"] += 1
                    z_status[i] += 1
                    if FlyPlane[i]["z"] > flayhlow:
                        uavtask.setupwithnogood(False)
                        uavtask.setgetgoodxy(True)
                elif uavtask.getgetgoodxy() :
                    dis = [(good["start_x"] - FlyPlane[i]["x"])**2 + (good["start_y"] - FlyPlane[i]["y"])**2 \
                           if good["weight"]<=FlyPlane[i]["load_weight"] else float("inf") for good in lastgoods]
                    if not dis or min(dis) == float("inf"):
                        continue
                    z_status[i] = -1
                    min_dis_index = dis.index(min(dis))
                    if lastgoods[min_dis_index]["no"] not in goodshasbeenchoose:
                       goodshasbeenchoose.append(lastgoods[min_dis_index]["no"])
                    x_dis = lastgoods[min_dis_index]["start_x"] - FlyPlane[i]["x"]
                    y_dis = lastgoods[min_dis_index]["start_y"] - FlyPlane[i]["y"]
                    temp_flyx = FlyPlane[i]["x"]
                    flag_x = 0
                    if x_dis != 0:                     
                        res = [False if buildsize["x_start"] <= FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) <= buildsize["x_end"] and \
                        buildsize["y_start"] <= FlyPlane[i]["y"] <= buildsize["y_end"] and FlyPlane[i]["z"] < buildsize["z_end"] else True for \
                        buildsize in buildings] 
                        if False not in res and ([FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))),FlyPlane[i]["y"],FlyPlane[i]["z"]] not in xyz_status):
                            temp_flyx = FlyPlane[i]["x"]
                            FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                            flag_x = 1
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                        else:
                            FlyPlane[i]["z"] += 1
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                            uavtask.setclimbbuilding(True)
                            continue
                    if y_dis != 0:
                        res = [False if buildsize["x_start"] <= FlyPlane[i]["x"]<= buildsize["x_end"] and \
                              buildsize["y_start"] <= FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) <= buildsize["y_end"] \
                              and FlyPlane[i]["z"] <  buildsize["z_end"] else True for buildsize in buildings]
                        if False not in res and ([FlyPlane[i]["x"],FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))),FlyPlane[i]["z"]] not in xyz_status):
                            FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                        else:
                            if flag_x or x_dis == 0:
                               FlyPlane[i]["z"] += 1
                               FlyPlane[i]["x"] = temp_flyx
                               xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                            uavtask.setclimbbuilding(True)
                            continue
                    if x_dis == 0 and y_dis == 0:
                        uavtask.setgoodno(lastgoods[min_dis_index]["no"])
                        if lastgoods[min_dis_index]["no"] not in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.append(lastgoods[min_dis_index]["no"])
                        uavtask.setend(lastgoods[min_dis_index]["end_x"],lastgoods[min_dis_index]["end_y"])
                        uavtask.setdowntogetgood(True)
                        uavtask.setgetgoodxy(False)
                        FlyPlane[i]["z"] -= 1
                elif uavtask.getdowntogetgood():
                    if  FlyPlane[i]["z"] == 0 :
                        if uavtask.getgoodno() in [good["no"] for good in goods]:
                            FlyPlane[i]["goods_no"] = uavtask.getgoodno()
                            uavtask.setdowntogetgood(False)
                            uavtask.setupwithgood(True)
                        else:
                            uavtask.setdowntogetgood(False)
                            uavtask.setupwithnogood(True)
                    else:
                        FlyPlane[i]["z"] -= 1

                elif uavtask.getupwithgood():
                    FlyPlane[i]["z"] += 1
                    if FlyPlane[i]["z"] > flayhlow:
                        uavtask.setupwithgood(False)
                        uavtask.setputgoodxy(True)
                elif uavtask.getputgoodxy():
                    x_dis = uavtask.getend()[0] - FlyPlane[i]["x"]
                    y_dis = uavtask.getend()[1] - FlyPlane[i]["y"]
                    temp_flyx = FlyPlane[i]["x"]
                    flag_x = 0
                    if x_dis != 0:                     
                        res = [False if buildsize["x_start"] <= FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))) <= buildsize["x_end"] and \
                        buildsize["y_start"] <= FlyPlane[i]["y"] <= buildsize["y_end"] and FlyPlane[i]["z"] < buildsize["z_end"] else True for \
                        buildsize in buildings] 
                        if False not in res and ([FlyPlane[i]["x"]+int(x_dis/(abs(x_dis))),FlyPlane[i]["y"],FlyPlane[i]["z"]] not in xyz_status):
                            FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                            flag_x = 1
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                        else:
                            FlyPlane[i]["z"] += 1
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                            uavtask.setclimbbuilding(True)
                            continue
                    if y_dis != 0:
                        res = [False if buildsize["x_start"] <= FlyPlane[i]["x"]<= buildsize["x_end"] and \
                              buildsize["y_start"] <= FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))) <= buildsize["y_end"] \
                              and FlyPlane[i]["z"] <  buildsize["z_end"] else True for buildsize in buildings]
                        if False not in res and ([FlyPlane[i]["x"],FlyPlane[i]["y"]+int(y_dis/(abs(y_dis))),FlyPlane[i]["z"]] not in xyz_status):
                            FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                            xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                        else:
                            if flag_x or x_dis == 0:
                               FlyPlane[i]["z"] += 1
                               FlyPlane[i]["x"] = temp_flyx
                               xyz_status[i] = [FlyPlane[i]["x"],FlyPlane[i]["y"],FlyPlane[i]["z"]]
                            uavtask.setclimbbuilding(True)
                            continue
                    if x_dis == 0 and y_dis == 0:
                        uavtask.setputgoodxy(False)
                        uavtask.setdowntoputgood(True)
                elif uavtask.getdowntoputgood():
                    if  FlyPlane[i]["z"] == 0:
                        if uavtask.getgoodno() in self.goodnohasbeendetected:
                            self.goodnohasbeendetected.remove(uavtask.getgoodno())
                        uavtask.setdowntoputgood(False)
                        uavtask.setupwithnogood(True)
                    else:
                        FlyPlane[i]["z"] -= 1
                self.tasklist[i] = uavtask
        #===============================把这些限制条件先放一放=======================
        # #parse mapinfo
        # restricts


        fogs = [{"x_start":foginfo["x"],"x_end":foginfo["x"]+foginfo["l"]-1,\
                "y_start":foginfo["y"],"y_end":foginfo["y"]+foginfo["w"]-1,
                "z_start":foginfo["b"],"z_end":foginfo["t"]}\
                for foginfo in a["fog"]]
        
        # 购买uav
        def toPurchaseUav(self):
            pass   
        '''while (len(set([[uav["x"],uav["y"],uav["z"]] for uav in FlyPlane])) != len(FlyPlane)):
            from collections import defaultdict
            d = defaultdict(list)
            for i,uavxyz in enumerate(FlyPlane):
                d[k].append(va)'''


        print(FlyPlane[3])          
        return FlyPlane





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
    Algo_main = Algo()
    while True:

        # // 进行当前时刻的数据计算, 填充飞行计划，注意：1时刻不能进行移动，
        # //即第一次进入该循环时,此时pstMatchStatus只有 "time" 信息
        # pstMapInfo 在一场比赛中是固定的，不会变
        # pstMatchStatus 服务器根据用户发送的数据经过处理后返回的信息
        # pstFlayPlane 是用户根据服务器的数据，经过自己的算法计算后得到的作战计划，需要发送给服务器
        
        FlyPlane = Algo_main.AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane)
        FlyPlane_send['UAV_info'] = FlyPlane
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