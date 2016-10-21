#!/usr/bin/env python
#_*_coding:utf-8_*_

import re
import StringIO
import pycurl
import pdfkit
from shutil import rmtree


def main():

    #抓取目录，并进行处理，获取目录中的所有文章链接

    print '='*30
    print '开始抓取目录......'

    #定义缓存区，用于接收response数据
    buf = StringIO.StringIO()
    #创建curl，进行网络请求
    curl = pycurl.Curl()
    #设置请求url
    curl.setopt(pycurl.URL,'http://python.usyiyi.cn/documents/python_278/library/index.html')
    #将responses数据重定向到缓存中
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)
    curl.perform()
    #获取响应状态码
    statu_code = curl.getinfo(pycurl.HTTP_CODE)
    #关闭curl
    curl.close()

    #处理抓取的内容，提取链接

    #将提取的url保存到list中
    lLinks = []

    if statu_code == 200:
        #从缓存中获取html的内容，以便进一步处理
        html = buf.getvalue()
        #利用正则，结合页面特征，提取页面中的目录div内容
        content = re.findall('<div class="toctree-wrapper compound">(.*?)</div>', html, re.S)
        #通过re.findall得到的content是一个list，content[0]即为匹配到的内容，通过目录页面特征发现，就一个匹配项
        links = re.findall('<a.*?href="(.*?)">(.*?)</a>', content[0], re.S)
        #通过re.findall匹配出来多条内容保存在links中，links中的每一项也是一个list，包含两个匹配字段（因为正则中有两个括号），字段item[0]是链接，字段item[1]是链接文本
        for item in links:
            #如果链接中包含#，说明是锚点（一个页面中可以有多个锚点进行快速定位，
            #该页面已经被添加进列表了，锚点就不添加了，不然会就同一个页面请求多次），就不添加进去
            if '#' in item[0]:
                continue

            #处理item[1]字段，因为item[1]字段虽然是a标签的链接文本，但是其中也包含了像字体font这样的样式在里面，要清除这样的样式，提取纯文本
            c = re.compile(r'<[^>]+>',re.S)
            s = c.sub('', item[1])
            #提取目录标号，比如：1、1.1，5，5.1，5.2，5.3等
            if '&#8212;' in s: s = s.replace('&#8212;','-')
            #正则提取目录标号，链接文本s类似这样的：8. Data Types 或 36.15. Built-in Functions ，所以这里正则匹配的时候要两部分（两个括号）
            label = re.findall('^(\d+\.)([\d]*[\.]*)', s)
            #合并，匹配的结果label是一个list，label中包含的元素也是一个列表，包含两个字段，组合之后就是一个序列号，比如8.或36.15.
            Serial_number = label[0][0]+label[0][1]

            #组装信息到lLinks中
            l = []
            l.append(Serial_number) #序列号
            l.append(item[0]) #url链接
            l.append(s) #链接文本，包含序列号的原始文本
            lLinks.append(l)

        print statu_code,'SUC!','目录抓取完毕！'

    else:
        print statu_code,'ERROR!','目录抓取出错，已退出...'
        exit()

    #缓存数据分析完毕，用不到了，关闭缓存
    buf.close()

    #抓取目录中链接的具体内容，循环请求url并进行处理

    print '='*40
    print '开始抓取页面......'

    #将抓取的页面先保存到basepath下面
    #因为后面要将所有html页面转换成一个pdf，本地一次性读取所有文件要快，如果网络请求一个个处理比较慢，而且出现请求失败的情况，比较麻烦
    basepath = '/root/pdf/'
    #需要抓取的页面url的路径
    baseurl = 'http://python.usyiyi.cn/documents/python_278/library/'
    #如果usyiyi网站上面请求失败，则转到python官网再次请求，因为usyiyi网站确实存在有些页面不存在的情况
    baseurl_https= 'https://docs.python.org/2.7/library/'
    #这个列表中用来保存已经保存到本地的页面名字，用来转换成pdf的时候使用
    filenames = []

    #循环请求页面，把所有的页面全部保存到本地
    for l in lLinks:
        filename = basepath + l[0] + 'html' #本地保存的文件路径，类似/root/pdf/36.15.html
        fileurl = baseurl + l[1] #url链接，类似http://python.usyiyi.cn/documents/python_278/library/intro.html
        #书签，其实就是这个页面的名字，这个字段其实用不到，但可以在输出出错提示信息的时候用
        #pdfkit可以将页面h1、h2、h3、h4...这样的html标签生成为pdf中的书签，
        #因为文档中包含有h标签，所以pdf自动就生成了书签，而且具有层级结构
        #同一个文件中的h1是一级书签，h2是二级书签，h3是三级书签，以此类推
        bookmark = l[2]
        
        filenames.append(filename)

        #抓取链接的内容，并提取正文内容，保存到文件中

        buf=StringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL,fileurl)
        curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        curl.perform()
        statu_code = curl.getinfo(pycurl.HTTP_CODE)
        curl.close()

        #页面抓取成功，保存到本地
        if statu_code == 200:
            html = buf.getvalue()
            #正则表达式匹配出正文
            content = re.findall('<div class="document">(.*?)<div class="sphinxsidebar">', html, re.S)
            f = open(filename,'wb')
            #将正文中的链接都去掉，其实只是去掉了a标签的href而且，但是这样一来，正文中的链接都不可点击了，在pdf中没必要有那么多的链接
            content_filter = re.sub('href=".*?"', '',content[0])

            #内容写入本地文件
            f.write(content_filter)
            f.close()

            print statu_code,'SUC!',filename,fileurl

        else:
            #当在usyiyi上抓取失败时，是因为usyiyi网站缺少这个页面，然后向python官网请求该页面
            buf_https=StringIO.StringIO()
            curl_https = pycurl.Curl()
            curl_https.setopt(pycurl.URL,baseurl_https+l[1])
            curl_https.setopt(pycurl.WRITEFUNCTION, buf_https.write)
            curl_https.perform()
            statu_code_https = curl_https.getinfo(pycurl.HTTP_CODE)
            curl_https.close()
            if statu_code_https == 200:
                html_https = buf_https.getvalue()
                #这里匹配的时候有一点不同，官网的这div写法与usyiyi网站上的稍微有点不同
                content_https = re.findall('<div class="document">(.*?)<div class="sphinxsidebar', html_https, re.S)
                f_https = open(filename,'wb')
                content_filter_https = re.sub('href=".*?"', '',content_https[0])
                f_https.write(content_filter_https)
                f_https.close()
                print statu_code_https,'SUC!',filename,baseurl_https+l[1]
            else:
                print statu_code,'ERROR!',filename,filename,baseurl_https+l[1]

            buf_https.close()

        buf.close()

    print '页面抓取完毕！'

    #页面全部已经保存到了本地，下面生成pdf

    print '='*40
    print '开始生成pdf文件......'

    #options有很多选项，其中encoding是这里必需的，不然会有乱码
    #另外linux中要有中文字体，从windos系统的fonts文件夹复制一个中文字体传到linux系统的/shar/即可
    options = { 'encoding':'utf-8' }
    pdfkit.from_file(filenames, '/root/python-library.pdf',options=options)

    print '文件生成成功！'

    #清理生成的文件
    #rmtree(basepath)


if __name__ == '__main__':
    main()

