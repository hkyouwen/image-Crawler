#!/usr/bin/env python
# -*- coding: utf-8 -*- 
################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide configure file management service in i18n environment.

Authors: hk
Date:    2015/07/16 17:23:06
""" 
import os
import re
import sys
import gzip
import time
import Queue
import getopt
import shutil
import urllib
import urllib2
import logging
import StringIO
import threading
import ConfigParser

import chardet
import BeautifulSoup

import clist


class Crawler(threading.Thread):
    """Crawl the urls with BFS

    Attributes:
        queue: The queue to reserve the urls that is waitint to be crawled.
        ls: The list to reserve the urls that have been crawled.
        ls1: The list
        ls2: The list
        output: The output filepath.
        timeout: The biggest response time.
        target: The target content to be saved.
    """
    def __init__(self, ls, queue, output, crawl_timeout, target_url):
        """Inits ClassCrawl."""
        threading.Thread.__init__(self)
        self.queue=queue
        self.ls=ls
        self.output=output
        self.timeout=crawl_timeout
        self.target=target_url
        
    def run(self):
        """Run a thread"""
        if self.queue.empty(): #判断队列是否为空
            print "the queue is empty"
            time.sleep(20)
            self.run()
        self.chost=self.queue.get() #get()方法从队头删除并返回一个项目
        if self.chost == "":
            time.sleep(20)
            self.run()
        if self.chost == "none":
            return 0
        self.list_data(self.chost) #遍历页里的地址
        self.run()
    
    def list_data(self,url):
        """Use the lists to remove duplicates"""
        #self.ls1.list_del(url)
        if self.ls.list_query(url):  #查询这个地址是否爬过
            print "url is crawled",url
            return 0
        self.ls.list_add(url)
        print "start crawl:",url
        list_2=[]
        list=self.geturl(url)
        for i in list:   #去除重复数据   
            if i not in list_2:
                list_2.append(i)
                self.queue.put(i)

    def geturl(self,myurl):
        """Get the htmls and save the content we need"""
        user_agent='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'   
        headers={'User-Agent': user_agent}   
        req=urllib2.Request(myurl, headers=headers)
        try:
            mypage=urllib2.urlopen(req,timeout=self.timeout)
        except urllib2.HTTPError as e:
            logging.exception(e)
            return []
        except urllib2.URLError as e:
            logging.exception(e)
            return []
        if mypage.info().get('Content-Encoding') == 'gzip':  #处理压缩网页格式
            buf=StringIO.StringIO(mypage.read())
            f=gzip.GzipFile(fileobj=buf)
            pg=f.read()
        else:
            pg=mypage.read()      
        chardit1=chardet.detect(pg)  #判断网页类型
        print chardit1['encoding']
        content=BeautifulSoup.BeautifulSoup(pg, fromEncoding=chardit1['encoding'])
        content=content.findAll('img')
        urls=[]
        for item in content:
            h=re.compile(r'src="([^"]+)"').search(str(item))
            if h:
                href=h.group(1)
                
                if re.compile(r'http[s]?').search(href) and re.compile(self.target).search(href):
                    urls.append(href)
        
                    ans=urllib2.urlopen(href).read()
                    href=href.replace(':','_')
                    href=href.replace('/','_')
                    href=href.replace('?','_')
                    
                    f=open(os.path.join(self.output,href),'wb')
                    f.write(ans)
                    f.write('\n')
                    f.close()
        return urls

def start_thread(ls,thread_count,openurl, outputfile, crawl_timeout, target_url):
    threads=[]
    for i in range(thread_count):
        threads.append(Crawler(ls, openurl, outputfile, crawl_timeout, target_url))
    for t in threads:
        t.start() #开始线程
    for t in threads:
        t.join()

def main(argv):
    """The main function to get the argvs"""
    opts,args=getopt.getopt(argv[1:], "hvc:")
    for op,value in opts:
        if op == "-h":
            print "help"
            sys.exit()
        elif op == "-v":
            print "the version is 1.0..."
            sys.exit()
        elif op == "-c":
            cf=ConfigParser.ConfigParser()
            cf.read(value)
            inputfile=cf.get("spider", "url_list_file")           #输入路径
            outputfile=cf.get("spider", "output_directory")       #输出路径
            max_depth=cf.getint("spider", "max_depth")            #最大抓取深度
            crawl_interval=cf.getint("spider", "crawl_interval")  #抓取间隔
            crawl_timeout=cf.getint("spider", "crawl_timeout")    #抓取超时
            target_url=cf.get("spider", "target_url")             #目标网页
            thread_count=cf.getint("spider", "thread_count")      #抓取线程数
            openurl=Queue.Queue(0)
            ls=clist.List()   #初始化类
            urls=open(inputfile, 'r')
            for url in urls:
                openurl.put(url.strip('\n'))
                
            urls.close()
            if openurl.empty(): #判断队列是否为空
                print "no seed links"
                sys.exit()
            depth=0
            while depth <= max_depth:  #控制抓取深度
                print depth
                for i in range(thread_count):
                    openurl.put("none")
                start_thread(ls, thread_count, openurl, outputfile, crawl_timeout, target_url)
                depth+=1
            print "reach the max depth"        
        else:
            print "unhandled option"
            sys.exit()
          
if __name__ == '__main__':
    main(sys.argv)
    
