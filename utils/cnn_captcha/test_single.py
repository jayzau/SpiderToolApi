# -*- coding: utf-8 -*-
import json

import tensorflow as tf
import numpy as np
import time
from PIL import Image
import random
import os

from utils.cnn_captcha.cnnlib.network import CNN
from utils.cnn_captcha.settings import CAPTCHA_CONFIG


class TestError(Exception):
    pass


class TestSingle(CNN):
    def __init__(self, img_path, image_width, image_height, max_captcha, char_set, model_save_dir, model_save_name):
        # 模型路径
        self.model_save_dir = model_save_dir
        # 打乱文件顺序
        self.img_path = img_path
        self.image_width = image_width
        self.image_height = image_height

        random.seed(time.time())

        # 初始化变量
        super(TestSingle, self).__init__(image_height, image_width, max_captcha, char_set, model_save_dir,
                                         model_save_name)

        # 相关信息打印
        print("-->图片尺寸: {} X {}".format(image_height, image_width))
        print("-->验证码长度: {}".format(self.max_captcha))
        print("-->验证码共{}类 {}".format(self.char_set_len, char_set))
        print("-->使用测试集为 {}".format(img_path))

    def test_batch(self):
        y_predict = self.model()
        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, self.model_save_path)
            s = time.time()
            # test_text, test_image = gen_special_num_image(i)
            captcha_image = Image.open(self.img_path)
            captcha_image = captcha_image.resize((self.image_width, self.image_height))
            test_image = np.array(captcha_image)  # 向量化
            test_image = self.convert2gray(test_image)
            test_image = test_image.flatten() / 255

            predict = tf.argmax(tf.reshape(y_predict, [-1, self.max_captcha, self.char_set_len]), 2)
            text_list = sess.run(predict, feed_dict={self.X: [test_image], self.keep_prob: 1.})
            predict_text = text_list[0].tolist()
            p_text = ""
            for p in predict_text:
                p_text += str(self.char_set[p])
            print("predict: {}".format(p_text))
            e = time.time()
        print("识别耗时{}秒".format(e-s))


def main():
    test_img_path = "/home/jayzau/Desktop/LoginRdCode.jpeg"

    image_width = CAPTCHA_CONFIG["image_width"]
    image_height = CAPTCHA_CONFIG["image_height"]

    max_captcha = CAPTCHA_CONFIG["max_captcha"]

    model_save_dir = CAPTCHA_CONFIG["model_save_dir"]
    model_save_name = CAPTCHA_CONFIG["model_save_name"]

    use_labels_json_file = CAPTCHA_CONFIG['use_labels_json_file']

    if use_labels_json_file:
        with open("tools/labels.json", "r") as f:
            char_set = f.read().strip()
    else:
        char_set = CAPTCHA_CONFIG["char_set"]

    tb = TestSingle(test_img_path, image_width, image_height, max_captcha, char_set, model_save_dir, model_save_name)
    tb.test_batch()


if __name__ == '__main__':
    main()
