from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import  settings
import configparser

import sys
sys.path.append("..")
from redis_conf import RedisDB 

import time
content = {'domain':settings.STATIC_ROOT}

#首页
def index(request,template='index.html'):
    day = time.strftime("%Y-%m-%d", time.localtime())
    ecs = RedisDB().getConnect().keys("ecs_"+day+"*")
    slb = RedisDB().getConnect().keys("slb_"+day+"*")
    content['ecs_num'] =  len(ecs)
    content['slb_num'] =  len(slb)
    content['type'] = 'no'
    return render_to_response(template,content)

'''列表'''
def ecs(request,template='ecs_list.html'):
    type = request.GET.get('type','ecs')
    day = time.strftime("%Y-%m-%d", time.localtime())
    ecs = RedisDB().getConnect().keys(type+"_"+day+"_*")
    res = []
    for i in ecs:
        len = RedisDB().getConnect().hlen(i)
        res.append( {'ip':i,'num':len,'ii':i.replace('ecs_'+day,'') } )
    content['res']  = res
    content['type'] = type
    content['day']  = day
    return render_to_response(template,content)

'''详情'''
def ecs_port(request,template='ecs_detail.html'):
    type = request.GET.get('type','ecs')
    ip =  request.GET.get('ip')
    real = ip.split('_').pop()
    res = RedisDB().getConnect().hgetall(ip)
    day = time.strftime("%Y-%m-%d", time.localtime())
    content['res'] = res
    content['type'] = type
    content['ip'] = real
    content['day'] = day
    return render_to_response(template,content)