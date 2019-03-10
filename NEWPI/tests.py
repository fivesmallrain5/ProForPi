#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import numpy as np
from collections import deque
# N=7
#
# def test(n):
#     weight = np.ones(N) / N
#     ab = [i + 2 for i in range(1000)]
#     a = np.array(ab)
#     start = time.time()
#     for i in range(10000):
#         # np.convolve(weight,a)
#         # np.convolve(weight, a,'same')
#         np.convolve(weight, a, 'valid')
#     end = time.time()
#     return "卷积单位：{} 总耗时：{}  每次耗时：{}\n".format(n,end-start,(end-start)/10000)
#
#
#
class AllPara(object):
    data = dict({'None':0})

    @staticmethod
    def updata(value):
        assert isinstance(value,dict)
        for i in value.iteritems():
            AllPara.data.setdefault(i[0],i[1])



if __name__ =="__main__":
    # weight = np.ones(N) / N
    # wightbag = deque((0 for i in range(N)),maxlen=N)
    # wightbag.append(1)
    # wightbag.append(1)
    # wightbag.append(1)
    # wightbag.append(1)
    # wightbag.append(1)
    # wightbag.append(2)
    # print wightbag
    # b= np.convolve(weight,wightbag,'valid')
    # print b
    a={2:100}
    AllPara.updata(a)
    print AllPara.data





