#!/usr/bin/env python
#-*- coding: UTF-8 -*-
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

class List:
    """Some process for a list

    Attributes:
        list: A list to use.
    """
    def __init__(self):
        """Initialize a list"""
        self.list=[]

    def list_del(self,data):
        """delete a data from list"""
        self.list.remove(data);

    def list_add(self,data):
        """add a data from list"""
        self.list.append(data)
        
    def list_query(self,data):
        """search for a data in a list"""
        E=0
        while E < len(self.list):
            if self.list[E]==data:
                return 1
            E = E + 1
        return 

            
            
