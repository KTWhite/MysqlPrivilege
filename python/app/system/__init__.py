# -*- encoding:utf-8 -*-
"""
@Time   :   2020/6/24 10:35 
@Author :   yanyu
@Email  :   973900834@qq.com
@Project:   
@Description    :   
"""
from flask import Blueprint
system=Blueprint('system',__name__,url_prefix='/sys')
from  . import views,errors