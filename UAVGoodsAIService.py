# -*- coding:utf-8 -*-
import json
import numpy as np
import time

class UAVGoodsAIService:
    def __init__(self, host, port, token):
        self.inited = False
        self.map = {}
        self.host = host
        self.port = port
        self.token = token

    def sayHello(self, mystr):
        self.map = json.loads(mystr)
        return self.toJson(self.map["map"])

    def numpyDemo(self):
        n = 1000000
        #生成n*1矩阵
        a = np.random.rand(n)
        b = np.random.rand(n)

        #向量化计算
        tic = time.time()
        c = np.dot(a, b)
        toc = time.time()
        print("sum: {:.5f}, numpy vectorization version takes {:5f} ms".format(c, (1000*(toc-tic))))

        #非向量化，传统for循环
        c = 0
        tic = time.time()
        for i in range(n):
            c = c+a[i]*b[i]
        toc = time.time()
        print("sum: {:.5f}, traditional 'for' version takes {:5f} ms".format(c, (1000*(toc-tic))))

    def toJson(self, obj):
        return json.dumps(obj)
