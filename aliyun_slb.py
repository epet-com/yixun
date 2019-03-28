'''
aliyun python sdk
date:2019-03-11
'''
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json


'''
    获取阿里云账号中所有的SLB的ip和id
    备注：如果地域不是华东1，需要调整 cn-hangzhou
'''
def getAliyunSlbIp(type='ip',account='',passkey='',endpoint=''):
    client = AcsClient(account, passkey, endpoint)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('slb.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2014-05-15')
    request.set_action_name('DescribeLoadBalancers')
    request.add_query_param('PageSize', '100')

    response = client.do_action(request)
    res = json.loads(str(response,encoding='utf-8'))
    ip = []
    ids = []
    for i in res['LoadBalancers']['LoadBalancer']:
        ip.append(i['Address'])
        ids.append(i['LoadBalancerId'])

    if type=='ip':
        return ip
    else:
        return ids

'''
    获取阿里云slb的ip和监听端口
'''
def getAliyunSlbIpPort(ids,account='',passkey='',endpoint=''):
    client = AcsClient(account, passkey, endpoint)
    for id in ids:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('slb.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https') # https | http
        request.set_version('2014-05-15')
        request.set_action_name('DescribeLoadBalancerAttribute')
        request.add_query_param('LoadBalancerId', id)
        response = client.do_action(request)
        res = json.loads(str(response, encoding = 'utf-8'))

    return res



'''获取slb后端ecs的id和开放port'''
def getEcsIdAndPort(client,slbid):
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('slb.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2014-05-15')
    request.set_action_name('DescribeHealthStatus')

    request.add_query_param('RegionId', 'cn-hangzhou')
    request.add_query_param('LoadBalancerId',slbid) 
    response = client.do_action(request)
    res = json.loads( str(response,encoding='utf-8') )
    return res['BackendServers']['BackendServer']
