from aliyun_ecs import getAliyunEcsIp
from redis_conf import RedisDB
import nmap,os,json,time,platform,requests,configparser

class PortScan():
    def __init__(self,account,passkey,endpoint,name):
        

        self.port_scan(ecs_ip,'ecs',name)

    def port_scan(self,ip,type,name):
        day = time.strftime("%Y-%m-%d",time.localtime())
        nscan = nmap.PortScanner()
        num = 0  
        for k in ip:
            num = num+1 
            print('=============================' )
            print('开始扫描第 '+str(num)+' 台ecs:' )
            '''判断主机的存活性'''
            if platform.system() == 'Linux':
                '''linux'''
                cmd = 'ping -c 4 '+k
                rate = '2000' #发包速率
            else:
                '''window'''
                cmd = 'ping '+k
                rate = '1000' #发包速率


            print('-检查ecs存活状态:'+cmd)
            res= os.system(cmd)
            if res !=0:
                #ping不通，有可能是没有开启icmp协议，其他端口有可能是开启的
                print('-账号：'+name+' 主机:'+k+' is not alive')
            else:
                print('-账号：'+name+' 主机:'+k+' is alive')

            dirname = IMG_DIR+'/'+name+'_masscan_'+day
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            '''masscan全端口扫描'''
            cmd = 'masscan ' + k + ' -p0-65535 -oJ '+dirname+'/masscan_' + k+'.txt --rate '+rate
            try:
                print('-开始对主机 '+k+' 进行masscan进行扫描:'+cmd)
                res = os.system(cmd)
            except Exception as e:
                print(e)

            if res == 0:
                print('-主机：'+k + ' masscan is over')
                # 如果执行完成,开始读取文件内容
                masscan_res = self.readFile(dirname+'/masscan_' + k+'.txt')
                if len(masscan_res) == 0:
                    print("-masscan_"+k+'_'+day+' scan result is empty!')
                    continue

                for kk in masscan_res:
                    if 'finish' in kk: #扫描结束标志
                        break;
                    ii = kk.replace(" ", "").replace("\n", "").strip(",").replace('"', '').replace("{", '{"').replace(
                        "}", '"}').replace(",", '","').replace(":", '":"')
                    ii = ii.replace('"[{', '[{').replace('}]"', '}]')
                    res = json.loads(ii)
                    if str(res['ports'][0]['port']) == '443':    #443端口直接跳过
                        continue
                    portStats = self.nampScan(nscan, res['ip'], res['ports'][0]['port'],day,type)
                    if portStats == False:
                        print('-namp scan port is error')
                    else:
                        print('-nmap scan is over')
            else:
                print('-主机：'+k+'masscan is fail')

    def nampScan(self, nscan, ip, port,day,type):
        result = nscan.scan(ip, port)
        if result['scan']:
            con = result['scan'][str(ip)]['tcp'][int(port)]
            s = '-ip:'+ip+' port:'+port+' product:' + con['product'] + ' name:' + con['name'] + ' version:' + con['version'] + ' state:' + con[
                'state']
            print(s)
            if con['state'] == 'open':
                '''redis 写库操作'''
                if con['product']:  
                    soft = con['product']
                else:
                    soft = 'not know'
                if con['name']:
                    service = con['name']
                else:
                    service = 'not know'
                if con['version']:
                    version = con['version']
                else:
                    version = 'not know'
                RedisDB().getConnect().hset(type+'_'+day+"_"+ip,port,'soft:'+soft+'-------service:'+service+'-------version:'+version)
                return con
        else:
            print('-'+port+' nmap not found info')
            return False

    def readFile(self, filepath):
        with open( filepath, 'r') as f:
            res = f.readlines()
        return res


if __name__ == '__main__':
    start = time.time()
    config = configparser.ConfigParser()
    config.read(os.getcwd()+'/config.ini',encoding='utf-8')
    IMG_DIR = config.get('img_dir','dirname')
    TEST_ECS_IP = config.get('test_ecs','ip')
    TEST_SLB_ID = config.get('test_slb','id')

    ecs_ip = []
    if len( TEST_ECS_IP ) == 0:
        #如果是正式环境
        ecs_ip = getAliyunEcsIp(account,passkey,endpoint) 
        if len(ecs_ip) == 0:
            print('ECS数量为0')
            exit(0)
        aliyun_ak_num = int(config.get('aliyun_ak_num','num'))
        for  i in range(1,aliyun_ak_num+1):
            i = str(i)
            account = config.get('aliyun_ak','account_'+i)
            passkey = config.get('aliyun_ak','passkey_'+i)
            endpoint = config.get('aliyun_ak','endpoint_'+i)
            name   = config.get('aliyun_ak','name_'+i)
            if account=='' or  passkey == '' or endpoint =='' or name=='':
                print('account_'+i+'|passkey_'+i+'|endpoint_'+i+'|name_'+i+'不能为空')
                exit(0)
            PortScan(account,passkey,endpoint,name)
    else:
        #如果是测试环境
        ecs_ip.append(TEST_ECS_IP)
        PortScan(account='',passkey='',endpoint='',name='')

    

    cost = round(time.time() - start,2)
    print('扫描共花费:'+str(cost) + ' s')