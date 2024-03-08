# youtobe-master

脚本 Python 版本

Python3.10

#### 安装三方库 

```
pip3 install  requests bs4 re json jsonpath
```

 #### 调用方法

根据参数  类目 搜索达人 返回达人主页 path 数组 

```
get_person_list('smartphone+review')
```

根据达人主页 path 进入主页获取信息 返回 json key:'title' 'intro' 'videoCount' 'outsideChainList' 'subscriberCount'

```
get_person_info(person_path)
```