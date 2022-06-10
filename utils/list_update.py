#!/usr/bin/env python3

import json
from calendar import month
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter

# 文件路径定义
sub_list_json = './sub/sub_list.json'


with open(sub_list_json, 'r', encoding='utf-8') as f:  # 载入订阅链接
    raw_list = json.load(f)
    f.close()


def check_url(url):  # 判断远程远程链接是否已经更新
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    try:
        resp = s.get(url, timeout=2)
        status = resp.status_code
    except Exception:
        status = 404
    if status == 200:
        isAccessable = True
    else:
        isAccessable = False
    return isAccessable


class update_url():

    def update_main(update_enable_list=[0, 21, 25, 37, 43]):
        if len(update_enable_list) > 0:
            for id in update_enable_list:
                status = update_url.update(id)
                update_url.update_write(id, status[1], status[1])
            updated_list = json.dumps(
                raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(sub_list_json, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()
        else:
            print('Don\'t need to be updated.')

    def update_write(id, status, updated_url):
        if status == 404:
            print(f'Id {id} URL 无可用更新\n')
        else:
            if updated_url != raw_list[id]['url']:
                raw_list[id]['url'] = updated_url
                print(f'Id {id} URL 更新至 : {updated_url}\n')
            else:
                print(f'Id {id} URL 无可用更新\n')

    def update(id):
        if id == 0:
            # remarks: pojiezhiyuanjun/freev2, 将原链接更新至 https://raw.fastgit.org/pojiezhiyuanjun/freev2/master/%MM%(DD - 1).txt
            # yesterday = (datetime.today() + timedelta(-1)).strftime('%m%d')
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            yesterday = (datetime.today() + timedelta(-1)).strftime('%m%d')
            front_url = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/'
            end_url = 'clash.yml'
            # 修改字符串中的某一位字符 https://www.zhihu.com/question/31800070/answer/53345749
            url_update = front_url + yesterday + end_url
            if check_url(url_update):
                return [0, url_update]
            else:
                return [0, 404]
        elif id == 21:
            # remarks: v2raydy/v2ray, 将原链接更新至 https://https://raw.githubusercontent.com/v2raydy/v2ray/main/%MM-%(DD - 1)%str%1.txt
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            yesterday = (datetime.today() + timedelta(-1)).strftime('%m-%d')

            front_url = 'https://raw.githubusercontent.com/v2raydy/v2ray/main/'
            end_url = '1.txt'
            for ch in 'abcdefghijklmnopqrstuvwxy':
                # 修改字符串中的某一位字符 https://www.zhihu.com/question/31800070/answer/53345749
                url_update = front_url + yesterday + ch + end_url
                if check_url(url_update):
                    return [21, url_update]
                else:
                    return [21, 404]
        elif id == 43:
            # remarks: v2raydy/v2ray, 将原链接更新至 https://https://raw.githubusercontent.com/v2raydy/v2ray/main/%MM-%(DD - 1)%str%1.txt
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            yesterday = (datetime.today() + timedelta(-1)).strftime('%Y%m%d')
            month = (datetime.today() + timedelta(-1)).strftime('%Y%m') +'/'
            front_url = 'https://nodefree.org/dy/'
            end_url = '.txt'
            url_update = front_url + month + yesterday + end_url
            if check_url(url_update):
                return [43, url_update]
            else:
                return [43, 404]
        
        elif id == 25:
            # remarks: v2raydy/v2ray, 将原链接更新至 https://https://raw.githubusercontent.com/v2raydy/v2ray/main/%MM-%(DD - 1)%str%1.txt
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            yesterday = (datetime.today() + timedelta(-1)).strftime('%Y%m%d')
            month = (datetime.today() + timedelta(-1)).strftime('%Y%m') +'/'
            year = (datetime.today() + timedelta(-1)).strftime('%Y') +'/'
            front_url = 'https://v2rayshare.com/wp-content/uploads/'
            end_url = '.txt'
            url_update = front_url + year + month + yesterday + end_url
            if check_url(url_update):
                return [25, url_update]
            else:
                return [25, 404]
                
        elif id == 37:
            url_raw = 'https://raw.githubusercontent.com/Pawdroid/Free-servers/main/README.md'
            try:
                resp = requests.get(url_raw, timeout=2)
                resp_content = resp.content.decode('utf-8')
                resp_content = resp_content.split('\n')
                for line in resp_content:
                    if '本次节点订阅地址' in line:
                        line_split = line.split('：')
                        line_split = line_split[1].split('<')
                        url_update = line_split[0]
                        if check_url(url_update):
                            return [37, url_update]
                        else:
                            return [37, 404]
            except Exception as err:
                print(err)
                return [37, 404]


# if __name__ == '__main__':
#     update_url.update_main([0, 21, 43, 37])
