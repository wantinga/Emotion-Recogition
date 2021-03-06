# -*- coding: utf-8 -*-


import tensorflow as tf
#from tensorflow.examples.tutorials.mnist import input_data1
import cifar10_lenet5_forward
import os
import numpy as np

BATCH_SIZE = 200
LEARNING_RATE_BASE = 0.1
LEARNING_RATE_DECAY = 0.99
REGULARIZER = 0.0001
STEPS = 10000
MOVING_AVERAGE_DECAY = 0.99
MODEL_SAVE_PATH = "./cifar_lenet_model/"
MODEL_NAME = "cifar_model"


def backward(mnist):
    x = tf.placeholder(tf.float32,[BATCH_SIZE,cifar10_lenet5_forward.IMAGE_SIZE,cifar10_lenet5_forward.IMAGE_SIZE,cifar10_lenet5_forward.NUM_CHANNELS])
    #这里与FC网络的形式不同
    y_ = tf.placeholder(tf.float32,[None,cifar10_lenet5_forward.OUTPUT_NODE])    
    y = cifar10_lenet5_forward.forward(x,True,REGULARIZER)#相比FC网络这里多了一个参数train
    global_step = tf.Variable(0,trainable=False)
    
    ce = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=y,
        labels=tf.argmax(y_,1))
    cem = tf.reduce_mean(ce)
    loss = cem + tf.add_n(tf.get_collection('losses'))
    
    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        mnist.train.num_examples/BATCH_SIZE,
        LEARNING_RATE_DECAY,
        staircase=True)
    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(
        loss,global_step)
    
    ema = tf.train.ExponentialMovingAverage(
        MOVING_AVERAGE_DECAY,
        global_step)
    ema_op = ema.apply(tf.trainable_variables())
    with tf.control_dependencies([train_step,ema_op]):
        train_op = tf.no_op(name='train')
        
    saver = tf.train.Saver()
    
    
    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        
        #tf.reset_default_graph() 
        ckpt = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess,ckpt.model_checkpoint_path)
        
        for i in range(STEPS):
            xs,ys = mnist.train.next_batch(BATCH_SIZE)
            reshaped_xs = np.reshape(xs,(BATCH_SIZE,cifar10_lenet5_forward.IMAGE_SIZE,cifar10_lenet5_forward.IMAGE_SIZE,cifar10_lenet5_forward.NUM_CHANNELS))
            _,loss_value,step = sess.run(
                [train_op,loss,global_step],
                feed_dict={x:reshaped_xs,y_:ys})
            if i%100 == 0:
                print("After %d steps, loss on training_batch is %g"%(
                        step,loss_value))
                saver.save(
                    sess,os.path.join(MODEL_SAVE_PATH,MODEL_NAME),
                    global_step=global_step)
                
def main():
    mnist = input_data.read_data_sets("./data/",one_hot=True)
    backward(mnist)

if __name__ == '__main__':
    main()