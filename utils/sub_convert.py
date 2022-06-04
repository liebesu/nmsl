#!/usr/bin/env python3

import base64
import json
import re
import socket
import urllib.parse

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
                        name_renamed = '[ss]' + server_head + \
                            node_part[1] + '(' + password + ')'
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
                        name_renamed = '[ss]' + server_head + server + \
                            ':' + server_port + '(' + password + ')'
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
                    name_renamed = '[ssr]' + server_head + node_part_head[0] + ':' + \
                        node_part_head[1] + '(' + password + ')'
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
                        '[vmess]' + node_json['add']) + node_json['add'] + ':' + node_json['port'] + '(' + node_json['id'] + ')'
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
                    name_renamed = '[trojan]' + server_head + \
                        node_part[1].split('?')[0] + '(' + password + ')'
                    node_raw = node_part[0] + '@' + \
                        node_part[1] + '#' + urllib.parse.quote(name_renamed)
                    node = 'trojan://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 trojan 节点发生错误: {err}')
        node_list_formated = '\n'.join(node_list_formated_array)
        if node_list_formated == '':
            return node_list_formated
        else:
            return node_list_formated + '\n'

    def duplicate_removal(node_list):
        node_list_dr_array = []
        node_name_dr_array = []
        for node in node_list:
            node_name = sub_convert.get_node_name(node)
            if node_name not in node_name_dr_array:
                node_name_dr_array.append(node_name)
                node_list_dr_array.append(node)
        return node_list_dr_array

    def get_node_name(node):
        if 'ss://' in node and 'vless://' not in node and 'vmess://' not in node:
            try:
                node_del_head = node.replace('ss://', '')
                if '@' in node_del_head:
                    node_part = re.split('@|#', node_del_head, maxsplit=2)
                    name = urllib.parse.unquote(node_part[2])
                else:
                    node_part = node_del_head.split('#')
                    name = urllib.parse.unquote(node_part[1])
            except Exception as err:
                print(f'改名 ss 节点发生错误: {err}')
        elif 'ssr://' in node:
            try:
                node_del_head = node.replace('ssr://', '')
                node_part = sub_convert.base64_decode(
                    node_del_head).split('/?')
                node_part_foot = node_part[-1].split('&')
                for i in range(len(node_part_foot)):
                    if 'remarks' in node_part_foot[i]:
                        name = sub_convert.base64_decode(
                            node_part_foot[i].replace('remarks=', ''))
                        break
            except Exception as err:
                print(f'获取节点名错误: {err}')
        elif 'vmess://' in node:
            try:
                node_del_head = node.replace('vmess://', '')
                node_json = json.loads(
                    sub_convert.base64_decode(node_del_head))
                name = node_json['ps']
            except Exception as err:
                print(f'获取节点名错误: {err}')
        elif 'trojan://' in node:
            try:
                node_del_head = node.replace('trojan://', '')
                node_part = re.split('@|#', node_del_head, maxsplit=2)
                name = urllib.parse.unquote(node_part[-1])
            except Exception as err:
                print(f'获取节点名错误: {err}')
        return name

    def find_country(server):
        emoji = {
            'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬',
            'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
            'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹',
            'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
            'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪',
            'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
            'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳',
            'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
            'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾',
            'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
            'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮',
            'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
            'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻',
            'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
            'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲',
            'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
            'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸',
            'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯',
            'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷',
            'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪',
            'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮',
            'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵',
            'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹',
            'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰',
            'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹',
            'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱',
            'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶',
            'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪',
            'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪',
            'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲',
            'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼',
            'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧',
            'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷',
            'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻',
            'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩',
            'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭',
            'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳',
            'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷',
            'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻',
            'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿',
            'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫',
            'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴',
            'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿',
            'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫',
            'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱',
            'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸',
            'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦',
            'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺',
            'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨',
            'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭',
            'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱',
            'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷',
            'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽',
            'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩',
            'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯',
            'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳',
            'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻',
            'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬',
            'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿',
            'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
            'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫',
            'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹',
            'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼',
            'RELAY': '🏁',
            'NOWHERE': '🇦🇶',
        }
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
        if country_code in emoji:
            name_emoji = emoji[country_code]
        else:
            name_emoji = emoji['NOWHERE']
        return name_emoji + '[' + country_code + ']'

    def write_to_node(node_list_array, path):
        node_list = '\n'.join(node_list_array)
        node_list_file = open(path, 'w', encoding='utf-8')
        node_list_file.write(node_list)
        node_list_file.close()

    def write_to_base64(node_list_array, path):
        node_list = '\n'.join(node_list_array)
        node_list_base64 = sub_convert.base64_encode(node_list)
        node_list_base64_file = open(path, 'w', encoding='utf-8')
        node_list_base64_file.write(node_list_base64)
        node_list_base64_file.close()

    def write_to_clash(node_list_array, path):
        # 使用远程订阅转换服务
        # server_host = 'https://api.v1.mk'
        for i in range(0, len(node_list_array), 1000):
            node_list_array_part = node_list_array[i:i + 1000]
            node_list_part = sub_convert.yaml_encode(node_list_array_part)
            node_list_part_file = open(
                f'{path}{(i+1)//1000}.yaml', 'w', encoding='utf-8')
            node_list_part_file.write(node_list_part)
            node_list_part_file.close()

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

    def yaml_encode(lines):  # 将 URL 内容转换为 YAML (输出默认 YAML 格式)
        url_list = []
        for line in lines:
            yaml_url = {}
            if 'vmess://' in line:
                try:
                    vmess_json_config = json.loads(
                        sub_convert.base64_decode(line.replace('vmess://', '')))
                    vmess_default_config = {
                        'v': 'Vmess Node', 'ps': 'Vmess Node', 'add': '0.0.0.0', 'port': 0, 'id': '',
                        'aid': 0, 'scy': 'auto', 'net': '', 'type': '', 'host': vmess_json_config['add'], 'path': '/', 'tls': ''
                    }
                    vmess_default_config.update(vmess_json_config)
                    vmess_config = vmess_default_config

                    yaml_url = {}
                    #yaml_config_str = ['name', 'server', 'port', 'type', 'uuid', 'alterId', 'cipher', 'tls', 'skip-cert-verify', 'network', 'ws-path', 'ws-headers']
                    #vmess_config_str = ['ps', 'add', 'port', 'id', 'aid', 'scy', 'tls', 'net', 'host', 'path']
                    # 生成 yaml 节点字典
                    if vmess_config['id'] == '':
                        print('节点格式错误')
                    else:
                        yaml_url.setdefault(
                            'name', '"' + urllib.parse.unquote(str(vmess_config['ps'])) + '"')
                        yaml_url.setdefault('server', vmess_config['add'])
                        yaml_url.setdefault('port', int(vmess_config['port']))
                        yaml_url.setdefault('type', 'vmess')
                        yaml_url.setdefault('uuid', vmess_config['id'])
                        yaml_url.setdefault(
                            'alterId', int(vmess_config['aid']))
                        yaml_url.setdefault('cipher', vmess_config['scy'])
                        yaml_url.setdefault('skip-cert-vertify', 'true')
                        if vmess_config['net'] == '' or vmess_config['net'] is False:
                            yaml_url.setdefault('network', 'tcp')
                        else:
                            yaml_url.setdefault('network', vmess_config['net'])
                        if vmess_config['path'] == '' or vmess_config['path'] is False:
                            yaml_url.setdefault('ws-path', '/')
                        else:
                            yaml_url.setdefault(
                                'ws-path', vmess_config['path'].split('?')[0])
                        if vmess_config['net'] == 'h2' or vmess_config['net'] == 'grpc':
                            yaml_url.setdefault('tls', 'true')
                        elif vmess_config['tls'] == '' or vmess_config['tls'] is False:
                            yaml_url.setdefault('tls', 'false')
                        else:
                            yaml_url.setdefault('tls', 'true')
                        yaml_url.setdefault(
                            'ws-headers', {'Host': vmess_config['add']})
                        # if vmess_config['host'] == '':
                        #     yaml_url.setdefault(
                        #         'ws-headers', {'Host': vmess_config['add']})
                        # else:
                        #     yaml_url.setdefault(
                        #         'ws-headers', {'Host': vmess_config['host']})

                except Exception as err:
                    print(f'yaml_encode 解析 vmess 节点发生错误: {err}')
                    pass

            if 'ss://' in line and 'vless://' not in line and 'vmess://' not in line:
                if '#' not in line:
                    line = line + '#SS%20Node'
                try:
                    ss_content = line.replace('ss://', '')
                    # https://www.runoob.com/python/att-string-split.html
                    part_list = ss_content.split('#', 1)
                    yaml_url.setdefault(
                        'name', '"' + urllib.parse.unquote(part_list[1]) + '"')
                    if '@' in part_list[0]:
                        mix_part = part_list[0].split('@', 1)
                        method_part = sub_convert.base64_decode(mix_part[0])
                        server_part = f'{method_part}@{mix_part[1]}'
                    else:
                        server_part = sub_convert.base64_decode(part_list[0])

                    # 使用多个分隔符 https://blog.csdn.net/shidamowang/article/details/80254476 https://zhuanlan.zhihu.com/p/92287240
                    server_part_list = server_part.split(':', 1)
                    method_part = server_part_list[0]
                    server_part_list = server_part_list[1].rsplit('@', 1)
                    password_part = server_part_list[0]
                    server_part_list = server_part_list[1].split(':', 1)

                    yaml_url.setdefault('server', server_part_list[0])
                    yaml_url.setdefault('port', server_part_list[1])
                    yaml_url.setdefault('type', 'ss')
                    yaml_url.setdefault('cipher', method_part)
                    yaml_url.setdefault('password', password_part)
                except Exception as err:
                    print(f'yaml_encode 解析 ss 节点发生错误: {err}')
                    pass

            if 'ssr://' in line:
                try:
                    ssr_content = sub_convert.base64_decode(
                        line.replace('ssr://', ''))

                    part_list = re.split('/\?', ssr_content)
                    if '&' in part_list[1]:
                        # 将 SSR content /？后部分参数分割
                        ssr_part = re.split('&', part_list[1])
                        for item in ssr_part:
                            if 'remarks=' in item:
                                remarks_part = item.replace('remarks=', '')
                        try:
                            remarks = sub_convert.base64_decode(remarks_part)
                        except Exception:
                            remarks = 'ssr'
                    else:
                        remarks_part = part_list[1].replace('remarks=', '')
                        try:
                            remarks = sub_convert.base64_decode(remarks_part)
                        except Exception:
                            remarks = 'ssr'
                            print(f'SSR format error, content:{remarks_part}')
                    yaml_url.setdefault(
                        'name', '"' + urllib.parse.unquote(remarks) + '"')

                    server_part_list = re.split(':', part_list[0])
                    yaml_url.setdefault('server', server_part_list[0])
                    yaml_url.setdefault('port', server_part_list[1])
                    yaml_url.setdefault('type', 'ssr')
                    yaml_url.setdefault('cipher', server_part_list[3])
                    yaml_url.setdefault('password', server_part_list[5])
                    yaml_url.setdefault('protocol', server_part_list[2])
                    yaml_url.setdefault('obfs', server_part_list[4])
                    for item in ssr_part:
                        if 'obfsparam=' in item:
                            obfs_param = sub_convert.base64_decode(
                                item.replace('obfsparam=', ''))
                            if obfs_param != '':
                                yaml_url.setdefault('obfs-param', obfs_param)
                            else:
                                yaml_url.setdefault('obfs-param', '""')
                        elif 'protoparam=' in item:
                            protocol_param = sub_convert.base64_decode(
                                item.replace('protoparam=', ''))
                            if protocol_param != '':
                                yaml_url.setdefault(
                                    'protocol-param', protocol_param)
                            else:
                                yaml_url.setdefault(
                                    'protocol-param', '""')
                except Exception as err:
                    print(f'yaml_encode 解析 ssr 节点发生错误: {err}')
                    pass

            if 'trojan://' in line:
                try:
                    url_content = line.replace('trojan://', '')
                    # https://www.runoob.com/python/att-string-split.html
                    part_list = re.split('#', url_content, maxsplit=1)
                    yaml_url.setdefault(
                        'name', '"' + urllib.parse.unquote(part_list[1]) + '"')

                    server_part = part_list[0].replace('trojan://', '')
                    # 使用多个分隔符 https://blog.csdn.net/shidamowang/article/details/80254476 https://zhuanlan.zhihu.com/p/92287240
                    server_part_list = re.split(':|@|\?|&', server_part)
                    yaml_url.setdefault('server', server_part_list[1])
                    yaml_url.setdefault('port', server_part_list[2])
                    yaml_url.setdefault('type', 'trojan')
                    yaml_url.setdefault('password', server_part_list[0])
                    yaml_url.setdefault('sni', server_part_list[1])
                    server_part_list_parameters = server_part_list[3:]

                    for config in server_part_list_parameters:
                        if 'sni=' in config:
                            yaml_url.setdefault('sni', config[4:])
                        elif 'allowInsecure=' in config or 'tls=' in config:
                            if config[-1] == 0:
                                yaml_url.setdefault('tls', 'false')
                            else:
                                yaml_url.setdefault('tls', 'true')
                        elif 'type=' in config:
                            yaml_url.setdefault('network', config[5:])
                        elif 'path=' in config:
                            yaml_url.setdefault(
                                'ws-path', config[5:].split('?')[0])
                        elif 'security=' in config:
                            if config[9:] != 'tls':
                                yaml_url.setdefault('tls', 'false')
                            else:
                                yaml_url.setdefault('tls', 'true')

                    yaml_url.setdefault('skip-cert-verify', 'true')
                except Exception as err:
                    print(f'yaml_encode 解析 trojan 节点发生错误: {err}')
                    pass
            yaml_node_raw = str(yaml_url)
            yaml_node_body = yaml_node_raw.replace('\'', '')
            yaml_node_head = '  - '
            yaml_node = yaml_node_head + yaml_node_body
            url_list.append(yaml_node)
        yaml_head = 'proxies:\n'
        yaml_content = yaml_head + '\n'.join(url_list)

        return yaml_content
