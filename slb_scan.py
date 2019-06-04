from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from aliyun_slb import *
from aliyun_ecs import *
from aliyunsdkcore.client  import AcsClient
from aliyunsdkcore.request import CommonRequest
import time,os,requests,platform,configparser
from redis_conf  import RedisDB

config = configparser.ConfigParser()
config.read(os.getcwd()+'/config.ini','utf-8')
IMG_DIR = config.get('img_dir','dirname')
TIMEOUT = config.get('timeout','selenium_timeout')

if __name__ == '__main__':
	print('-----------------------数据开始处理----------------------------')
	print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
	start = time.time()
	ecs_ip = []
	aliyun_ak_num = int(config.get('aliyun_ak_num','num'))

	for  ai in range(aliyun_ak_num):
		ai = str(ai+1)
		account  = config.get('aliyun_ak','account_'+ai)
		passkey  = config.get('aliyun_ak','passkey_'+ai)
		endpoint = config.get('aliyun_ak','endpoint_'+ai)
		name     = config.get('aliyun_ak','name_'+ai)

		slbids = []
		slbids = getAliyunSlbIp('id',account,passkey,endpoint)

		if len(slbids) == 0:
			print('账号：'+name+'SLB数量为0')
			exit()

		#先清空
		client = AcsClient(account,passkey,endpoint)

		'''获取ecs的ip和id映射关系 '''
		ecsipandid = getAliyunEcsIpAndId('ipandid',account,passkey,endpoint)
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'获取ecs的ip和id映射关系 完成')

		dirname = IMG_DIR 

		date =  time.strftime('%Y-%m-%d',time.localtime())
		host = []
		for slbid in slbids:
			#通过slb的id 获取后端的ecs(id+port)
			res = getEcsIdAndPort(client,slbid) 
			for i in res:
				'''检查状态为正常且端口不为443'''
				if i['ServerHealthStatus'] == 'normal' and str(i['Port'])!='443':
					#通过ecs的id获取到ip
					ecsip =  ecsipandid[ i['ServerId'] ]
					url = 'http://'+ ecsip +':'+ str(i['Port'])
					host.append( url )
				else:
					'''后端ecs的状态异常'''
					print('ecs_id:'+i['ServerId']+'is '+i['ServerHealthStatus'])

		#去重
		host  = list(set(host))
		dirpath = IMG_DIR+'/'+name+'_images_'+date
		if not os.path.exists(dirpath):
			os.mkdir(dirpath)

	if len(host) > 0:
		chrome_option = Options()
		chrome_option.add_argument('--headless')
		chrome_option.add_argument('--no-sandbox')
		driver = webdriver.Chrome(chrome_options=chrome_option)
		driver.set_page_load_timeout(TIMEOUT)
		for i in host:
			try:
				driver.get(i)
				ss = i.replace('http://','').replace('/','_').replace(':','_')
				sh = i.replace('http://','').split(':')[0]
				filename = dirpath+'/'+ss+'.png'
				driver.get_screenshot_as_file( filename )
				print(filename+' 已生成')
				RedisDB().getConnect().lpush('getAliyunEcs',i)
				RedisDB().getConnect().hset('slb_'+date+'_ecs_'+sh,i,ss+'.png')
			except TimeoutException:
				print(i+' 页面超时');
				continue
		driver.quit()

	end = time.time()
	print('扫描共耗时'+str(round(end-start,2))+' s')