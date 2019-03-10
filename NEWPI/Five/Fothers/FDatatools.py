#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用来多个key 对应一个value


"""
class Rome():
    key = dict()
    value = dict()
    count = 0

    def __init__(self, **args):

        for i, d in args.iteritems():
            self.count += 1
            self.key.setdefault(i, self.count)
            self.value.setdefault(self.count, [d,1])



    def __str__(self):
        if self.count != 0:
            strs = 'Rome('
            for i, d in self.key.iteritems():
                strs = " {}{}:{}:{}, ".format(strs, i, d, self.value[d])
            return ''.join([strs, ')'])
        else:
            return 'Rome(None)'

    def __getitem__(self, key):
        if self.key.has_key(key):
            return self.value[self.key[key]][0]
        else:
            raise KeyError(key)

    def __setitem__(self, key,value):
        if self.key.has_key(key):
            self.value[self.key[key]][0]=value
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        """
        删除某个key，当最后一个key被删掉时，对应的值也会被删掉
        :param key:
        :return:
        """
        if self.key.has_key(key):
            if self.value[self.key[key]][1]>1:
                self.value[self.key[key]][1]-=1
                del self.key[key]
            else:
                del self.value[self.key[key]]
                del self.key[key]
        else:
            raise KeyError(key)

    def setdefault(self, **args):

        for i, d in args.iteritems():
            self.count += 1
            self.key.setdefault(i, self.count)
            self.value.setdefault(self.count, [d,1])


    def bondKey2Key(self,*keys):
        """
        对已存在的existedKey值进行添加几个不同的newKey值，前提每个newKey
        必须在Rome总的所有key中是唯一的，否贼会忽略这个newKey。
        :param existedKey:
        :param newKey:
        :return:
        """
        m,n,existedKey,count=0,0,None,0
        for key in keys:
            if self.key.has_key(key):
                count += 1
                if count == 1:
                    existedKey = key
                    continue
                if key != existedKey:
                    strs="already exist {}".format(key)
                    raise KeyError(strs)
        if existedKey==None:
            raise  KeyError('no valid key')
        for i in keys:
            if not self.key.has_key(i):
                self.key.setdefault(i, self.key[existedKey])
                self.value[self.key[existedKey]][1] += 1

    def has_key(self,key):
        return  self.key.has_key(key)

    def get_relative_key(self,key):
        print self[key]

if __name__ =="__main__":
    l = Rome(a=100, j='hello',u=230)
    l.bondKey2Key('a', 'w','b')
    # print l
    del l['a']
    # print l
    # print l
    # print l['a']
    test={'aa':36}
    l.setdefault(**test)
    # print l
    l.bondKey2Key('aa','a')
    # print l
    l.bondKey2Key('aa1', 'a')
    print l
    l.get_relative_key('a')
    # print l['a'] is l['w']
    # l['w']=110
    # print l
    # print l['a']


