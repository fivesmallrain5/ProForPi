#!/usr/bin/env python
# -*- coding: utf-8 -*-

def readTable(path=None,f=None):
    """
    读一个文件，返回里面固定格式数据。‘#’ 可以用来注释，忽略中英文；;，,的区别
    解析文件格式为：

    TABLE: 表名字1
    参数1: 参数1的值,参数2：参数2的值，
    参数3: 参数3的值，
    TABLE: 表名字2
    参数1: 参数1的值，参数2: 参数2的值，
    参数3: 参数3的值，

    :param f: 一个只读文件的指针
    :param path:  文件路径
    :return:字典
            ｛
            表名字1：{ 'cellContent':｛参数1: 参数1的值，参数2: 参数2的值，参数3: 参数3的值｝,
                        'lineno': （表在文中第几行开始，第几行结束） ，
                        'tableNumber':第几个表}，

            表名字2： 'cellContent':｛参数1: 参数1的值，参数2: 参数2的值，参数3: 参数3的值｝,
                        'lineno': （表在文中第几行开始，第几行结束），
                        'tableNumber':第几个表}，
            ｝
    """
    try:
        if f ==None:
            assert path!=None
            f=open(path,'r')
        f.seek(0)
        tables,index,tablenumber={},0,0
        currenttable,contentCell="",dict()
        for i in f.readlines():
            index+=1
            i = i.replace(' ', '')#取出空格
            if i.strip().startswith('#') or i=='\n':
                continue
            elif i.strip().startswith('TABLE'):
                if '：' in i:
                    i=i.replace('：',':')
                i = i.strip().split(':')
                currenttable = i[1]
                tables.setdefault(currenttable, dict())
                tables[currenttable].setdefault("lineno", (index,0))
                tablenumber+=1
                tables[currenttable].setdefault("tableNumber",tablenumber)
                contentCell = dict()
            else:
                if ':'  not in i and  '：' not in i:
                    continue
                if '：' in i:
                    i=i.replace('：',':')
                if '，' in i:
                    i=i.replace('，',',')
                i=i.strip().split(",")
                for j in i:
                    if j == '':
                        continue
                    contentCell.setdefault(j.strip().split(':')[0],j.strip().split(':')[1])
                tables[currenttable].setdefault("cellContent", contentCell)
                tempindex=tables[currenttable]["lineno"][0]
                tables[currenttable].update(lineno=(tempindex,index))
    except:
        return None
    if f==None:
        f.close()
    if tables=={}:
        return None
    else:
        return tables

def insertTable(tables,tablename,path,where):
    """
    给文件插入一个表，会自动检查表是否允许插入
    :param tables: 字典格式的表{参数1: 参数1的值，参数2: 参数2的值，}
    :param path:  文件路径
    :param where:
                -1:  默认插在文件末尾，
                0:  插在最开始
              '数字或其他关键字’如果是具体某个表名或第几个表，则插在此表末尾，


    :return:  插入成功True,失败False
    """
    assert  isinstance(tables,dict)
    templines ,index,tablecount= [],-1,-1
    with open(path, 'r') as f:
        for i in f.readlines():
            templines.append(i)
        f.seek(0)

        line = "\nTABLE:{}".format(tablename) + "\n"
        tempindex=1
        for keys, values in tables.iteritems():
            if tempindex%3==0:
                line = "".join([line, "    {} :{},\n".format(keys, values)])
            else:
                line = "".join([line, "    {} :{},".format(keys, values)])
            tempindex+=1
        line += '\n'

        tableinfor=readTable(f=f)
        if tableinfor !=None:
            if tableinfor.get(tablename, False) != False:
                raise ValueError("tablename already exsit!")
            flag=False
            for keys, values in tableinfor.iteritems():
                if keys == where or where == values['tableNumber']:
                    templines.insert(values['lineno'][1], line)
                    flag = True
                    break
            if not flag and where!=0 :
                where=-2
        else:
            where=-3

        if where <=0:
            if where==0:
                templines.insert(0,line)
            else:
                templines.append(line)

    with open(path,'w') as f:
        for i in templines:
            f.writelines(i)
    return True



def updataTable(tables,tablename,path):
    """
    更新某个特别的表
    :param tables: 字典类型的表
    :param tablename: 表名字
    :param path: 文件
    :return:
    """
    tableinfor = readTable(path)
    if tableinfor.has_key(tablename):
        delTable(tablename, path)
        insertTable(tables, tablename, path, tableinfor[tablename]['tableNumber'] - 1)
    else:
        raise ValueError('table is not exist!')
    return True


def delTable(tablename,path):
    """
    删除文件中的特定表
    :param tablename: 表的名字删除表
    :param path:  文件路径
    :return: 删除成功为True
            否则为False
    """
    tableinfor = readTable(path)
    templines=[]
    if tableinfor != None:
        if tableinfor.get(tablename, False) == False:
                return False
        else:
            with open(path,'r') as f:
                f.seek(0)
                for i in f.readlines():
                    templines.append(i)
            d1,d2=tableinfor[tablename]['lineno']
            del templines[d1-1:d2+1]
            with open(path,'w') as f:
                for i in templines:
                    f.writelines(i)
        return True




def getTableNames(path):
    """
    返回某个文件内的所有表
    :param path: 文件路径
    :return:
    """
    tableinfor = readTable(path)
    return tuple(tableinfor.keys())

def createTable(path):
    with open(path,'w') as f:
        pass






def getcomments(path_f, keys):
    """
    获取某个特别的注释 #path*hello,如果path没有值则返回[]
    :param path_f: 路径或只读文件指针
    :param keys:tuple,list类型数据
    :return: ｛'path':hello｝
    """
    comments = dict().fromkeys(keys)
    for key in keys:
        comments.update({key:[]})
    try:
        with open(path_f, 'r') as f:
            for line in f.readlines():
                if not line.startswith('#'):
                    continue
                else:
                    line = line.lstrip('#')
                    if "*" not in line:
                        continue
                    key,value = line.split('*')
                    if key in keys and value!='':
                        # print key,comments[key],value
                        comments[key].append(value)
                        # print key,comments[key]

    except:
        pass
    return comments

def getComment(path_f):
    """获取所有注释"""
    comments=[]
    f = None
    if isinstance(path_f, str):
        f = open(path_f, 'r')
        f.seek(0)
    try:
        for line in f:
            if not line.startswith('#'):
                continue
            else:
                line = line.lstrip('#')
                comments.append(line)
    finally:
        f.close()
        return comments


def writeComments(path,lines):
    """写注释"""
    f = open(path, 'a+')
    f.seek(0)
    try:
        if '\n'in lines:
            lines=lines.split('\n')
        for line in lines:
            f.write('\n#')
            f.write(line)
    finally:
        f.close()

def removeComments(path,keys):
    """
    删除key对应的注释
    :param path: 路径
    :param keys: tuple,list的keys
    :return:
    """
    templines = []
    with open(path, 'r') as f:
        f.seek(0)
        for line in f:
            templines.append(line)
            if not line.startswith('#'):
                continue
            line = line.lstrip('#').strip()
            if "*" not in line:
                continue
            key = line.split('*')[0]
            if key in keys:
                templines.pop()
    with open(path, 'w') as f:
        f.writelines(templines)


def updateComments(path,comments):
    """
    comments存在则更新对应的数据
    :param path: 文件路径
    :param comments: 字典类型｛"path":"123"｝
    :return:
    """
    assert isinstance(comments, dict)
    keys=comments.keys()
    templines=[]
    with open(path,'r') as f:
        f.seek(0)
        for line in f:
            templines.append(line)
            if not line.startswith('#'):
                continue
            line=line.lstrip('#').strip()
            if "*" not in line:
                continue
            key, value = line.split('*')[0], line.split('*')[1]
            if key in keys:
                templines[-1]="".join(['#',key,'*',comments[key],'\n'])
    with open(path,'w') as f:
        f.writelines(templines)







if __name__ =="__main__":
    path='./new1.txt'
    createTable(path)
    #
    #example2: 插入表
    JIXIE1 = {"名称": "机械1", "型号": "WXTY"}
    lists=['基本信息2','基本信息3','基本信息4','基本信息5','基本信息6','基本信息7']
    for i in lists:
        print  i
        insertTable(JIXIE1,i,path,-1)

    #example3：插入表到指定表后面
    insertTable(JIXIE1, '*特别表', path,'基本信息3' )

    # example1 ：获取文档的表信息
    print  readTable(path)

    # example 删除特定的某一个表
    print delTable('基本信息6',path)

    # example 更新某个特定的表
    JIXIE2 = {"名称": "更新参数2", "型号": "更新参数"}
    print updataTable(JIXIE2,'基本信息',path)

    print getTableNames(path)

