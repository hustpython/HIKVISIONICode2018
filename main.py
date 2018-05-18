# -*- coding:utf-8 -*-
import sys
import socket
import json
import struct
# python main.py 47.95.243.246 31478 1e49d75c-424c-4e50-9550-106b5b54db97
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
    print(str_all)
    ret = hSocket.sendall(str_all.encode())
    if ret == None:
        ret = 0
    print('sendall', ret)
    return ret

#用户自定义函数, 返回字典FlyPlane, 需要包括 "UAV_info", "purchase_UAV" 两个key.
def AlgorithmCalculationFun(a, b, c):
    FlyPlane = c["astUav"]
    return FlyPlane





def main(szIp, nPort, szToken):
    print("server ip %s, prot %d, token %s\n", szIp, nPort, szToken)

    #Need Test // 开始连接服务器
    hSocket = socket.socket()

    hSocket.connect((szIp, nPort))
    #接受数据  连接成功后，Judger会返回一条消息：
    #=======================yzw============
    #收到的第一条消息
    '''{
    "notice": "token",
    "msg": "hello, what's your token?"
    }'''
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
    '''
    {
    "token": "eyJ0eXAiOiJKV1",
    "notice": "tokenresult",
    "result": 0,
    "roundId": "vvvvv",
    "yourId": "player01"
    }
    '''
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
    '''
    {
    "token": "eyJ0eXAiOiJKV1",
    "notice": "sendmap",
    "time": 0,
    "map": {***}
    }
    '''
    '''
    map format:
    {
    "map": {         //地图信息
        "x": 100,  
        "y": 100,
        "z": 100    //天空最大高度
    },
    "parking": {    // 停机坪
        "x": 0,
        "y": 0
    },
    "h_low": 60,    //"飞行最低高度": 固定值
    "h_high": 100,  //"飞行最高高度": 固定值
    "building": [   //xy表示建筑物的起始位置 
                    // l表示长度，w表示宽度，h表示高度
                    //因此水平上坐标位置为x->x+l-1, y->y+w-1",
        { "x": 10, "y": 10, "l": 10, "w": 10, "h": 80 },
        { "x": 40, "y": 40, "l": 10, "w": 10, "h": 60 }

    ],
     //雾区: 固定值，整个比赛过程中不变，雾区个数根据地图而不同，
     //xy表示雾区的起始位置，l表示长度，w表示宽度，b表示雾区最低高度，
     //t表示雾区的最大高度，水平上坐标为x->x+l-1, y->y+w-1，垂直区间为b->t",
    "fog": [
        { "x": 60, "y": 60, "l": 10, "w": 10, "b": 55, "t": 90 },
        { "x": 35, "y": 47, "l": 15, "w": 20, "b": 60, "t": 100 }
    ],
     //"一开始停机坪无人机信息": "固定值，整个比赛过程中不变，无人机个数根据地图而不同，无人机信息包括 编号和最大载重量，编号单方唯一"
    "init_UAV": [
        { "no": 0, "x":0,"y":0,"z":0,"load_weight": 100,"type": "F1"，"status": 0, "goods_no":-1},
        { "no": 1, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3"，"status": 0, "goods_no":-1},
        { "no": 2, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3"，"status": 0, "goods_no":-1}
    ],

    //"无人机价格表": "固定值，整个比赛过程中不变，no表示无人机购买编号，价格表根据载重不同，价值也不同，初始化的无人机中的载重必定在这个价格表中，方便统计最后价值",
    "UAV_price": [
        { "type": "F1", "load_weight": 100, "value": 300 },
        { "type": "F2","load_weight": 50, "value": 200 },
        { "type": "F3","load_weight": 20, "value": 100 },
        { "type": "F4","load_weight": 30, "value": 150 },
        { "type": "F5","load_weight": 360, "value": 400 }
    ],

    }
    '''
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
    while True:

        # // 进行当前时刻的数据计算, 填充飞行计划，注意：1时刻不能进行移动，即第一次进入该循环时
        FlyPlane = AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane)
        FlyPlane_send['UAV_info'] = FlyPlane

        print(pstMatchStatus["time"])
        #==================mxq=====================
        #发送作战路线
        '''
        {
        "token": "eyJ0eXAiOiJKV1",
        "action": "flyPlane",
        //无人机信息: 必须包含我方控制的所有的无人机的信息（除了撞毁的），信息内容包括无人机编号，xyz坐标， goods_no 货物编号，-1表示没有载货
        "UAV_info": [
                    { "no": 0, "x": 10, "y": 20, "z": 80, "goods_no": 0},
                    { "no": 1, "x": 10, "y": 20, "z": 90, "goods_no": -1},
                    { "no": 2, "x": 10, "y": 30, "z": 40, "goods_no": 2 },
                    { "no": 4, "x": 70, "y": 20, "z": 20, "goods_no": 3 }
                    ],

        //请求购买无人机: 该字段可以没有，如果有表示要购买无人机，提交购买请求后，下一次收到的服务器发送过来的我方无人机信息中会增加相应的无人机信息，初始位置为停机坪,若购买2架F1，一架F2，写法如下：。
       "purchase_UAV":[
                    { "purchase": "F1" },
                    { "purchase": "F1" },
                    { "purchase": "F2" }
                    ]
        }
        '''
        # //发送飞行计划
        nRet = SendJuderData(hSocket, FlyPlane_send)
        if nRet != 0:
            return nRet
        
        # // 接受当前比赛状态
        #=====================mxq===================
        #接收当前状态
        '''
        {
        "token": "eyJ0eXAiOiJKV1",
        "notice": "step",
        //比赛状态: 0表示正常比赛中，1表示比赛结束，收到为1时，参赛者可以关闭连接, 
        "match_status": 0
        //当前时间: 当前的时间，每次给比赛者都会比上一次增加1
        "time": 1,

        //我方无人机信息": "不同时间，数据不同。 我方无人机的当前信息，根据我方传递给服务器后，服务器经过计算后得到的数据， goods_no货物编号， -1表示没有载货物，否则表示装载了相应的货物 
        //状态说明: "无人机状态 0表示正常， 1表示坠毁， 2表示处于雾区， 其他数据暂时未定义"
        "UAV_we": [
            { "no": 0,  "type": "F1","x": 10, "y": 20, "z": 80, "goods_no": -1, "status": 0 },
            { "no": 1,  "type": "F1","x": 10, "y": 20, "z": 90, "goods_no": 0, "status": 0 },
            { "no": 2,  "type": "F1","x": 10, "y": 30, "z": 40, "goods_no": 3, "status": 0 },
            { "no": 3,  "type": "F1","x": 50, "y": 20, "z": 30, "goods_no": 5, "status": 0 },
            { "no": 4,  "type": "F1","x": 70, "y": 20, "z": 20, "goods_no": -1, "status": 1 }
        ],

        //"我方目前总价值": "不同时间，数据不同，表示当前时刻，我方所拥有的所有价值，无人机价值以及获取到的运送物品价值",
        "we_value": 10000, 

        //"敌方无人机信息": "不同时间，数据不同。 敌方无人机的当前信息，根据敌方传递给服务器后，服务器经过计算后得到的数据，如果敌方无人机在雾区，状态为2， x， y，z坐标都为-1，表示无效"
        "UAV_enemy": [
            { "no": 0, "type": "F1","x": 40, "y": 20, "z": 80, "goods_no": -1, "status": 0 },
            { "no": 1,"type": "F1", "x": 20, "y": 20, "z": 90, "goods_no": 7, "status": 0 },
            { "no": 2, "type": "F1","x": 80, "y": 30, "z": 40, "goods_no": -1, "status": 0 },
            { "no": 3, "type": "F1","x": 90, "y": 20, "z": 30, "goods_no": -1, "status": 0 },
            { "no": 4, "type": "F1","x": 17, "y": 20, "z": 20, "goods_no": -1, "status": 1 },
            { "no": 5, "type": "F1","x": -1, "y": -1, "z": -1, "goods_no": -1, "status": 2 }
        ],
        //"敌方目前总价值": "不同时间，数据不同，表示当前时刻，敌方方所拥有的所有价值，无人机价值以及获取到的运送物品价值",
        "enemy_value": 30000, 

        //物品信息: 不同时间，数据不同，no 货物唯一编号， startxy 表示货物出现的地面坐标，endxy表示货物需要运送到的地面坐标， weight表示货物的重量，value表示运送到后货物的价值,start_time:货物出现的时间,remain_time:货物从开始出现到消失的持续时长,left_time: 货物可被捡起的剩余时长，这是个冗余字段，您可以从start_time+remain_time-step得出；一旦被捡起，remain_time和left_time字段无效。status为0表示货物正常且可以被拾起,status为1表示已经被无人机拾起，status为2表示已经运送到目的地，status为3表示无效（无效包括运送过程中撞毁、货物超时未被拾起等，被删除),其实您只能看见0和1状态，因为其他状态的货物会被删除,status为0时，left_time才有意义,已经消失或送到的货物会在列表中被删除。

        "goods": [
            { "no": 0, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 90, "left_time": 75,"status": 1},
            { "no": 1, "start_x": 98, "start_y": 13, "end_x": 3, "end_y": 3, "weight": 51, "value": 90,"start_time":15, "remain_time": 9, "left_time": 0,"status": 0},
            { "no": 2, "start_x": 15, "start_y": 63, "end_x": 81, "end_y": 33, "weight": 15, "value": 20,"start_time":15, "remain_time": 7, "left_time": 0,"status": 0},
            { "no": 3, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 330, "left_time": 310,"status": 0},
            { "no": 5, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100,"start_time":15, "remain_time": 1, "left_time": 2,"status": 0}
            ]
        }
        '''
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