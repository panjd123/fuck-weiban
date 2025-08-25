# 新生安全教育脚本(安全微伴脚本，麦课在线教育脚本, weiban.mycourse.cn脚本)

### Installation

脚本基于 `python` 编写，所以首先你需要自行安装 `python`

随后在命令行中执行

```bash
pip install playwright tqdm python-dotenv zai-sdk
playwright install
```

国内用户可能会遇到网络问题，可以在执行 `playwright install` 前设置镜像加速：

- Windows: `set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`
- Mac/Linux: `export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`

### Run

#### 刷课脚本

```bash
python course.py
```

1. 运行后会弹出一个浏览器，**先不要操作**
2. 观察终端，等待其输出"xxxx，按任意键开始..."字样的指示后再开始操作
3. 按照指示操作后，回到终端，输入回车
4. 等待脚本自动结束
5. 如果遇到问题，可以尝试改大代码里的 `WAITING_SECS`

#### 考试脚本（新）

该脚本会调用智谱轻言GLM-4.5-flash大模型来自动选择正确的答案，其是免费的，但你需要自己注册获取 API_KEY，以下是简易流程

1. 进入智谱开放平台 [https://bigmodel.cn/](https://bigmodel.cn/)
2. 右上角注册/登录
3. 右上角进入控制台
4. 右上角进入 API KEY
6. 右上角添加新的 API KEY
7. 在下方找到添加的 API KEY，鼠标移动上去复制

如果你需要图片教程，请前往 [imgs/](imgs/) 查看

-----------------------------------------------

然后你需要据此配置 `.env` 文件，默认是不存在这个文件的，你需要自己创建，注意其不含任何后缀名，你可以简单地通过样例文件初始化

```bash
cp .env.example .env
```

其默认配置如下：

```
ZAI_API_KEY=your_zai_api_key
thinking=disabled
```

你需要替换 `your_zai_api_key` 为你刚刚获取到的 API KEY。

另外，GLM-4.5-flash 可以开启或关闭思维链（深度思考），实测思考模式的耗时是非思考模式的 5-10 倍，但是开启思维链回答的正确率会高一点，非思考有考试不通过的可能，如果你不着急，我建议开启思考，即将 `disabled` 改为 `enabled`。

----------------------------------------------

```bash
python exam.py
```

注意事项是一致的：

1. 运行后会弹出一个浏览器，**先不要操作**
2. 观察终端，等待其输出"xxxx，按任意键开始..."字样的指示后再开始操作
3. 按照指示操作后，回到终端，输入回车
4. 等待脚本自动结束

### 参考资料

[利用js快速完成大学生新生安全教育课程 by Honyelchak](https://blog.csdn.net/m0_38072683/article/details/118878085)

### 提醒

1. 刷课间隔过快，请求会被系统拒绝，我的测试是 10s 一定会被拒绝，15s 总是能通过，如果你遇到问题，可以考虑修改代码改大此值
3. 系统不允许重复登录，脚本运行时不要再打开这个网站
4. 默认会保存 cookie 等信息在 `state.json` 文件里，请注意隐私保护

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=panjd123/fuck-weiban&type=Date)](https://star-history.com/#panjd123/fuck-weiban&Date)
