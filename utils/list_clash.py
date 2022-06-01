import os

from sub_convert import sub_convert

nodes_file_path = './sub/node/'
clash_file_path = './sub/clash/'
file_names = os.listdir(nodes_file_path)
sub_convert.write_to_clash(file_names, clash_file_path)
# if __name__ == '__main__':
