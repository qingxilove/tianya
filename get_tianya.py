# coding:utf-8
# 2016.09.08
# Author：qingxilove

import re,os,requests
import time,random

class TianYa():
    def __init__(self):
        #PageNumber：帖子页面数，tmpList：用来临时存储每页中获取的图片名，下一页时清空（在GetText()中使用pop方法清空）
        self.PageNumber=1
        self.tmpList=[]
    
    def GetPage(self,PageNumber):
        #本函数获取页面内容
        #页面URL地址
        url="http://bbs.tianya.cn/post-worldlook-223829-"+str(PageNumber)+".shtml"
        print url
        header={"User-Agent":"Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.6.1","Referer":"http://bbs.tianya.cn/post-worldlook-223829-1.shtml"}
        req=requests.get(url,headers=header)
        content=req.content
        return content

    def CheckFileExist(self,filename,dirname):
        #用于检查图片在指定目录中是否存在，存在则重命名，不存在则创建
        realname=filename.split('.')[0] #获取文件名前缀
        for dirpath,dirnames,filenames in os.walk(dirname):
            #dirpath：每次遍历的路径名，dirnames：路径下子目录列表，filenames：目录下所有文件列表（含子目录）
            #os.listdir(dirname):可以列出dirname下所有文件（含文件夹，只限当前目录，不含子文件夹中文件），列表类型。用os.path.isfile()或os.path.isdir()来判断是否为文件或文件夹
            if filename in filenames:
                #os.path.exists(file or dir),可以检查是否存在该文件或文件夹
                #文件夹中存在同名文件的情况
                if realname[::-1][0].isdigit():
                    #文件名前缀中最后一位为数字
                    for i in xrange(len(realname)):
                        #从后往前找到第一个不为数字的位置
                        if realname[::-1][i].isdigit():
                            continue
                        else:
                            # print i
                            try:
                                #文件名中后面的数字部分
                                number=int(realname[len(realname)-i:])+1
                                #新文件名为数字部分加1
                                NewFileName=realname[:-i:]+str(number)+filename.split('.')[1]
                                NewFileName=self.CheckFileExist(NewFileName,dirname)
                                # print NewFileName
                                return NewFileName
                            except ValueError :
                                continue
                else:
                    #文件名前缀中最后一位不是数字
                    NewFileName=realname+'1'+'.jpg'
                    NewFileName=self.CheckFileExist(NewFileName,dirname)
                    # print NewFileName
                    return NewFileName
            else:
                #文件夹中没有该文件
                return filename
                # print filename

    def GetIamge(self,content):
        #获取当前页面中所有的图片地址
        #存储每页中图片的url
        ImgUrls=[]
        #下面这个是找出了页面中正文中所有的图片，包含了非楼主发的图片
        # ImgUrls=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.jpg)"'),content)
        #只获取楼主发的图片，下面获取的是楼主发言的楼层
        pattern=re.compile('_host="%E9%84%99%E8%A7%86%E6%8A%A2%E6%B2%99%E5%8F%91%E7%9A%84".*?class="bbs-content(.*?)href="#fabu_anchor"',re.S)
        result=re.findall(pattern,content)
        for item in result:
            tmpUrl=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.[a-z]{3,4})"'),item)
            #匹配每个发言中是否含有图片
            #含有图片则追加到列表中
            if tmpUrl:
                ImgUrls.extend(tmpUrl)
        return ImgUrls

    def DownloadImage(self,ImgUrls):
        #获取当前页面中楼主发的图片，并保存到本地
        header={"User-Agent":"Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.6.1","Referer":"http://bbs.tianya.cn/post-worldlook-223829-1.shtml","Accept":"image/png,image/*;q=0.8,*/*;q=0.5"}
        #图片下载需要的headers与正文不一样，需加上Accept一项。否则不能获取到正确的图片
        for url in ImgUrls:
            #开始下载图片
            imgContent=requests.get(url,headers=header).content
            #获取图片名
            imgNamePattern=re.compile('http.*/(.*\.[a-z]{3,4})')
            imgName=re.findall(imgNamePattern,url)
            #检查图片是否已经在硬盘上存在
            newImgName=self.CheckFileExist(imgName[0],'/root/python/tianya/')
            if newImgName:
                #tmpList追加图片名
                self.tmpList.append(newImgName)
                #图片写入硬盘
                with open(newImgName,'w') as f:
                    f.write(imgContent)
        print "Download %d  images!" % len(ImgUrls)


    def GetText(self,content,PageNumber):
        #获取楼主发言的文本，并写入到htm文件
        #获取当前页面中楼主发言楼层
        pattern=re.compile('_host="%E9%84%99%E8%A7%86%E6%8A%A2%E6%B2%99%E5%8F%91%E7%9A%84".*?class="bbs-content(.*?)href="#fabu_anchor"',re.S)
        result=re.findall(pattern,content)
        print "楼主发言 %d 次！"% len(result)
        #Htm文件头部，编码及标题
        fileHead='<head>\n<meta charset="utf-8">\n</head><br><h1>第'+str(PageNumber+1)+'页</h1>'
        #开始写入文件
        with open(str(PageNumber+1)+'.htm','w') as f:
            f.write(fileHead)
            #写入文件头
            for item in result:
                #每个item就是楼主的一个发言，如果发言中有图片，则将网络图片地址替换为本地图片地址
                #替换掉 xxx楼 信息。
                textPattern=re.compile('<div class="atl-reply">.*?<a class="a-link-2 reply"',re.S)
                item=re.sub(textPattern,"",item)
                #匹配每个发言中是否含有图片
                imgurl=re.findall(re.compile('original="(http://[a-zA-Z0-9].*?/.*?\.[a-z]{3,4})"'),item)
                #含有图片则替换地址
                if len(imgurl)!=0:
                    # print imgurl
                    for url in imgurl:
                        #使用下载保存到本地的图片名，替换掉正文中图片的网络地址
                        # print url
                        if self.tmpList:
                        #这么写是为了排除页面中没有图片，tmpList为空，调用出错的问题
                            imgName=self.tmpList.pop(0) 
                            # print imgName  
                            imgOld=re.findall(re.compile('src="(http.*?original="http://.*?\.[jpgpnif]{3})'),item)[0]

                            item=re.sub(imgOld,imgName,item)
                #写入发言分割符
                f.write(item+'<br>'+'-'*200+'<br>')

TY=TianYa()
#页码范围：1-938
for PageNumber in xrange(0,938):
    content=TY.GetPage(PageNumber+1)
    #下载图片
    ImgUrls=TY.GetIamge(content)
    TY.DownloadImage(ImgUrls)
    #下载正文
    TY.GetText(content,PageNumber)
    #随机等待，防止被服务器拦截
    time.sleep(random.uniform(0.5,5))