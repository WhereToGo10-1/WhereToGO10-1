import requests
address = '北京市海淀区交大东路18号院2号楼'
url= 'http://api.map.baidu.com/geocoder?output=json&key=Q8WAb6s5IunRGZflWX4U8oxu9zE9WeGe&address='+str(address)
response = requests.get(url)
answer = response.json()
lon = float(answer['result']['location']['lng'])
lat = float(answer['result']['location']['lat'])
print('经度：%.2f'%lon)
print('纬度: %.2f'%lat)