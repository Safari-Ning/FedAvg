'''
Author: Safari Ning
Date: 2021-07-08 14:02:10
LastEditTime: 2021-07-08 15:27:27
LastEditors: Please set LastEditors
Description: 删除中间文件
FilePath: /FileSys/fileremove.py
'''

import os

def file_remove(file_path):
    '''
    @description: 删除文件夹下的所有文件
    @param filepath文件夹名
    @return 
    '''    
    for file in os.listdir(file_path):
        os.remove(file_path+"/"+file)

def remove_all_param_file():
    """
    移除所有参数
    """
    file_path_list = ["initparam","localparam","globalparam","testset","checkpoints"]
    
    for path in file_path_list:
        file_remove(path)

if __name__=='__main__':
    remove_all_param_file()

