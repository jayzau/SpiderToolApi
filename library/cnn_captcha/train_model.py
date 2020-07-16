# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time
from PIL import Image
import random
import os

from tensorflow.python.framework.errors_impl import NotFoundError

from library.cnn_captcha.cnnlib.network import CNN, logger


class TrainError(Exception):
    pass


class TrainModel(CNN):
    def __init__(self, train_img_path, verify_img_path, char_set, model_save_dir, model_save_name, cycle_stop, acc_stop,
                 cycle_save, image_suffix, train_batch_size, test_batch_size, verify=False, **kwargs):
        # 训练相关参数
        self.cycle_stop = cycle_stop
        self.acc_stop = acc_stop
        self.cycle_save = cycle_save
        self.train_batch_size = train_batch_size
        self.test_batch_size = test_batch_size

        self.image_suffix = image_suffix
        char_set = [str(i) for i in char_set]

        # 打乱文件顺序+校验图片格式
        self.train_img_path = train_img_path
        self.train_images_list = os.listdir(train_img_path)
        # 校验格式
        if verify:
            self.confirm_image_suffix()
        # 打乱文件顺序
        random.seed(time.time())
        random.shuffle(self.train_images_list)

        # 验证集文件
        self.verify_img_path = verify_img_path
        self.verify_images_list = os.listdir(verify_img_path)

        # 获得图片宽高和字符长度基本信息
        label, captcha_array = self.gen_captcha_text_image(train_img_path, self.train_images_list[0])

        captcha_shape = captcha_array.shape
        captcha_shape_len = len(captcha_shape)
        if captcha_shape_len == 3:
            image_height, image_width, channel = captcha_shape
            self.channel = channel
        elif captcha_shape_len == 2:
            image_height, image_width = captcha_shape
        else:
            raise TrainError("图片转换为矩阵时出错，请检查图片格式")

        # 初始化变量
        super(TrainModel, self).__init__(image_height, image_width, len(label), char_set, model_save_dir,
                                         model_save_name)

        # 相关信息打印
        logger.info("-->图片尺寸: {} X {}".format(image_height, image_width))
        logger.info("-->验证码长度: {}".format(self.max_captcha))
        logger.info("-->验证码共{}类 {}".format(self.char_set_len, char_set))
        logger.info("-->使用测试集为 {}".format(train_img_path))
        logger.info("-->使验证集为 {}".format(verify_img_path))

        # test model input and output
        logger.info(">>> Start model test")
        batch_x, batch_y = self.get_batch(0, size=100)
        logger.info(">>> input batch images shape: {}".format(batch_x.shape))
        logger.info(">>> input batch labels shape: {}".format(batch_y.shape))

    @staticmethod
    def gen_captcha_text_image(img_path, img_name):
        """
        返回一个验证码的array形式和对应的字符串标签
        :return:tuple (str, numpy.array)
        """
        # 标签
        label = img_name.split("_")[0]
        # 文件
        img_file = os.path.join(img_path, img_name)
        captcha_image = Image.open(img_file)
        captcha_array = np.array(captcha_image)  # 向量化
        return label, captcha_array

    def get_batch(self, n, size=128):
        batch_x = np.zeros([size, self.image_height * self.image_width])  # 初始化
        batch_y = np.zeros([size, self.max_captcha * self.char_set_len])  # 初始化

        max_batch = int(len(self.train_images_list) / size)
        # print(max_batch)
        if max_batch - 1 < 0:
            raise TrainError("训练集图片数量需要大于每批次训练的图片数量")
        if n > max_batch - 1:
            n = n % max_batch
        s = n * size
        e = (n + 1) * size
        this_batch = self.train_images_list[s:e]
        # print("{}:{}".format(s, e))

        for i, img_name in enumerate(this_batch):
            label, image_array = self.gen_captcha_text_image(self.train_img_path, img_name)
            image_array = self.convert2gray(image_array)  # 灰度化图片
            batch_x[i, :] = image_array.flatten() / 255  # flatten 转为一维
            batch_y[i, :] = self.text2vec(label)  # 生成 oneHot
        return batch_x, batch_y

    def get_verify_batch(self, size=100):
        batch_x = np.zeros([size, self.image_height * self.image_width])  # 初始化
        batch_y = np.zeros([size, self.max_captcha * self.char_set_len])  # 初始化

        verify_images = []
        for i in range(size):
            verify_images.append(random.choice(self.verify_images_list))

        for i, img_name in enumerate(verify_images):
            label, image_array = self.gen_captcha_text_image(self.verify_img_path, img_name)
            image_array = self.convert2gray(image_array)  # 灰度化图片
            batch_x[i, :] = image_array.flatten() / 255  # flatten 转为一维
            batch_y[i, :] = self.text2vec(label)  # 生成 oneHot
        return batch_x, batch_y

    def confirm_image_suffix(self):
        # 在训练前校验所有文件格式
        logger.info("开始校验所有图片后缀")
        for index, img_name in enumerate(self.train_images_list):
            logger.info("{} image pass".format(index), end='\r')
            if not img_name.endswith(self.image_suffix):
                raise TrainError('confirm images suffix：you request [.{}] file but get file [{}]'
                                 .format(self.image_suffix, img_name))
        logger.info("所有图片格式校验通过")

    def train_cnn(self):
        y_predict = self.model()
        logger.info(">>> input batch predict shape: {}".format(y_predict.shape))
        logger.info(">>> End model test")
        # 计算概率 损失
        with tf.name_scope('cost'):
            cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y_predict, labels=self.Y))
        # 梯度下降
        with tf.name_scope('train'):
            optimizer = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
        # 计算准确率
        predict = tf.reshape(y_predict, [-1, self.max_captcha, self.char_set_len])  # 预测结果
        max_idx_p = tf.argmax(predict, 2)  # 预测结果
        max_idx_l = tf.argmax(tf.reshape(self.Y, [-1, self.max_captcha, self.char_set_len]), 2)  # 标签
        # 计算准确率
        correct_pred = tf.equal(max_idx_p, max_idx_l)
        with tf.name_scope('char_acc'):
            accuracy_char_count = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
        with tf.name_scope('image_acc'):
            accuracy_image_count = tf.reduce_mean(tf.reduce_min(tf.cast(correct_pred, tf.float32), axis=1))
        # 模型保存对象
        saver = tf.train.Saver()
        with tf.Session() as sess:
            init = tf.global_variables_initializer()
            sess.run(init)
            # 恢复模型
            if os.path.exists(self.model_save_dir):
                try:
                    # 利用checkpoint自动读取上一次记录的模型
                    # checkpoint_file = tf.train.latest_checkpoint(self.model_save_dir)
                    # saver.restore(sess, checkpoint_file)

                    # 指定模型
                    saver.restore(sess, self.model_save_path)
                # 判断捕获model文件夹中没有模型文件的错误
                except (ValueError, NotFoundError):
                    logger.info("model文件夹为空，将创建新模型")
            else:
                pass
            # 写入日志
            tf.summary.FileWriter("logs/", sess.graph)

            break_count = 0
            step = 1
            for i in range(self.cycle_stop):
                batch_x, batch_y = self.get_batch(i, size=self.train_batch_size)
                # 梯度下降训练
                _, cost_ = sess.run([optimizer, cost],
                                    feed_dict={self.X: batch_x, self.Y: batch_y, self.keep_prob: 0.75})
                if step % 10 == 0:
                    # 基于训练集的测试
                    batch_x_test, batch_y_test = self.get_batch(i, size=self.train_batch_size)
                    acc_char = sess.run(accuracy_char_count, feed_dict={
                        self.X: batch_x_test, self.Y: batch_y_test, self.keep_prob: 1.})
                    acc_image_t = sess.run(accuracy_image_count, feed_dict={
                        self.X: batch_x_test, self.Y: batch_y_test, self.keep_prob: 1.})
                    logger.info("第{}/{}次训练 >>> ".format(step, self.cycle_stop))
                    logger.info("[训练集] 字符准确率为 {:.5f} 图片准确率为 {:.5f} >>> loss {:.10f}"
                                .format(acc_char, acc_image_t, cost_))

                    # 准确率达到99%后保存并停止
                    if acc_image_t >= self.acc_stop:
                        break_count += 1
                    else:
                        break_count = 0
                    if break_count >= 5:
                        saver.save(sess, self.model_save_path)
                        logger.info(f"训练集准确率连续5次达到{int(self.acc_stop * 100)}%，保存模型成功")
                        break

                    # with open("loss_train.csv", "a+") as f:
                    #     f.write("{},{},{},{}\n".format(step, acc_char, acc_image, cost_))

                    # 基于验证集的测试
                    batch_x_verify, batch_y_verify = self.get_verify_batch(size=self.test_batch_size)
                    acc_char = sess.run(accuracy_char_count, feed_dict={
                        self.X: batch_x_verify, self.Y: batch_y_verify, self.keep_prob: 1.})
                    acc_image = sess.run(accuracy_image_count, feed_dict={
                        self.X: batch_x_verify, self.Y: batch_y_verify, self.keep_prob: 1.})
                    logger.info(
                        "[验证集] 字符准确率为 {:.5f} 图片准确率为 {:.5f} >>> loss {:.10f}".format(
                            acc_char, acc_image, cost_
                        )
                    )

                    # with open("loss_test.csv", "a+") as f:
                    #     f.write("{}, {},{},{}\n".format(step, acc_char, acc_image, cost_))

                    # 准确率达到99%后保存并停止
                    if acc_image > self.acc_stop:
                        saver.save(sess, self.model_save_path)
                        logger.info(f"验证集准确率达到{int(self.acc_stop * 100)}%，保存模型成功")
                        break
                # 每训练500轮就保存一次
                if i % self.cycle_save == 0:
                    saver.save(sess, self.model_save_path)
                    logger.info("定时保存模型成功")
                step += 1
            saver.save(sess, self.model_save_path)
        return acc_image
