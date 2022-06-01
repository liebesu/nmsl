#!/usr/bin/env python3

import base64
import json
import re
import socket
import urllib.parse
from asyncore import write

import geoip2.database
import requests
from requests.adapters import HTTPAdapter


class sub_convert():
    def get_node_from_sub(url_raw='', server_host='http://127.0.0.1:25500'):
        # 使用远程订阅转换服务
        # server_host = 'https://api.v1.mk'
        # 使用本地订阅转换服务
        # 分割订阅链接
        urls = url_raw.split('|')
        sub_content = []
        for url in urls:
            # 对url进行ASCII编码
            url_quote = urllib.parse.quote(url, safe='')
            # 转换并获取订阅链接数据
            converted_url = server_host+'/sub?target=mixed&url='+url_quote+'&list=true'
            try:
                resp = requests.get(converted_url)
                node_list = resp.text
            except Exception as err:
                # 链接有问题，直接返回原始错误
                print('网络错误，检查订阅转换服务器是否失效:' + '\n' +
                      converted_url + '\n' + err + '\n')
            # 如果解析出错，将原始链接内容拷贝下来
            if resp.text == 'No nodes were found!':
                print(resp.text + '\n下载订阅文件……')
                node_list = sub_convert.convert(url)
            # 改名
            node_list_formated = sub_convert.format(node_list)
            sub_content.append(node_list_formated)
        sub_content_all = ''.join(sub_content)
        return sub_content_all

    # 一般可以通过subconviter生成订阅链接的内容一般都不需要额外处理
    def convert(raw_input):
        # convert Url to YAML or Base64
        sub_content = ''
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        s.mount('https://', HTTPAdapter(max_retries=5))
        try:
            print('Downloading from:' + raw_input)
            resp = s.get(raw_input, timeout=5)
            if '404' or 'Couldn\'t' in resp.text:
                print('订阅链接不存在')
                return ''
            else:
                lines = resp.text.split('\n')
                for list in lines:
                    if 'ss://' in list:
                        sub_content += list + '\n'
                    elif 'ssr://' in list:
                        sub_content += list + '\n'
                    elif 'vmess://' in list:
                        sub_content += list + '\n'
                    elif 'trojan://' in list:
                        sub_content += list + '\n'
                    else:
                        continue
                return sub_content
        except Exception as err:
            print(err)
            return ''

    def format(node_list):
        # 重命名
        node_list_formated_array = []
        node_list_array = node_list.split('\n')
        for node in node_list_array:
            # ss有多种情况待办
            if 'ss://' in node and 'vless://' not in node and 'vmess://' not in node:
                try:
                    node_del_head = node.replace('ss://', '')
                    if '@' in node_del_head:
                        node_part = re.split('@|#', node_del_head, maxsplit=2)
                        server_head = sub_convert.find_country(
                            node_part[1].split(':')[0])
                        password = sub_convert.base64_decode(
                            node_part[0]).split(':')[-1]
                        name_renamed = server_head + \
                            node_part[1] + '-' + password
                        node_part[2] = urllib.parse.quote(
                            name_renamed, safe='')
                        node_raw = node_part[0] + '@' + \
                            node_part[1] + '#' + node_part[2]
                        node = 'ss://' + node_raw
                    else:
                        node_part = node_del_head.split('#')
                        node_part_head_decoded = sub_convert.base64_decode(
                            node_part[0])
                        node_part_head = re.split(
                            '@|:', node_part_head_decoded, maxsplit=0)
                        server_port = node_part_head[-1]
                        server = node_part_head[-2]
                        server_head = sub_convert.find_country(
                            server)
                        password = node_part_head[-3]
                        name_renamed = server_head + \
                            server + ':' + server_port + '-' + password
                        node_part[1] = urllib.parse.quote(
                            name_renamed, safe='')
                        node_raw = node_part[0] + '#' + node_part[1]
                        node = 'ss://' + node_raw
                        node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 ss 节点发生错误: {err}')
            elif 'ssr://' in node:
                try:
                    node_del_head = node.replace('ssr://', '')
                    node_part = sub_convert.base64_decode(
                        node_del_head).split('/?')
                    # example : 194.50.171.214:9566:origin:rc4:plain:bG5jbi5vcmcgOGw/?obfsparam=&remarks=5L-E572X5pavTQ&group=TG5jbi5vcmc
                    node_part_head = node_part[0].split(':')
                    server_head = sub_convert.find_country(
                        node_part_head[0])
                    password = sub_convert.base64_decode(node_part_head[-1])
                    name_renamed = server_head + \
                        node_part_head[0] + ':' + \
                        node_part_head[1] + '-' + password
                    node_part_foot = node_part[-1].split('&')
                    for i in range(len(node_part_foot)):
                        if 'remarks' in node_part_foot[i]:
                            node_part_foot[i] = 'remarks=' + \
                                sub_convert.base64_encode(name_renamed)
                            break
                    node_part_foot_str = '&'.join(node_part_foot)
                    node_raw = sub_convert.base64_encode(
                        node_part[0] + '/?' + node_part_foot_str)
                    node = 'ssr://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 ssr 节点发生错误: {err}')
            elif 'vmess://' in node:
                try:
                    node_del_head = node.replace('vmess://', '')
                    node_json = json.loads(
                        sub_convert.base64_decode(node_del_head))
                    name_renamed = sub_convert.find_country(
                        node_json['add']) + node_json['add'] + ':' + node_json['port'] + '-' + node_json['id']
                    node_json['ps'] = name_renamed
                    node_json_dumps = json.dumps(node_json)
                    node_raw = sub_convert.base64_encode(node_json_dumps)
                    node = 'vmess://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 vmess 节点发生错误: {err}')
            elif 'trojan://' in node:
                try:
                    node_del_head = node.replace('trojan://', '')
                    node_part = re.split('@|#', node_del_head, maxsplit=2)
                    server_head = sub_convert.find_country(
                        node_part[1].split(':')[0])
                    password = node_part[0]
                    name_renamed = server_head + \
                        node_part[1].split('?')[0] + '-' + password
                    node_raw = node_part[0] + '@' + \
                        node_part[1] + '#' + name_renamed
                    node = 'trojan://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 trojan 节点发生错误: {err}')
        node_list_formated = '\n'.join(node_list_formated_array)
        if node_list_formated == '':
            return node_list_formated
        else:
            return node_list_formated + '\n'
    # 使用外部subconverter转换订阅链接为链接url

    def find_country(server):
        if server.replace('.', '').isdigit():
            ip = server
        else:
            try:
                # https://cloud.tencent.com/developer/article/1569841
                ip = socket.gethostbyname(server)
            except Exception:
                ip = server
        with geoip2.database.Reader('./utils/Country.mmdb') as ip_reader:
            try:
                response = ip_reader.country(ip)
                country_code = response.country.iso_code
            except Exception:
                ip = '0.0.0.0'
                country_code = 'NOWHERE'

        if country_code == 'CLOUDFLARE':
            country_code = 'RELAY'
        elif country_code == 'PRIVATE':
            country_code = 'RELAY'
        return '[' + country_code + ']'

    def write_to_node(node_list_array, path):
        length = 1000
        for i in range(0, len(node_list_array), length):
            nodes_part_array = node_list_array[i:i + length]
            node_list = '\n'.join(nodes_part_array)
            node_list_file = open(f'{path}{(i+1)//length}.txt', 'w', encoding='utf-8')
            node_list_file.write(node_list)
            node_list_file.close()

    def write_to_base64(node_list_array, path):
        node_list = '\n'.join(node_list_array)
        node_list_base64 = sub_convert.base64_encode(node_list)
        node_list_base64_file = open(path, 'w', encoding='utf-8')
        node_list_base64_file.write(node_list_base64)
        node_list_base64_file.close()

    def write_to_clash(file_list_array, path, server_host='http://127.0.0.1:25500'):
        # 使用远程订阅转换服务
        server_host = 'https://api.v1.mk'
        for i in range(file_list_array):
            url_head = 'https://raw.githubusercontent.com/songtao1873/nmsl/main/sub/node/'
            url = url_head + file_list_array[i]
            file_part_encoded = urllib.parse.quote(url, safe='')
            converted_url = server_host + '/sub?target=clash&url=' + \
                file_part_encoded + '&list=true'
            try:
                nodes_part_converted = requests.get(converted_url)
                nodes_part_file = open(
                    f'{path}{i}.yaml', 'w', encoding='utf-8')
                nodes_part_file.write(nodes_part_converted.text)
            except Exception as err:
                print(err)

    def base64_encode(url_content):  # 将 URL 内容转换为 Base64
        base64_content = base64.b64encode(
            url_content.encode('utf-8')).decode('ascii')
        return base64_content

    def base64_decode(url_content):  # Base64 转换为 URL 链接内容
        if '-' in url_content:
            url_content = url_content.replace('-', '+')
        elif '_' in url_content:
            url_content = url_content.replace('_', '/')
        # print(len(url_content))
        missing_padding = len(url_content) % 4
        if missing_padding != 0:
            # 不是4的倍数后加= https://www.cnblogs.com/wswang/p/7717997.html
            url_content += '='*(4 - missing_padding)
        try:
            base64_content = base64.b64decode(url_content.encode(
                'utf-8')).decode('utf-8', 'ignore')  # https://www.codenong.com/42339876/
            base64_content_format = base64_content
            return base64_content_format
        except UnicodeDecodeError:
            base64_content = base64.b64decode(url_content)
            base64_content_format = base64_content
            return base64_content
