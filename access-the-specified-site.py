#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @FileName    : access-the-specified-site.py
    @Created    : 2016/10/11 20:05
    @Author  : Lonlin0731
    @Site    : https://github.com/lonlin0731
    @Description : 批量访问指定的网站（url）
    @Background : 项目中有个需求，从第三方拿到一些数据，通过访问对方的接口，来接收一些json数据，这里
    就是按天来进行访问，url中的date指定的哪一天，访问该url就能得到该天的数据，项目中的需求是批量获取
    过去40天的数据。
    @Usage :
                1、请求的url
                2、连续的日期
'''

import urllib2
import datetime

'''
    需求：访问接口，通过变换不同的时间，请求近40天的以来的数据
	功能：访问指定网址，并对判断异常情况
'''
def main():
    posurl = "http://www.xxx.com/getInfo?date="
    for posdate in range(40,0,-1):
        day = datetime.date.today()- datetime.timedelta(days=posdate)
        sDay = day.strftime('%Y-%m-%d')
        print sDay
        try:
            s = urllib2.urlopen(posurl+sDay).read()
        except urllib2.HTTPError,e:
            print e.code
        except urllib2.URLErrror,e:
            print str(e)

if __name__ == '__main__':
    main()
