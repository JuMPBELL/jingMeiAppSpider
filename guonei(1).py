import os

import urllib3
urllib3.disable_warnings()
import requests
import csv
from requests.adapters import HTTPAdapter
import time
from lxml import html
etree = html.etree

def upload(filename):
    session = requests.session()
    resp = session.get('https://app.xunjiepdf.com/voice2text/')
    root = etree.HTML(resp.text)
    temptag = root.xpath('//*[@id="usertemptag"]/@value')[0]
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://app.xunjiepdf.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://app.xunjiepdf.com/voice2text/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    response = session.post('https://app.xunjiepdf.com/api/producetoken', headers=headers, data={'machineid': temptag})
    token = response.json().get('token')
    guid = response.json().get('guid')

    url = "https://app.xunjiepdf.com/api/Upload"
    querystring = {"tasktype": "voice2text", "phonenumber": "", "loginkey": "",
                   "machineid": temptag, "token": token,
                   "limitsize": "20480", "pdfname": filename,
                   "queuekey": guid, "uploadtime": "", "filecount": "1", "fileindex": "1",
                   "pagerange": "", "picturequality": "", "outputfileextension": "", "picturerotate": "0",
                   "filesequence": "0", "filepwd": "", "iconsize": "", "picturetoonepdf": "", "isshare": "0",
                   "softname": "pdfonlineconverter", "softversion": "V5.0", "validpagescount": "20", "limituse": "1",
                   "filespwdlist": "", "fileCountwater": "1", "languagefrom": "zh-CHS", "languageto": "",
                   "cadverchose": "",
                   "pictureforecolor": "", "picturebackcolor": "", "id": "WU_FILE_1",
                   "name": filename, "type": "audio/mp3",
                   "lastModifiedDate": "Tue Feb 11 2020 19:05:16 GMT+0800 (中国标准时间)", "size": "232006"}

    headers = {
        'connection': "keep-alive",
        'content-length': "232006",
        'sec-fetch-dest': "empty",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
        'content-type': "audio/mp3",
        'accept': "*/*",
        'origin': "https://app.xunjiepdf.com",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'referer': "https://app.xunjiepdf.com/voice2text/",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
        'cache-control': "no-cache",
    }
    with open(filename, 'rb') as f:
        data = f.read()
    response = requests.request("POST", url, headers=headers, params=querystring, data=data)

    print(response.text)
    return getText(tasktag=response.json().get('keytag'))

def getText(tasktag):
    data = {
        'tasktag': tasktag
    }
    for i in range(20):
        response = requests.post('https://app.xunjiepdf.com/api/Progress', data=data)
        print(response.text)
        response = response.json().get('txtconent')
        if response:
            return response
        else:
            time.sleep(1)


session = requests.session()
session.mount('http://', HTTPAdapter(max_retries=15))
session.mount('https://', HTTPAdapter(max_retries=15))

def download(url):
    if not os.path.exists('audios/'+url.split('/')[-1]):
        r = session.get(url,timeout=10)
        with open('audios/'+url.split('/')[-1], "wb") as code:
            code.write(r.content)

guonei_city = session.get('https://api.gowithtommy.com/rest/miniapp/city/list/?country_id=40',verify = False,timeout=10)#请求国内城市列表
guonei_city = guonei_city.json()

for i in guonei_city.get('data'):
    res_data = []
    f = open('file/'+i.get('name')+'.csv', 'w', encoding='utf_8_sig')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["地区", "城市", "景区名称", "景点名称", "景点经度", "景点纬度", "景点描述", "景点图片"])

    url = 'https://api.gowithtommy.com/rest/miniapp/scene/list/?city_id='+str(i.get('id'))
    jinqu_list = session.get(url , verify = False).json().get('data')
    print(jinqu_list)
    for j in jinqu_list:
        url = 'https://api.gowithtommy.com/rest/miniapp/sub_scene/list/?scene_id='+str(j.get('id'))
        audio_url = j.get('audios')[0].get('audio')
        csv_writer.writerow([j.get('country_name'),
                             j.get('city_name'),
                             j.get('name'),
                             '',
                             j.get('longitude'),
                             j.get('latitude'),
                             url.split('/')[-1],
                             j.get('images')[0].get('image')])
        jingdian_info = session.get(url , verify = False).json().get('data')
        for z in jingdian_info:
            print(z)
            if z.get('audios'):
                url = z.get('audios')[0].get('audio')
                # download(url)
                # text = upload('audios/'+url.split('/')[-1])
                csv_writer.writerow([z.get('country_name'),
                                     z.get('city_name'),
                                     z.get('scene_data').get('name'),
                                     z.get('name'),
                                     z.get('longitude'),
                                     z.get('latitude'),
                                     url.split('/')[-1],
                                     z.get('image')])
            else:
                csv_writer.writerow([z.get('country_name'),
                                    z.get('city_name'),
                                    z.get('scene_data').get('name'),
                                    z.get('name'),
                                    z.get('longitude'),
                                    z.get('latitude'), '',z.get('image')])
