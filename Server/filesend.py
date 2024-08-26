'''
Author: your name
Date: 2021-07-07 14:53:11
LastEditTime: 2021-07-08 15:18:41
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \FileSys\filesend.py
'''
import os
import json
import struct 
import socket

def file_sender(hostname,port,filepath):
    sk = socket.socket()
    sk.connect((hostname, port))
    # 文件名\文件大小
    abs_path = filepath
    filename = os.path.basename(abs_path)
    filesize = os.path.getsize(abs_path)

    dic = {'filename': filename, 'filesize': filesize}
    str_dic = json.dumps(dic)
    b_dic = str_dic.encode("utf-8")
    mlen = struct.pack('i', len(b_dic))
    sk.send(mlen)
    sk.send(b_dic)

    with open(abs_path, mode='rb') as f:
        while filesize > 0:
            content = f.read(1024)
            filesize -= 1024
            sk.send(content)
    sk.close()

if __name__=='__main__':
    file_sender("10.2.11.164",9001,"./data/data.npy")