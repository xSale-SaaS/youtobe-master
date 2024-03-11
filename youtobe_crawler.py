# youtobe 找达人方法
# 1. 先通过搜索框搜对应的类目 比如https://www.youtube.com/results?search_query=smartphone+review 搜索智能手机测评的
# 2. 进入达人主页 https://www.youtube.com/@Mrwhosetheboss
# 3. 点击达人主页中的简介 查看信息
import requests
from bs4 import BeautifulSoup
import re
import json
import jsonpath
from youtubesearchpython import VideosSearch
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    # 'Cookie':'VISITOR_PRIVACY_METADATA=CgJVUxIEGgAgJw%3D%3D; __Secure-3PAPISID=mMGfGplRnaGT-Vsx/A0JQFTzXE6I3XYHvG; __Secure-3PSID=eQiajaYRICdTLPSGJwgppNwX8ohh6KsVfPlkDN1BsP8NbOd9Ljd55NkVq2EMNXCkrN0QWA.; LOGIN_INFO=AFmmF2swRgIhAJvtj68R9QzS1EcXgE0CBK5_kNHTacdwo7eljB14o6UXAiEA_ae_nNYrW3x7JVQopGynDXvdzH3E7IWXwZLFf7moBDY:QUQ3MjNmd1J6SGdmYTdUTHNZTlNtbDN5b2J0VHV5cHZNS0FpS1RqdnN1cUlHUW5DQjEtVmxLVXBEXzI4X2N5OFJaVmV1cWM0UXowczBCaGx1TTRpcnV5NktnZmktZkN6WGNTamtPbllsTEZISWJJZWE2VkprMHpBRWtueDF2Yks3emZGa254dUhxMUZBaUE2TGZpcGZDN3F1OFRMVklIOTJB; VISITOR_PRIVACY_METADATA=CgJVUxIEGgAgJw%3D%3D; VISITOR_INFO1_LIVE=SG1Jnd3yYro; YSC=nbpZ8fCoJRg; PREF=f7=100&tz=Asia.Shanghai&f4=4000000; __Secure-1PSIDTS=sidts-CjEBYfD7ZyDR8Km-m3vzan4Y6U9seN3M1h4V22yT35_BaOZBY0I-GMyyi3rkjFkEkNFSEAA; __Secure-3PSIDTS=sidts-CjEBYfD7ZyDR8Km-m3vzan4Y6U9seN3M1h4V22yT35_BaOZBY0I-GMyyi3rkjFkEkNFSEAA; __Secure-3PSIDCC=AKEyXzVf0ClXOUlFawVu5ZnylW3S4MDG9hmmyOG2C5anOtIn54j0iloxdxKnXxs0zjYVXlrhEw'
}
person_info_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'X-Client-Data': 'CI62yQEIpbbJAQipncoBCO7/ygEIkqHLAQiGoM0BCN3uzQEItvfNAQjY/80BGOzTzQEYyvjNAQ=='
}

# 找到所有的 <script> 标签
# 定义正则表达式模式
pattern = r'<script.*?>(.*?)</script>'

# category 品类 smartphone+review
"""
:param category: 达人分类
:return:达人主页path数组
"""
def get_person_list(category):
    # 匹配JSON数据部分
    url_list = []
    videosSearch = VideosSearch(category, limit=10)
    while len(url_list) < 50:
        for video in videosSearch.result()['result']:
            url = video['channel']['link']
            if url not in url_list:
                url_list.append(url)
        videosSearch.next()

    # search_result_con = requests.post(list_url_continue,json = json.dumps(body), headers=headers,)
    # print(search_result_con)
    return list(set(url_list))


"""
:param path 达人主页的path
:return json key:'title' 'intro' 'videoCount' 'outsideChainList' 'subscriberCount'
"""
def get_person_info(path):
    # home_page_url = f'https://www.youtube.com{path}'
    home_page = requests.get(path, headers=person_info_headers)
    person_info_dict = {}
    soup = BeautifulSoup(home_page.text, "html.parser")
    # 提取 script 标签中的 var 的正则
    var_pattern = re.compile(r"var (.*?) =(.*?);$", re.MULTILINE | re.DOTALL)
    # 提取 script 标签中的（function（））中的ytcfg.set（）的正则
    json_pattern = re.compile(r'ytcfg.set\((.*?)\);', re.MULTILINE | re.DOTALL)
    # 取出所有 script 标签
    var_scripts = soup.find('script', string=var_pattern)
    json_scripts = soup.findAll('script', string=json_pattern)
    #遍历 script取出 地区国家数据
    for json_script_content in json_scripts:
        for item in json_script_content:
            if item and item.startswith('(function()'):
                data_str = json_pattern.search(item).group(1)
                try:
                    data_json = json.loads(data_str,strict=False)
                    if data_json:
                        # 获取达人国家
                        obj = jsonpath.jsonpath(data_json, '$..contentRegion')[0]
                        person_info_dict['contentRegion'] = obj
                except Exception as e:
                    print("抓取地址出错")
    # 遍历 script 取出其他数据
    for script_content in var_scripts:
        data_str = var_pattern.search(script_content).group(2)
        try:
            data_json = json.loads(data_str, strict=False)
            # print(f"------data-json-{data_json}--")
            if data_json:
                # 订阅数
                obj = jsonpath.jsonpath(data_json,'$..subscriberCountText')[0]
                subscriberCountString = obj['simpleText']
                person_info_dict['subscriberCount'] = subscriberCountString
                # 外链
                obj = jsonpath.jsonpath(data_json,'$..channelVideoPlayerRenderer')[0]
                url_list = list(map(lambda x: x['text'],obj['description']['runs']))
                url_pattern = re.compile(r'^(?:http|ftp)s?://',re.IGNORECASE)
                new_list = []
                for url in url_list:
                    if url_pattern.match(url) is not None:
                        new_list.append(url)
                person_info_dict['outsideChainList'] = new_list
                # 名字和简介
                obj = jsonpath.jsonpath(data_json,'$..metadata')[0]
                intro = obj['channelMetadataRenderer']['description']
                title = obj['channelMetadataRenderer']['title']
                person_info_dict['intro'] = intro
                person_info_dict['title'] = title
                # 视频数量
                obj = jsonpath.jsonpath(data_json,'$..viewCountText')[0]
                video_count = obj['simpleText']
                person_info_dict['videoCount'] = video_count
        except Exception as e:
            print("An error occurred:", e)
    return person_info_dict


if __name__ == '__main__':
    #所有的category,['电影和动画','汽车和交通工具','音乐','宠物与动物','体育','旅行和活动','游戏','人和博客','喜剧','娱乐','新闻和政治','操作方法和风格','教育','科学技术','非营利组织和行动主义']
    youtube_categories = ['Film&Animation', 'Autos&Vehicles', 'Music', 'Pets&Animals', 'Sports', 'Travel&Events',
                          'Gaming', 'People&Blogs', 'Comedy', 'Entertainment', 'News+and+Politics', 'Howto&Style', 'Education', 'Science&Technology', 'Nonprofits&Activism']
    # 参数 两个单词中间+号隔开
    person_url_list = get_person_list('smartphone+review')
    for person_url in person_url_list:
        person_info_dict = get_person_info(person_url)
        print(person_info_dict)
