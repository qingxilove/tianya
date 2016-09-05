# coding:utf-8

import re,os,requests
from bs4 import BeautifulSoup
import time
# from PIL import Image
# from io import StringIO


class TianYa():
    def __init__(self):
        self.PageNumber=1
        self.tmpList=[]

    
    def GetPage(self,PageNumber):
        url="http://bbs.tianya.cn/post-worldlook-223829-"+str(PageNumber)+".shtml"
        print url
        header={"User-Agent":"Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.6.1","Referer":"http://bbs.tianya.cn/post-worldlook-223829-1.shtml"}
        req=requests.get(url,headers=header)
        content=req.content
        # soup=BeautifulSoup(content)
        # return content,soup
        return content

    def CheckFileExist(self,filename,dirname):
        realname=filename.split('.')[0]
        for parents,dirnames,filenames in os.walk(dirname):
            if filename in filenames:
                if realname[::-1][0].isdigit():
                    for i in xrange(len(realname)):
                        if realname[::-1][i].isdigit():
                            continue
                        else:
                            # print i
                            try:
                                number=int(realname[len(realname)-i:])+1
                                NewFileName=realname[:-i:]+str(number)+'.jpg'
                                NewFileName=self.CheckFileExist(NewFileName,dirname)
                                # print NewFileName
                                return NewFileName
                            except ValueError :
                                continue
                else:
                    NewFileName=realname+'1'+'.jpg'
                    NewFileName=self.CheckFileExist(NewFileName,dirname)
                    # print NewFileName
                    return NewFileName
            else:
                return filename
                # print filename

    #存储每页中图片的url
    def GetIamge(self,content):
        ImgUrls=[]
        # imgs=soup.findAll(original=re.compile('http.*photo.*\.jpg'))
        # # imgs=soup.findAll('img',attrs={"src":"http://static.tianyaui.com/img/static/2011/imgloading.gif"})
        # pattern=re.compile('original="(.*\.jpg)"')
        # for img in imgs:
        #     ImgUrls.append(re.findall(pattern,str(img)))
        #下面这个是找出了页面中正文中所有的图片，包含了非楼主发的图片
        # ImgUrls=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.jpg)"'),content)
        #只获取楼主发的图片
        pattern=re.compile('_host="%E9%84%99%E8%A7%86%E6%8A%A2%E6%B2%99%E5%8F%91%E7%9A%84".*?class="bbs-content(.*?)href="#fabu_anchor"',re.S)
        result=re.findall(pattern,content)
        for item in result:
            tmpUrl=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.jpg)"'),item)
            # print tmpUrl
            if tmpUrl:
                ImgUrls.extend(tmpUrl)
        # print ImgUrls
        return ImgUrls

    #获取页面中的图片，并保存到本地
    def DownloadImage(self,ImgUrls):
        header={"User-Agent":"Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.6.1","Referer":"http://bbs.tianya.cn/post-worldlook-223829-1.shtml","Accept":"image/png,image/*;q=0.8,*/*;q=0.5"}
        #图片下载需要的headers与正文不一样，需加上Accept一项。否则不能获取到正确的图片
        # if not ImgUrls:
        #     return
        for url in ImgUrls:
            # print url
            imgContent=requests.get(url,headers=header).content
            imgNamePattern=re.compile('http.*/(.*\.jpg)')
            imgName=re.findall(imgNamePattern,url)
            # print imgName[0]
            newImgName=self.CheckFileExist(imgName[0],'/root/python/tianya/')
            # print newImgName
            if newImgName:
                self.tmpList.append(newImgName)
                with open(newImgName,'w') as f:
                    f.write(imgContent)
        print "Download %d  images!" % len(ImgUrls)


    def GetText(self,content,PageNumber):
        pattern=re.compile('_host="%E9%84%99%E8%A7%86%E6%8A%A2%E6%B2%99%E5%8F%91%E7%9A%84".*?class="bbs-content(.*?)href="#fabu_anchor"',re.S)
        result=re.findall(pattern,content)
        print "楼主发言 %d 次！"% len(result)
        with open(str(PageNumber+1)+'.htm','a') as f:
            for item in result:
                #每个item就是楼主的一个发言，如果发言中有图片，则替换为本地图片
                imgurl=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.jpg)"'),item)
                # imgNamePattern=re.compile('http.*/(.*\.jpg)')
                if len(imgurl)!=0:
                    # print imgurl
                    for url in imgurl:
                        # print url
                        # imgName=re.findall(imgNamePattern,url)[0]
                        # imgName=re.findall(imgNamePattern,url)[0]
                        # print imgName
                        # for i in self.tmpList:
                        #     print i
                        # if imgName=='m.jpg':
                            # imgName=self.tmpList.pop(0)
                        #使用下载保存到本地的图片名，替换掉正文中图片的网络地址
                        if self.tmpList:
                            imgName=self.tmpList.pop(0) 
                            # print imgName  
                            imgOld=re.findall(re.compile('src="(http.*?\.jpg)'),item)[0]
                            # print imgOld
                            item=re.sub(imgOld,imgName,item)
                        # print self.tmpList
                f.write('\n'+item+'<br>')
                f.write('-'*50)
            # f.write(result[0])
        # for item in result:
        #     print item
        #     print "\n"+"-"*20

# # GetText(content)

# GetIamge(content)
# # for i in ImgUrls:
# #     print i[0]
# DownloadImage(ImgUrls)
TY=TianYa()
# content,soup=TY.GetPage()
for PageNumber in xrange(502,503):
    content=TY.GetPage(PageNumber+1)
    ImgUrls=TY.GetIamge(content)
    # for url in ImgUrls:
    #     print url
    TY.DownloadImage(ImgUrls)
    TY.GetText(content,PageNumber)
    time.sleep(5)