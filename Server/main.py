'''
Author: Safari Ning
Date: 2021-07-06 09:36:17
LastEditors: Safari Ning
LastEditTime: 2021-07-08 19:50:18
Description: description
'''
import os,time,json,threading,requests
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

def get_user_cmd():
    '''
    @description: 获取前端用户指令

    @param 
    
    @return {*}
    '''    

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

def server_init(gpu,modelname,learning_rate):
    '''
    @description: 初始化服务端

    @param: gpu

    @return: saver,myModel,sess,accuracy,inputsx,inputsy
    '''    
    os.environ['CUDA_VISIBLE_DEVICES'] = gpu
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

    saver = tf.train.Saver(max_to_keep=3)
    sess = tf.Session(config=tf.ConfigProto(
                        log_device_placement=True, 
                        allow_soft_placement=True, 
                        gpu_options=tf.GPUOptions(allow_growth=True)))
    sess.run(tf.initialize_all_variables())

    vars = tf.trainable_variables()
    global_vars = sess.run(vars)
    upload_params("./globalparam/global_param.npy",global_vars)
    file_remove("globalparam")
    
    
    return saver,myModel,sess,accuracy,inputsx,inputsy,global_vars,vars

def server_run(num_comm,save_freq,num_of_clients,cfraction,modelname,saver,save_path,sess,val_freq,accuracy,inputsx,inputsy,IID,global_vars,vars):
    '''
    @description: 运行服务端

    @param: num_comm,save_freq,num_of_clients,cfraction,modelname,saver,save_path,sess,val_freq,inputsx,inputsy,IID,global_vars,vars

    @return: none
    '''    


    num_in_comm = int(max(num_of_clients * cfraction, 1))
    for i in range(num_comm):
        print("communicate round {}".format(i))
        
        sum_vars = None

        while int(len(os.listdir("./localparam/"))) < num_in_comm:
            time.sleep(1)

        local_param_files = os.listdir("./localparam/") 

        for local_param_file in tqdm(local_param_files):
            local_vars = download_params("./localparam/"+local_param_file)

            if sum_vars is None:
                sum_vars = local_vars
            else:
                for sum_var, local_var in zip(sum_vars, local_vars):
                    sum_var += local_var

        file_remove("localparam")

        global_vars = []
        for var in sum_vars:
            global_vars.append(var / num_in_comm)
        #--------------------------------------------------------------------------#
        upload_params("./globalparam/global_param.npy",global_vars)
        file_remove("globalparam")
        #--------------------------------------------------------------------------#
        if ((i+1) % val_freq) == 0:
            for variable, value in zip(vars, global_vars):
                variable.load(value, sess)
            
            test_data = download_params("./testset/testdata.npy")
            test_label = download_params("./testset/testlabel.npy")

            print(sess.run(accuracy, feed_dict={inputsx: test_data, inputsy: test_label}))

        if ((i+1) % save_freq) == 0:
            checkpoint_name = os.path.join(save_path, '{}_comm'.format(modelname) +
                                            'IID{}_communication{}'.format(IID, i+1)+ '.ckpt')
            saver.save(sess, checkpoint_name)
            print("save model-{}".format(i+1))
    
    tf.reset_default_graph()
    sess.close()

def get_init_param(jsonfile):
    '''
    @description: 获取初始化参数的json文件

    @param: 初始化参数json文件路径
    @return: dict of json
    '''   
    with open(jsonfile) as f:
        init_param = json.load(f)
    return init_param
    
    
if __name__=='__main__':
    while True:
        while os.path.exists("./initparam/initparam.json")==False:
            time.sleep(1)
        init_param = get_init_param("./initparam/initparam.json")
        file_sender(hostname, port, "./initparam/initparam.json")

        saver,myModel,sess,accuracy,inputsx,inputsy,global_vars,vars = server_init(str(init_param["gpu"]),init_param["modelname"],init_param["learning_rate"])
        num_in_comm = int(max(init_param["num_of_clients"] * init_param["cfraction"], 1))

        # while int(len(os.listdir("./localparam/"))) < num_in_comm:
        #     time.sleep(1)
        
        server_run(init_param["num_comm"],init_param["save_freq"],
                    init_param["num_of_clients"],init_param["cfraction"],
                    init_param["modelname"],saver,init_param["save_path"],
                    sess,init_param["val_freq"],accuracy,inputsx,inputsy,
                    init_param["iid"],global_vars,vars)
        file_remove("testset")
        file_remove("initparam")

