# 新生安全教育脚本(安全微伴脚本，麦课在线教育脚本, weiban.mycourse.cn脚本)

### Installation

使用前请确保你的电脑安装了git和python。如果没有git，你可以手动复制仓库源码。但是一定要安装python！！！

```bash
git clone git@github.com:Lenzhzh/fuck-weiban.git
pip install playwright tqdm
playwright install
```

国内用户可能会遇到网络问题，可以在执行 `playwright install` 前设置镜像加速：

- Windows: `set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`
- Mac/Linux: `export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`

如果你的电脑（Windows系统下）提示  `playwright` 不是一个命令，可以采用以下命令：

```bash
python -m playwright install
```

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
[油叉挂考试脚本](https://greasyfork.org/zh-CN/scripts/544879-%E5%AE%89%E5%85%A8%E5%BE%AE%E4%BC%B4-2025-08-%E5%8F%AF%E5%88%B7%E8%AF%BE%E7%A8%8B-by-%E6%B5%A9%E5%8A%AB%E8%80%8512345-modified-by-houtar/code)

### 提醒

1. 间隔过快，请求会被系统拒绝，我的测试是 10s 一定会被拒绝，15s 总是能通过，如果你遇到问题，可以考虑修改代码改大此值
3. 系统不允许重复登录，脚本运行时不要再打开这个网站
4. 默认会保存 cookie 等信息在 `state.json` 文件里，请注意隐私保护

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=panjd123/fuck-weiban&type=Date)](https://star-history.com/#panjd123/fuck-weiban&Date)
