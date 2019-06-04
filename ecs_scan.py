from aliyun_ecs import getAliyunEcsIp
from redis_conf import RedisDB
import nmap,os,json,time,configparser

class PortScan():
    def __init__(self,account,passkey,endpoint,name,nscan):
        # ecs_ip = getAliyunEcsIp('ip',account,passkey,endpoint)
        ecs_ip = ['192.168.0.19','192.168.0.212','192.168.0.222']
        self.port_scan(ecs_ip,'ecs',name,nscan)

    def port_scan(self,ip,type,name,nscan):
        day   = time.strftime("%Y-%m-%d",time.localtime())
        num = 0  
        for k in ip:
            num = num+1 
            print('=============================' )
            print('开始扫描第 '+str(num)+' 台ECS:' )

            dirname = IMG_DIR+'/'+name+'_masscan_'+day
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            '''masscan全端口扫描'''
            cmd = 'masscan '+k+' -p0-65535 -oJ '+dirname+'/masscan_' + k+'.txt --rate 1000'
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
        with open(filepath, 'r') as f:
            res = f.readlines()
        return res


if __name__ == '__main__':
    start = time.time()
    config = configparser.ConfigParser()
    config.read(os.getcwd()+'/config.ini',encoding='utf-8')
    IMG_DIR = config.get('img_dir','dirname')
   
    aliyun_ak_num = int(config.get('aliyun_ak_num','num'))
    nscan = nmap.PortScanner()
    for  i in range(aliyun_ak_num):
        i = str(i+1)
        account  = config.get('aliyun_ak','account_' +i)
        passkey  = config.get('aliyun_ak','passkey_' +i)
        endpoint = config.get('aliyun_ak','endpoint_'+i)
        name     = config.get('aliyun_ak','name_'+i)
        if account=='' or  passkey == '' or endpoint =='' or name=='':
            print('account_'+i+'|passkey_'+i+'|endpoint_'+i+'|name_'+i+'不能为空')
            exit(0)
        PortScan(account,passkey,endpoint,name,nscan)
    cost = round(time.time() - start,2)
    print('扫描共花费:'+str(cost) + ' s')