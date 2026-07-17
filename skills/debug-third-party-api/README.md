# 第三方 API 调试

用真实测试环境核对第三方 API 文档，并生成便于接入、评审和沟通的单文件 HTML 报告。

## 如何使用

### 项目级别安装

把以下提示交给 Codex：

```text
使用 $skill-installer，把这个 Skill 安装到当前项目的
.agents/skills/debug-third-party-api：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

如果默认下载遇到本机 SSL 证书错误，请改用安装器的 Git 模式，
不要关闭 TLS 校验。
```

本地安装只对当前项目生效。

### 用户全局安装

```text
使用 $skill-installer，全局安装这个 Skill：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

如果默认下载遇到本机 SSL 证书错误，请改用安装器的 Git 模式，
不要关闭 TLS 校验。
```

全局安装对所有项目生效。安装后从下一轮对话开始可用；未出现时重启 Codex。

也可以直接复制目录：

```text
本地：<项目根目录>/.agents/skills/debug-third-party-api/
全局：~/.codex/skills/debug-third-party-api/
```

你想使用WorkBuddy等其他Agent？skill本身并不绑定环境，把地址扔给Agent自己安装即可。为了效果最佳，推荐 Codex

### 运行条件

- Codex 桌面端、CLI 或 IDE 扩展。
- Python 3.10+。
- 读取语雀私有文档时需要 `YUQUE_TOKEN`。
- 供应商指定 SDK 或密码学算法时需要相应依赖。

### 发起调试

开始前提供：

1. 第三方文档地址。
2. 测试环境地址、测试凭据和必要测试数据。
3. 本次需要调试的接口范围。
4. 希望验证的业务场景，可选。

假设你将上述信息放入了Debug需求文档中，该文档在本地目录中：

```text
/debug-third-party-api @通过弹窗选取<Debug需求文件>
```

读取在线需求文档（需要先配置语雀 Token）：

```text
/debug-third-party-api <需求文档链接>
```

### 配置语雀 Token

#### macOS：让已安装的 Codex 桌面端读取

如果 Codex 是从访达或 Dock 启动的，可以为当前 macOS 登录会话设置：

```bash
launchctl setenv YUQUE_TOKEN '<your-token>'
```

#### 命令行方式配置

macOS / Linux 当前会话生效：

```bash
# 添加
export YUQUE_TOKEN='<your-token>'

# 删除
unset YUQUE_TOKEN
```

如果不想每次都配置，可以选择在用户根目录持久化：

```bash
# 添加
echo "export YUQUE_TOKEN='<your-token>'" >> ~/.zshrc
source ~/.zshrc

# 删除
sed -i.bak '/^export YUQUE_TOKEN=/d' ~/.zshrc
rm ~/.zshrc.bak
unset YUQUE_TOKEN
```

默认终端使用 bash 时，将 `~/.zshrc` 换成 `~/.bashrc`。

如何判断你的默认终端
```bash
echo $SHELL
> /bin/zsh
```

## 如何更新

更新本地安装：

```text
更新当前项目的 debug-third-party-api：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

用 GitHub main 的最新版本替换
<项目根目录>/.agents/skills/debug-third-party-api，不要修改其他 Skill。
```

更新全局安装：

```text
更新全局 debug-third-party-api：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

用 GitHub main 的最新版本替换
~/.codex/skills/debug-third-party-api，不要修改其他 Skill。
```

GitHub `main` 是发布源。更新后从下一轮对话开始生效；Skill命令未出现时重启 Codex。

## 如何卸载

卸载本地安装：

```text
卸载当前项目的 debug-third-party-api，只删除：
<项目根目录>/.agents/skills/debug-third-party-api
```

卸载全局安装：

```text
卸载全局 debug-third-party-api，只删除：
~/.codex/skills/debug-third-party-api
```

手动卸载时，删除对应目录即可。卸载后重新开启任务；仍然出现时重启 Codex。

## 结构

```text
debug-third-party-api/
├── SKILL.md                 # 核心要求
├── README.md                # 使用说明
├── agents/                  # Codex 界面信息
├── assets/                  # 报告模板
├── references/              # 规则
└── scripts/                 # 工具
```
