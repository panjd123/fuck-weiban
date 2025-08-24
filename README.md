# 新生安全教育脚本(安全微伴脚本，麦课在线教育脚本, weiban.mycourse.cn脚本)

### Installation

```bash
pip install playwright tqdm
playwright install
```

国内用户可能会遇到网络问题，可以在执行 `playwright install` 前设置镜像加速：

- Windows: `set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`
- Mac/Linux: `export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`

### Run

```bash
python main.py
```

1. 运行后会弹出一个浏览器，先不要操作
2. 观察终端，等待其输出"xxxx，按任意键开始..."字样的指示后再开始操作
3. 按照指示操作后，回到终端，输入回车
4. 等待脚本自动结束

### 参考资料

[利用js快速完成大学生新生安全教育课程 by Honyelchak](https://blog.csdn.net/m0_38072683/article/details/118878085)

### 提醒

1. 间隔过快，请求会被系统拒绝，我的测试是 10s 一定会被拒绝，15s 总是能通过，如果你遇到问题，可以考虑修改代码改大此值
3. 系统不允许重复登录，脚本运行时不要再打开这个网站
4. 默认会保存 cookie 等信息在 `state.json` 文件里，请注意隐私保护

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=panjd123/fuck-weiban&type=Date)](https://star-history.com/#panjd123/fuck-weiban&Date)
