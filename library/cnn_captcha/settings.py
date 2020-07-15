import os

CNN_CAPTCHA_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CNN_CAPTCHA_ROOT_PATH, "model")
if not os.path.isdir(MODEL_PATH):
    os.mkdir(MODEL_PATH)

IMAGE_WIDTH = 100
IMAGE_HEIGHT = 60

CAPTCHA_CONFIG = {
  "max_captcha": 4,
  "model_save_dir": MODEL_PATH,
  "model_save_name": "default.ckpt",
  "cycle_stop": 100,
  "acc_stop": 0.99,
  "cycle_save": 500,
  # "enable_gpu": 0,
  "image_suffix": "png",
  "train_batch_size": 128,
  "test_batch_size": 100
}

CHAR_SET = {
  "0004": "0123456789",
  "1004": "abcdefghijklmnopqrstuvwxyz",
  "2004": "0123456789abcdefghijklmnopqrstuvwxyz",
  "3004": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
}

SOFT_ID = {
  "bx0v34a22c1v6dbe859sc46a05327e1f": "601281"
}

DEFAULT_WEBSITE = "default"
DEFAULT_MAX_CAPTCHA = CAPTCHA_CONFIG["max_captcha"]
DEFAULT_CHAR_SET = "3004"
DEFAULT_IMAGE_SUFFIX = CAPTCHA_CONFIG["image_suffix"]
