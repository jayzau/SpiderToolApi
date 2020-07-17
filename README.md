# SpiderTool

## 爬虫工具
`python=3.7`

```shell
git clone https://github.com/jayzau/SpiderTool.git
cd SpiderTool
pip install -r requirement.txt
// 数据库搭建
python manage.py
```

- 验证码识别

基本提供：识别图片/反馈错误识别/上传训练集/识别训练/~~二次识别反馈的图片(人工)~~

核心代码来自 => [nickliqian/cnn_captcha](https://github.com/nickliqian/cnn_captcha)

三方打码平台 => [超级鹰](https://www.chaojiying.com/)
(可用于快速获取带标识的图片)

直接食用 => `library/cnn_captcha/sdk` 
(模型需自己训练)

---

- 小工具

1. `/pages/ua/` UA、IP查看、ChromeDriver检测
2. ~~Chrome/FireFox请求头转换~~
3. ~~各种加密~~

- ~~Cookie池~~

- ~~代理池~~

---

欢迎各路大佬提出建议优化这座shi山~
