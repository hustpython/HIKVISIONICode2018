# -*- coding:utf-8 -*-
import sys
import socket
import json
# python main.py 47.95.243.246 31343 53eda47f-a90f-417d-be15-30daac19cd66
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
class Algo():
    def __init__(self):
        self.request_down = []
        self.good_selectno = -1
        self.good_needup = []
        self.good_needdown = []
        self.good_to = [0,0]
    def AlgorithmCalculationFun(self,a, b, c):
        FlyPlane = c["astUav"]
        #parse mapinfo
        # restricts

        flayhlow = a["h_low"]
        flayhhight = a["h_high"]

        buildings = [{"x_start":buildinfo["x"],"x_end":buildinfo["x"]+buildinfo["l"]-1,\
                    "y_start":buildinfo["y"],"y_end":buildinfo["y"]+buildinfo["w"]-1,
                    "z_start":0,"z_end":buildinfo["h"]}\
                    for buildinfo in a["building"]]
        fogs = [{"x_start":foginfo["x"],"x_end":foginfo["x"]+foginfo["l"]-1,\
                "y_start":foginfo["y"],"y_end":foginfo["y"]+foginfo["w"]-1,
                "z_start":foginfo["b"],"z_end":foginfo["t"]}\
                for foginfo in a["fog"]]

        uavloadweight = {}
        for i in a["UAV_price"]:
            uavloadweight[i["type"]] = i["load_weight"]
        #print(FlyPlane)
        # 如果uav是寻找goods的起始点，则应该传入起始位置
        # 若uav正在去送goods到终点，则应该传入终点位置
        # map(),pool 多线程
        
            
            # 水平方向的６种飞行方式
            '''horizonfly_modes = [[x+1,y],[x-1,y],[x,y+1],[x,y-1],[x+1,y+1],[x-1,y-1]]
            
            feasiblefly_modes = []
            # 去除操作后会撞墙的 mode
            for every_mode in horizonfly_modes:
                flag = 1
                for every_build in buildings:
                if z < every_build["z_end"] and every_mode[0]>= every_build["x_start"] and \
                    every_mode[0]<= every_build["x_end"] \
                    and every_mode[1] >= every_build["y_start"] and every_mode[1] <= every_build["y_end"]:
                    flag = 0
                if flag:
                    feasiblefly_modes.append(every_mode)
            
            # 利用欧氏距离找出最短路径 mode 
            # 分达到 货物 起点和 货物目的地两种情况
            dis_max = 100000
            short_mode = []
            for every_mode in feasiblefly_modes:
                dis = (x_end - every_mode[0])**2 + (y_end - every_mode[1])
                if dis < dis_max:
                    dis_max = dis 
                    short_mode = every_mode'''
        # 购买uav
        def toPurchaseUav(self):
            pass
            
        #parse matchstatus
        # good_no 出现 -1 的情况：
        # 1.在停机坪或故意不运送货物
        # 2.运送途中出现撞机，且status = 1.
        # 3.将货物运送到目的地后，在寻找下一个货物地点中
        
        if b["time"] >= 1:
        # value of us:b["we_value"]
            UAV_we = b["UAV_we"]
            carryandnormal = [i for i in UAV_we if i["goods_no"]!= -1 and i["status"] == 0]
            notcarryandnormal = [i for i in UAV_we if i["goods_no"] == -1 and i["status"] == 0]
        
            goods = b["goods"]
            for uav in notcarryandnormal:
                for good in goods:
                    if uavloadweight[uav["type"]] > good["weight"]:
                        pass
            # 垂直上升,一架一架的离开，直达所有飞机到达最低高度
            z_status = [sin_z["z"] for sin_z in FlyPlane]
            for i,_ in enumerate(FlyPlane):
                z = FlyPlane[i]["z"]
                no = FlyPlane[i]["no"]
                if no in self.good_needup and z<= flayhlow:
                    FlyPlane[i]["z"] += 1

                elif no in self.good_needup and z > flayhlow:
                    x_dis = self.good_to[0] - FlyPlane[i]["x"]
                    y_dis = self.good_to[1] - FlyPlane[i]["y"]
                    if x_dis != 0:
                        FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                    if y_dis != 0:
                        FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                    if x_dis == 0 and y_dis == 0:
                        self.good_needup.remove(no)
                        if no not in self.good_needdown:
                           self.good_needdown.append(no)
                elif z <= flayhlow and (z+1) not in z_status and no not in self.request_down:
                    if i == 0:
                        FlyPlane[i]["z"] += 1
                        z_status[i] += 1
                elif z> flayhlow and no not in self.good_needdown:
                    if i== 0:
                        z_status[i] = -1
                        dis = [(good["start_x"] - FlyPlane[i]["x"])**2 + (good["start_y"] - FlyPlane[i]["y"])**2 for good in goods]
                        min_dis_index = dis.index(min(dis))
                        x_dis = goods[min_dis_index]["start_x"] - FlyPlane[i]["x"]
                        y_dis = goods[min_dis_index]["start_y"] - FlyPlane[i]["y"]
                        if x_dis != 0:
                           FlyPlane[i]["x"] += int(x_dis/(abs(x_dis)))
                        if y_dis != 0:
                           FlyPlane[i]["y"] += int(y_dis/(abs(y_dis)))
                        if x_dis == 0 and x_dis == 0:
                            if FlyPlane[i]["no"] not in self.request_down:
                                self.request_down.append(FlyPlane[i]["no"])
                            FlyPlane[i]["z"] -= 1
                            self.good_selectno = goods[min_dis_index]["no"]
                            self.good_to = [goods[min_dis_index]["end_x"],goods[min_dis_index]["end_y"]]
                elif no in self.good_needdown:
                    if z != 0  and i == 0:
                        FlyPlane[i]["z"] -= 1
                    if z == 0:
                        FlyPlane[i]["goods_no"] = -1
                        #FlyPlane[i]["z"] += 1
                elif no in self.request_down and no not in self.good_needdown:
                    if z != 0  and i == 0:
                        FlyPlane[i]["z"] -= 1
                    if z == 0:
                        FlyPlane[i]["goods_no"] = self.good_selectno
                        if FlyPlane[i]["no"] not in self.good_needup:
                           self.good_needup.append(FlyPlane[i]["no"])
                            
        print(FlyPlane[0])              
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
        #print(pstMatchStatus["time"])
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