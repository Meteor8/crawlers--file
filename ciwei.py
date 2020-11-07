import requests
from lxml import etree
import json

DEBUG = 0
i = 0

ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
headers = {
    'User-agent': ua
}

def get_content():
    t_url = "http://ciweiyuedui.q.hao.ac:8062/lyrics/"
    with requests.Session() as session:
        response = session.get(t_url, headers=headers)
        text = response.text
        t_html = etree.HTML(text)
        if DEBUG: print('所有歌曲',t_html)
    return t_html

def get_songList(t_html):
    t_songUrl = t_html.xpath("//div[@id='lyrics_container']/div/a[1]/@href")
    #数组中，把id逐个分割获取
    t_songsUrl = [url for url in t_songUrl]       
    if DEBUG: print('所有url',t_songsUrl)
    return t_songsUrl

def get_infoHtml(t_url):
    t_songUrl = "http://ciweiyuedui.q.hao.ac:8062" + t_url
    with requests.Session() as session:
        response = session.get(t_songUrl, headers=headers)
        text = response.text
        t_html = etree.HTML(text)
    return t_html

#获取歌名、id、歌词
def get_info(t_html, t_songUrl):
    global i
    #119/nothing-means-but-only-music/nothing-means-but-music/ 页面丢失
    try:
        t_songId = int(t_html.xpath("//td[2]/a[2]/@track_id")[0])
        t_songCnName = t_html.xpath("//b[@class='songSubTitle']/text()")[0]
        t_songEnName = t_songUrl.split("/")[-2].replace("-", ' ').title()
        t_songName = t_songCnName + '[' + t_songEnName + ']'
    except:
        t_songId = -999
        t_songName = "NOT FOUND"
    print(t_songId, t_songName)
    return t_songId, t_songName
    '''
    t_songLyrics = t_html.xpath("//pre")
    try:
        for pre in t_songLyrics:
            i += 1
            if DEBUG: print(i, pre.text[0:10])
            with open(str(i)+".txt", 'w+') as f:
                f.write(pre.text)
    except:
        i += 1
        print(i, "NONE")
    '''
    

def get_downloadData(t_url, t_id):
    myurl = "http://ciweiyuedui.q.hao.ac:8062/music/ajaxinfo/"

    myheaders = {
        "accept": '*/*',
        "accept-encoding" :'gzip, deflate',
        "Connection": "keep-alive",
        "accept-language": "zh-CN,zh;q=0.6",
        "content-length": "26",
        "content-type": 'application/x-www-form-urlencoded; charset=UTF-8',
        "cookie": "",
        "Host": "ciweiyuedui.q.hao.ac:8062",
        "Origin": "http://ciweiyuedui.q.hao.ac:8062",
        "Referer": "http://ciweiyuedui.q.hao.ac:8062"+t_url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

    }

    mydata = {
        "music_id": t_id,
        "map_ids": t_id
    }
    myresponse = requests.post(myurl, data=mydata, headers=myheaders)
    return myresponse.text

def cook_data(t_data):
    t_cookData = json.loads(t_data)
    t_url = t_cookData[0]['file']
    return t_url


def download_song(t_url, t_name, t_id):
    t_requestData = get_downloadData(t_url, t_id)
    t_songUrl = cook_data(t_requestData)
    if t_songUrl[-3:] != "mp3":
        t_songUrl = "http://ciweiyuedui.q.hao.ac:8062/data/ump3s" + t_url[:-1] + ".mp3"
    #特殊处理
    if t_id == 1534: #火车
        t_songUrl = "http://ciweiyuedui.q.hao.ac:8062/data/ump3s/sound-of-life-towards/201712/2711243573__master_rev05.mp3"
    elif t_id == 1537: #盼暖春来
        t_songUrl = "http://ciweiyuedui.q.hao.ac:8062/download/music/2018_LP/masterd/0412cfm/%E7%9B%BC%E6%9A%96%E6%98%A5_master_2448_rev05.mp3"
    elif t_id == 1535:
        t_songUrl = "http://ciweiyuedui.q.hao.ac:8062/data/ump3s/sound-of-life-towards/201801/1815224166__master_rev03_16441.mp3"
    print(str(t_songUrl))
    
    with requests.Session() as session:
        try:
            response = session.get(t_songUrl, headers=headers)
            with open(t_name+".mp3", 'wb+') as f:
                    f.write(response.content)
            print('下载成功')
        except:
            print("下载失败")
    

def main():
    global i
    contentHtml = get_content()
    songList = get_songList(contentHtml)
    #songList = ["/sounds-of-life-towards/opium/"]
    for songUrl in songList:
        i += 1
        print("=======")
        print(i, songUrl)
        infoHtml = get_infoHtml(songUrl)
        songId, songName = get_info(infoHtml, songUrl)
        download_song(songUrl, songName, songId)

        
main()
