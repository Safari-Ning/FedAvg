'''
Author: Safari Ning
Date: 2021-07-08 08:53:06
LastEditors: Safari Ning
LastEditTime: 2021-07-08 23:30:17
Description: description
'''

import os,time,threading
import argparse
import json
import numpy as np
import tensorflow as tf
from tqdm import tqdm
from Models import Models
from clients import clients, user
from filereceive import file_receive
from filesend import file_sender
from fileremove import file_remove
from cfg import Cfg

hostname = Cfg.hostname
port = Cfg.port



def get_init_param(jsonfile):
    '''
    @description: 获取初始化参数的json文件

    @param: 初始化参数json文件路径
    @return: dict of json
    '''   
    with open(jsonfile) as f:
        init_param = json.load(f)
    return init_param
    

def download_params(filename):
    '''
    @description: 下载全局训练参数
    
    @param filename: 参数文件名

    @return type:nparray 全局参数
    '''    
    while True:
        try:
            global_param = np.load(filename,allow_pickle=True)
            break
        except Exception:
            continue
    return global_param

def upload_params(filename,array):
    '''
    @description: 保存上传npy文件

    @param: filename,array
    @return: 
    '''    
    np.save(filename,array,allow_pickle=True)
    file_sender(hostname,port,"{}".format(filename))

def client_init(modelname,learning_rate):
    '''
    @description: 初始化生成客户端

    @param: modelname,learning_rate

    @return: sess, train, inputsx, inputsy, datasetname
    '''    
    if modelname == 'mnist_2nn' or modelname == 'mnist_cnn':
        datasetname = 'mnist'
        with tf.variable_scope('inputs') as scope:
            inputsx = tf.placeholder(tf.float32, [None, 784])
            inputsy = tf.placeholder(tf.float32, [None, 10])
    elif modelname == 'cifar10_cnn':
        datasetname = 'cifar10'
        with tf.variable_scope('inputs') as scope:
            inputsx = tf.placeholder(tf.float32, [None, 24, 24, 3])
            inputsy = tf.placeholder(tf.float32, [None, 10])

    myModel = Models(modelname, inputsx)

    predict_label = tf.nn.softmax(myModel.outputs)
    with tf.variable_scope('loss') as scope:
        Cross_entropy = -tf.reduce_mean(inputsy * tf.log(predict_label), axis=1)

    with tf.variable_scope('train') as scope:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        train = optimizer.minimize(Cross_entropy)

    with tf.variable_scope('validation') as scope:
        correct_prediction = tf.equal(tf.argmax(predict_label, axis=1), tf.argmax(inputsy, axis=1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))

    return train, inputsx, inputsy, datasetname

def client_run(num_of_clients,cfraction,epoch,batchsize,datasetname,IID,num_comm):
    '''
    @description: 运行客户端
    
    @param num_of_clients客户端数量,cfraction选用客户端的比例,epoch,batchsize,
            learning_rate学习率,IID是否服从独立同分布,datasetname数据集名,num_comm

    @return bool
    '''
    with tf.Session(config=tf.ConfigProto(
            log_device_placement=True, 
            allow_soft_placement=True, 
            gpu_options=tf.GPUOptions(allow_growth=True))) as sess:
        sess.run(tf.initialize_all_variables())

        myClients = clients(num_of_clients, datasetname,
                                    batchsize, epoch, sess, train, inputsx, inputsy, IID)
        
        upload_params("./testset/testdata.npy",myClients.test_data)
        upload_params("./testset/testlabel.npy",myClients.test_label)

        for i in range(num_comm):
            print("communicate round {}".format(i))

            while os.path.exists("./globalparam/global_param.npy")==False:
                time.sleep(1)

            num_in_comm = int(max(num_of_clients * cfraction, 1))                        
            order = np.arange(num_of_clients)
            np.random.shuffle(order)
            clients_in_comm = ['client{}'.format(i) for i in order[0:num_in_comm]]
            for client in tqdm(clients_in_comm):
                global_vars = download_params("./globalparam/global_param.npy")
                local_vars = myClients.ClientUpdate(client, global_vars)
                #上传训练参数
                upload_params("./localparam/"+client+"-local_param.npy",local_vars)
                
            file_remove("localparam")
            file_remove("globalparam")
            #上传测试集和标签
            
        

if __name__=='__main__':
    # rec_t = threading.Thread(target=file_receive())
    # rec_t.start()
    while True:
        while os.path.exists("./initparam/initparam.json")==False:
            time.sleep(1)
        init_param = get_init_param("./initparam/initparam.json")

        train, inputsx, inputsy, datasetname = client_init(init_param["modelname"],init_param["learning_rate"])

        while os.path.exists("./globalparam/global_param.npy")==False:
            time.sleep(1)
        client_run(init_param["num_of_clients"],init_param["cfraction"],
                    init_param["epoch"],init_param["batchsize"],
                    datasetname,init_param["iid"],init_param["num_comm"])
        file_remove("initparam")
        file_remove("testset")