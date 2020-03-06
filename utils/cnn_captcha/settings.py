import os

CNN_CAPTCHA_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CAPTCHA_PATH = os.path.join(CNN_CAPTCHA_ROOT_PATH, "captcha")
MODEL_PATH = os.path.join(CNN_CAPTCHA_ROOT_PATH, "model")

CAPTCHA_CONFIG = {
  "origin_image_dir": os.path.join(CAPTCHA_PATH, "origin"),
  "new_image_dir": os.path.join(CAPTCHA_PATH, "new_train"),
  "train_image_dir": os.path.join(CAPTCHA_PATH, "train"),
  "test_image_dir": os.path.join(CAPTCHA_PATH, "test"),
  "api_image_dir": os.path.join(CAPTCHA_PATH, "api"),
  "online_image_dir": os.path.join(CAPTCHA_PATH, "online"),
  "local_image_dir": os.path.join(CAPTCHA_PATH, "local"),
  "model_save_dir": MODEL_PATH,
  "model_save_name": "model.ckpt",
  "image_width": 100,
  "image_height": 60,
  "max_captcha": 4,
  "image_suffix": "png",
  "char_set": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
  "use_labels_json_file": False,
  "remote_url": "http://127.0.0.1:6100/captcha/",
  "cycle_stop": 81000,
  "acc_stop": 0.99,
  "cycle_save": 500,
  "enable_gpu": 0,
  "train_batch_size": 128,
  "test_batch_size": 100
}


