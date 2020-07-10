import gevent
import gevent.monkey
gevent.monkey.patch_all()
import os
import csv
import requests
import time
from lxml import html
etree = html.etree


def upload(filename,j):
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
                   "lastModifiedDate": "Sat Feb 15 2020 14:37:20 GMT+0800 (中国标准时间)",
                   "size": "343706"}

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
    if response.json().get('result'):
        while True:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'text/plain, */*; q=0.01',
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

            data = {
                'tasktag': response.json().get('keytag'),
                'phonenumber': '',
                'loginkey': '',
                'limituse': '1'
            }

            response = requests.post('https://app.xunjiepdf.com/api/Progress', headers=headers, data=data)
            data = response.json()
            if data.get('message') == '处理成功':
                j.append(data.get('txtconent'))
                return j
            elif data.get('message') == '处理失败':
                
            else:
                print(data.get('message'))
                time.sleep(1)

def readCSV(filename):
    res = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            res.append(row)
    return res

def walkFile(file):
    res = []
    for root, dirs, files in os.walk(file):
        for f in files:
            res.append(f)
    return res

def download(name,url):
    if not os.path.exists('guowai_audios/'+name):
        if len(url) >5:
            try:
                r = requests.get(url,timeout=600000)
                with open('guowai_audios/'+ name, "wb") as code:
                    code.write(r.content)
            except Exception as e:
                print(e)
                print(name,url)

        else:
            print('---------------------',name,url)

def transfor():
    bookName = 'guowai'
    filesPath = walkFile(bookName)
    for filePath in filesPath:
        csvData = readCSV(bookName+'/'+filePath)
        downloadJoinall = []
        #下载音频
        for j in csvData[1:len(csvData)]:
            name = f'{j[0]}-{j[1]}-{j[2]}-{j[3]}.mp3'.replace('/','')
            downloadJoinall.append(gevent.spawn(download,name,j[6]))
        gevent.joinall(downloadJoinall)
        #新建csv
        f = open('overseasInfo/' + filePath, 'w', encoding='utf_8_sig', newline='')
        csv_writer = csv.writer(f)
        csv_writer.writerow(["地区", "城市", "景区名称", "景点名称", "景点经度", "景点纬度", "景点音频", "景点图片","景点描述"])
        #音频转换
        g_list = list()
        for j in csvData[1:len(csvData)]:
            name = f'{j[0]}-{j[1]}-{j[2]}-{j[3]}.mp3'.replace('/', '')
            g = gevent.spawn(upload,'guowai_audios/' + name,j)
            g_list.append(g)
        gevent.joinall(g_list,count=5)
        for g in g_list:
            print(g.value)
            csv_writer.writerow(g.value)

if __name__ == '__main__':
 transfor()