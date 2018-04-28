# -*- coding:utf-8 -*-
import sys
from UAVGoodsAIService import *

if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Server Host: " + sys.argv[1])
        print("Server Port: " + sys.argv[2])
        print("Auth Token: " + sys.argv[3])

        demoMap = r'''
        {
            "x": 100,  
            "y": 100,
            "z": 100,
            "comment": "Hello, AI!"
        }
        '''
        ai = UAVGoodsAIService(sys.argv[1], sys.argv[2], sys.argv[3])
        print(ai.sayHello(demoMap))
        print("testing numpy:")
        ai.numpyDemo()
    else:
        print("need 3 arguments")