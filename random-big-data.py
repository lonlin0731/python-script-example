#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @FileName    : random-big-data.py
    @Created    : 2016/10/26 22:38
    @Author  : Lonlin0731
    @Site    : https://github.com/lonlin0731
    @Description : 按照数据库表的格式生成大批量的数据，上百万条的数据
    @Background : 为了测试mysql数据库的性能，需要比较多的数据，基本的记录数在100万到1000万之间，使用
    这个脚本进行生成数据，然后利用mysql命令load data infole导入数据到表中
    @Usage : 需要设置的参数就两个
            outfile : 生成的文件的目录
            recordCount : 生成的记录的条数

            其中表结构为4个字段：id, name, age, description
'''

import random
import time

#输出的文件路径
outfile = '/tmp/data.txt'
#生成的记录条数
recordCount = 1000000

def main(outfile,recordCount):
    #使用with，打开的文件会自动关闭，不需要显示调用close()
    with open('/tmp/data.txt', 'wb') as output:
        for i in range(1,recordCount):
            #这里的id为随机的id，是为了演示没有主键及自增的时候情况
            id = random.randint(1,recordCount)
            #随机生成名字，中文名字2-3个字，使用中文，常用字0x4e00-0x9fa5
            name = ''
            for j in range(2,random.randint(4,5)):
                name += unichr(random.randint(0x4e00,0x9fa5))
            #随机生成年龄
            age = random.randint(1,150)
            #随机生成描述，也是中文，1-50个字不等
            description = ''
            for k in range(1,random.randint(1,51)):
                description += unichr(random.randint(0x4e00,0x9fa5))

            #将生成的字段连接成一个字符串，并写入到文件中
            #record = '"{0}","{1}","{2}","{3}"{4}'.format(id , name.encode('utf-8') , age , description.encode('utf-8'), '\n')
            record = '"{1}","{2}","{3}"{4}'.format(id , name.encode('utf-8') , age , description.encode('utf-8'), '\n')
            output.write(record)        


if __name__ == '__main__':
    random.seed()
    start = time.time()
    main(outfile, recordCount)
    end = time.time()
    print 'use time : {0} s'.format(end-start)

