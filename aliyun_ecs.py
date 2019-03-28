'''
aliyun python sdk
date:2019-03-11
'''
from aliyunsdkcore.client  import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
'''
    获取阿里云账号中所有的ECS
    备注：如果地域不是华东1，需要调整 cn-hangzhou
'''

def getAliyunEcsIp(cate='ip',account='',passkey='',endpoint=''):
    client = AcsClient(account, passkey, endpoint)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('ecs.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https') # https | http
    request.set_version('2014-05-26')
    request.set_action_name('DescribeInstances')
    # request.add_query_param('RegionId', 'cn-hangzhou')
    request.add_query_param('PageSize', '100')  # 返回数量
    request.add_query_param('Status', 'Running') # ECS状态:运行中 

    response = client.do_action(request)
    res = json.loads(str(response,encoding='utf-8'))
    ipArr = []
    ips = {}
    for  i  in res['Instances']['Instance']:
            # ECS的ip有两种： 公网ip 和 弹性ip
            if len(i['EipAddress']['IpAddress']) !=0:
                ipArr.append(i['EipAddress']['IpAddress'])
                ips[ i['InstanceId'] ] =  i['EipAddress']['IpAddress']

            if len(i['PublicIpAddress']['IpAddress']) !=0 :
                ipArr.append(i['PublicIpAddress']['IpAddress'][0])
                ips[ i['InstanceId'] ] =  i['PublicIpAddress']['IpAddress'][0]

    if cate=='ip':
        return ipArr
    else:
        return ips

'''
    获取阿里云账号中所有的ECS的ip和id的映射字典
    备注：如果地域不是华东1，需要调整 cn-hangzhou
'''
def getAliyunEcsIpAndId(type,account,passkey,endpoint):
    return getAliyunEcsIp('ipandid',account,passkey,endpoint)