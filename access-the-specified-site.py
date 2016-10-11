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
        print sDay;
        try:
            s = urllib2.urlopen(posurl+sDay).read()
        except urllib2.HTTPError,e:
            print e.code
        except urllib2.URLErrror,e:
            print str(e)

if __name__ == '__main__':
    main()
