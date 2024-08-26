'''
Author: your name
Date: 2021-07-07 14:53:16
LastEditTime: 2021-07-08 20:51:34
LastEditors: Safari Ning
Description: In User Settings Edit
FilePath: \FileSys\filereceive.py
'''
import socket
import json
import struct

def file_receive():
    """
    开启服务器永久监听
    param:文件夹名
    """
    file_path_list = ["initparam/","localparam/","globalparam/","testset/"]

    sk = socket.socket()
    sk.bind(('0.0.0.0', 9002))
    sk.listen()
    while 1:
        conn, addr = sk.accept()
        if conn:
            print("connection build")
        msg_len = conn.recv(4)
        dic_len = struct.unpack("i", msg_len)[0]  # 防止粘包
        msg = conn.recv(dic_len).decode("utf-8")
        msg = json.loads(msg)
        filename = msg['filename']
        print("receive file:"+filename)
        
        if "global" in filename:
            file_path = file_path_list[2]
        elif "local" in filename:
            file_path = file_path_list[1]
        elif "init" in filename:
            file_path = file_path_list[0]
        elif "test" in filename:
            file_path = file_path_list[3]

        with open(file_path+filename, 'wb') as f:
            while msg['filesize'] > 0:
                content = conn.recv(1024)
                msg['filesize'] -= len(content)  # tcp协议将1024字节分开发送
                f.write(content)

    conn.close()
    sk.close()

if __name__=='__main__':
    file_receive()