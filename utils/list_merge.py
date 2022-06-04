#!/usr/bin/env python3

# Python 之间互相调用文件https://blog.csdn.net/winycg/article/details/78512300
import json
from urllib import request

from list_update import update_url
from sub_convert import sub_convert

# 分析当前项目依赖 https://blog.csdn.net/lovedingd/article/details/102522094


# 文件路径定义
# readme = './README.md'
sub_list_json = './sub/sub_list.json'
sub_list_path = './sub/list/'


class sub_merge():
    # 将转换后的所有 Url 链接内容合并转换 YAML or Base64, ，并输出文件，输入订阅列表。
    def sub_merge(url_list):
        content_list_array = []
        for index in range(len(url_list)):
            # 出现三种情况，最复杂的为clash、base64、url三种格式的互相掺杂
            # 首先用|拆分，然后再进行转换，最后再合并
            url = url_list[index]['url']
            ids = url_list[index]['id']
            remarks = url_list[index]['remarks']
            content = sub_convert.get_node_from_sub(url)
            # try:
            if content == '':
                # disable_list(ids)
                print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                file = open(f'{sub_list_path}{ids:0>2d}.txt',
                            'w', encoding='utf-8')
                file.write(f'节点解析出错，请检查订阅链接：{ids} 是否正确')
                file.close()
            else:
                content_list_array.append(content)
                file = open(f'{sub_list_path}{ids:0>2d}.txt',
                            'w', encoding='utf-8')
                file.write(content)
                file.close()
                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')

        print('Merging nodes...\n')
        # https://python3-cookbook.readthedocs.io/zh_CN/latest/c02/p14_combine_and_concatenate_strings.html
        content_list = ''.join(content_list_array)
        # 去重
        content_array = content_list.split('\n')[:-1]
        content_array_deduplication = sub_convert.duplicate_removal(content_array)
        # 写入文件
        sub_convert.write_to_node(
            content_array_deduplication, './sub/node.txt')
        sub_convert.write_to_base64(
            content_array_deduplication, './sub/base64')
        sub_convert.write_to_clash(content_array_deduplication, './sub/clash/')
        print('Done!\n')

    def read_list(json_file):  # 将 sub_list.json Url 内容读取为列表
        with open(json_file, 'r', encoding='utf-8') as f:
            raw_list = json.load(f)
        enabled_list = []
        for index in range(len(raw_list)):
            if raw_list[index]['enabled']:
                enabled_list.append(raw_list[index])
        return enabled_list

    # def disable_list(list_id):
    #     with open(sub_list_json, 'w', encoding='utf-8') as f:
    #         raw_list = json.load(f)
    #         raw_list[list_id]['enabled'] = False
    #         f.write(raw_list)
    #         f.close()

    def geoip_update(url):
        print('Downloading Country.mmdb...')
        try:
            request.urlretrieve(url, './utils/Country.mmdb')
            print('Success!\n')
        except Exception:
            print('Failed!\n')
            pass


if __name__ == '__main__':
    update_url.update_main()
    sub_merge.geoip_update(
        'https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')
    sub_list = sub_merge.read_list(sub_list_json)
    sub_merge.sub_merge(sub_list)
    # sub_merge.readme_update(readme, sub_list)
