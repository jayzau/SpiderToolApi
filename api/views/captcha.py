import datetime
import os
import shutil
from importlib import reload

from PIL import Image, UnidentifiedImageError
from flask import request, jsonify, abort
from werkzeug.datastructures import CombinedMultiDict

from api.forms import CaptchaTypeForm, CaptchaReportForm, CaptchaValidForm, CaptchaUploadForm
from api.models import Captcha, add_and_commit
from config.settings import ROOT_PATH, FLASK_CONFIG
from library.cnn_captcha import captcha_reader
from library.cnn_captcha.settings import CAPTCHA_CONFIG, CHAR_SET, DEFAULT_CHAR_SET, IMAGE_WIDTH, IMAGE_HEIGHT
from library.cnn_captcha.train_model import TrainModel, TrainError
from library.cnn_captcha.captcha_operation import make_pic_name, parse_pic_name, parse_recognizer_key, \
    make_recognizer_key, make_pic_name_for_train
from library.redprint import RedPrint

api = RedPrint("captcha")
# 必要的文件夹
# static_folder = current_app.static_folder
static_folder = os.path.join(ROOT_PATH, FLASK_CONFIG["static_folder"])
CAPTCHA_FOLDER = os.path.join(static_folder, "captcha")
CAPTCHA_UPLOAD_FOLDER = os.path.join(CAPTCHA_FOLDER, "upload")
CAPTCHA_REPORT_FOLDER = os.path.join(CAPTCHA_FOLDER, "report")
CAPTCHA_TRAIN_FOLDER = os.path.join(CAPTCHA_FOLDER, "train")
CAPTCHA_TEST_FOLDER = os.path.join(CAPTCHA_FOLDER, "test")
for _path in [
    static_folder,
    CAPTCHA_FOLDER,
    CAPTCHA_UPLOAD_FOLDER,
    CAPTCHA_REPORT_FOLDER,
    CAPTCHA_TRAIN_FOLDER,
    CAPTCHA_TEST_FOLDER
]:
    if not os.path.isdir(_path):
        os.mkdir(_path)


@api.route("/", methods=["POST"])
def read_captcha():
    """
    识别或上传一张验证码图片
    :return:
    """
    result = {
        "error_code": 200,
        "captcha_str": "",
        "captcha_id": "",
        "md5": "",
        "err_str": "",
    }
    form = CaptchaTypeForm(CombinedMultiDict([request.form, request.files]))

    if form.validate():
        # 公用项
        img_bytes = form.captcha.data.stream.read()
        is_train = form.train.data      # 2020-06-19 标记是否用于训练
        # 自家验证码必备项
        website = form.website.data
        max_captcha = form.max_captcha.data
        char_set = form.char_set.data
        # 超级鹰验证码必备项
        username = form.username.data
        password = form.password.data
        soft_id = form.soft_id.data
        code_type = form.code_type.data
        # 验证码识别整合
        response = captcha_reader.parse_img_code(
            img_bytes,  # 图片流
            website, max_captcha, char_set,  # 自家验证码需要的特征
            username, password, soft_id, code_type  # 超级鹰需要的参数
        )

        recognizer_key = response.get("recognizer_key")
        pic_str = response.get("pic_str")
        pic_id = response.get("pic_id")
        md5 = response.get("md5")
        source = response.get("source")

        result["captcha_str"] = pic_str
        result["md5"] = md5
        result["source"] = source

        # 存储图片
        if not pic_str:         # 没有识别出来字符 直接进入反馈文件夹 等待手动打码
            img_name = make_pic_name(recognizer_key, md5)
            _, dir_name = os.path.split(CAPTCHA_REPORT_FOLDER)
            img_path = os.path.join(CAPTCHA_REPORT_FOLDER, img_name)
        else:           # 不管对错 记录此次打码结果
            img_name = make_pic_name(recognizer_key, md5, pic_str)
            _, dir_name = os.path.split(CAPTCHA_UPLOAD_FOLDER)
            img_path = os.path.join(CAPTCHA_UPLOAD_FOLDER, img_name)
        if is_train:        # 标记了要用于训练 才存储到本地
            with open(img_path, 'wb') as f:
                f.write(img_bytes)

        # 入库
        path = os.path.join(dir_name, img_name)         # 入库的路径 没必要那么长
        captcha = Captcha(
            captcha_id=pic_id,
            path=path,
            md5=md5,
            source=source,
            timestamp=int(datetime.datetime.now().timestamp()),
        )
        result["captcha_id"] = add_and_commit(captcha)
        if not pic_str:
            abort(404, "Not Extended. Please try it again later.")

    result["err_str"] = form.errors
    """
    超级鹰实例
    {'err_no': 0, 'err_str': 'OK', 'pic_id': '9099716572150703246', 'pic_str': 'vszz', 
    'md5': 'cbf7e7a8d377eb0fdd67d218b1c7fbc5'}
    """
    return jsonify(result)


@api.route("/report/", methods=["POST"])
def report_captcha():
    """
    错误识别反馈
    :return:
    """
    result = {
        "error_code": 200,
    }
    form = CaptchaReportForm(request.form)
    if form.validate():
        captcha_id = form.captcha_id.data
        md5 = form.md5.data

        username = form.username.data
        password = form.password.data
        soft_id = form.soft_id.data

        captcha = Captcha.query.filter_by(
            id=captcha_id,
            md5=md5
        ).first_or_404(f"No captcha id {captcha_id}.")

        if captcha.source == "super_eagle":  # 超级鹰回执
            if all([
                username,
                password,
                soft_id,
            ]):
                pic_id = captcha.captcha_id
                captcha_reader.sp_report_error(pic_id, username, password, soft_id)
            else:       # 属于超级鹰打码的 必须要有账号密码才能回馈
                abort(400, description="Parameter username, password, soft_id required.")

        file_path = captcha.path
        _, file_name = os.path.split(file_path)
        old_abs_path = os.path.join(CAPTCHA_FOLDER, file_path)

        if os.path.isfile(old_abs_path):
            # 去掉识别出来的字符
            recognizer_key, md5, pic_str = parse_pic_name(file_name)
            new_file_name = make_pic_name(recognizer_key, md5)
            new_abs_path = os.path.join(CAPTCHA_REPORT_FOLDER, new_file_name)
            shutil.move(old_abs_path, new_abs_path)
            new_file_path = os.path.join(os.path.split(CAPTCHA_REPORT_FOLDER)[-1], new_file_name)
            captcha.path = new_file_path
            captcha.update()
        else:
            abort(404, description=f"Captcha {captcha_id} has been moved.")

    result["err_str"] = form.errors
    return jsonify(result)


@api.route("/upload/", methods=["POST"])
def upload():
    """
    上传图片用于训练
    :return:
    """
    form = CaptchaUploadForm(CombinedMultiDict([request.form, request.files]))
    if form.validate():
        # 公用项
        img_bytes = form.captcha.data.stream.read()
        # 自家验证码必备项
        website = form.website.data
        max_captcha = form.max_captcha.data
        char_set = form.char_set.data
        captcha_str = form.captcha_str.data

        recognizer_key = make_recognizer_key(website, max_captcha, char_set)

        file_name = make_pic_name_for_train(captcha_str)

        train_path = os.path.join(CAPTCHA_TRAIN_FOLDER, recognizer_key)
        if not os.path.isdir(train_path):
            os.mkdir(train_path)
        file_path = os.path.join(train_path, file_name)
        with open(file_path, "wb") as f:
            f.write(img_bytes)
    return jsonify({
        "err_code": 200,
        "err_str": form.errors
    })


@api.route("/train/", methods=["POST"])
def train():
    config = CAPTCHA_CONFIG.copy()

    result_text = {}

    timestamp = datetime.datetime.now().timestamp()     # 当前时间
    for file in os.listdir(CAPTCHA_UPLOAD_FOLDER):          # 从打码文件夹拿出符合条件的图片
        path = os.path.join(CAPTCHA_UPLOAD_FOLDER, file)
        at_time = os.path.getatime(path)
        difference = int(timestamp - at_time)
        if difference > 60:         # 创建时间大于xx的
            recognizer_key, md5, pic_str = parse_pic_name(file)     # 放入指定训练集
            train_image_dir = os.path.join(CAPTCHA_TRAIN_FOLDER, recognizer_key)
            if not os.path.isdir(train_image_dir):
                os.mkdir(train_image_dir)
            re_file = make_pic_name_for_train(pic_str)
            re_path = os.path.join(train_image_dir, re_file)
            shutil.move(path, re_path)

    for dirname in os.listdir(CAPTCHA_TRAIN_FOLDER):
        # 训练集
        train_image_dir = os.path.join(CAPTCHA_TRAIN_FOLDER, dirname)       # 训练集文件夹
        # 验证集
        if not os.path.isdir(CAPTCHA_TEST_FOLDER):
            os.mkdir(CAPTCHA_TEST_FOLDER)
        verify_image_dir = os.path.join(CAPTCHA_TEST_FOLDER, dirname)       # 验证集文件夹
        if not os.path.isdir(verify_image_dir):
            os.mkdir(verify_image_dir)
        length_train = len(os.listdir(train_image_dir))
        if length_train < 8:
            result_text[dirname] = "No enough pic."
            continue
        if len(os.listdir(verify_image_dir)) < int(length_train / 8):
            pic_names = os.listdir(train_image_dir)[-int(length_train / 8):]
            for pic_name in pic_names:
                shutil.move(
                    os.path.join(train_image_dir, pic_name),
                    os.path.join(verify_image_dir, pic_name)
                )
        # 更改图片大小
        for dir_path in [train_image_dir, verify_image_dir]:
            for file in os.listdir(dir_path):
                abs_path = os.path.join(dir_path, file)
                try:
                    img = Image.open(abs_path)
                except UnidentifiedImageError:
                    os.remove(abs_path)
                    continue
                img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
                img.save(abs_path)
        website, max_captcha, char_set = parse_recognizer_key(dirname)
        char_set = CHAR_SET.get(char_set) or CHAR_SET[DEFAULT_CHAR_SET]
        model_save_name = f"{dirname}.ckpt"  # 模型保存名称
        cycle_stop = len(os.listdir(train_image_dir))  # 多少轮次后停止
        if not cycle_stop:
            continue
        config.update(dict(
            train_img_path=train_image_dir,
            verify_img_path=verify_image_dir,
            char_set=char_set,
            model_save_name=model_save_name,
            cycle_stop=cycle_stop,
        ))
        try:
            tm = TrainModel(**config)
            acc_image = tm.train_cnn()
            for dir_path in [train_image_dir, verify_image_dir]:
                for file in os.listdir(dir_path):
                    abs_path = os.path.join(dir_path, file)
                    os.remove(abs_path)
            result_text[dirname] = f"Estimated success rate {acc_image}."
        except TrainError:
            result_text[dirname] = "No enough pic."
    return {
        "err_code": 200,
        "err_str": result_text,
    }


@api.route("/reload/", methods=["PUT"])
def reload_pak():
    reload(captcha_reader)
    return {
        "err_code": 200,
    }


@api.route("/valid/", methods=["POST"])
def valid_captcha():
    """
    打码认证
    :return:
    """
    form = CaptchaValidForm(request.form)
    if form.validate():
        # 名称更改为   label_timestamp_website.png
        filename = form.filename.data
        captcha_str = form.captcha_str.data

        prefix = os.path.split(filename)[-1].split(".")[0]
        recognizer_key, md5, pic_str = parse_pic_name(prefix)
        # website, max_captcha, char_set = parse_recognizer_key(recognizer_key)

        rename = make_pic_name_for_train(captcha_str)

        filepath = os.path.join(CAPTCHA_REPORT_FOLDER, filename)
        if os.path.isfile(filepath):
            train_path = os.path.join(CAPTCHA_TRAIN_FOLDER, recognizer_key)
            if not os.path.isdir(train_path):
                os.mkdir(train_path)
            filepath_mv = os.path.join(train_path, rename)
            shutil.move(filepath, filepath_mv)
    return jsonify({
        "err_code": 200,
        "err_str": form.errors
    })
