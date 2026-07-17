# 第三方 API 调试

这个 Skill 用真实测试环境核对第三方 API 文档，并生成便于接入、评审和沟通的单文件 HTML 调试报告。

## 如何使用

### 安装

仓库发布到 GitHub 后，直接把下面的地址交给 Codex：

```text
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api
```

安装提示词：

```text
使用 $skill-installer 安装这个 Skill：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api
```

Codex 会下载并安装到 `~/.codex/skills/debug-third-party-api`。安装完成后，从下一轮对话开始使用；如果没有出现，重启 Codex。

安装前需要确认 GitHub 的 `main` 分支已经包含这个目录。公开仓库不需要 GitHub Token。

### 运行环境

基础功能安装后即可运行，不需要执行 `pip install`。随附脚本只使用 Python 标准库，生成的 HTML 也不依赖外部 CDN。

需要的基础环境：

- Codex 桌面端、CLI 或 IDE 扩展。
- Python 3.10 或更高版本。
- 能访问第三方文档和测试环境的网络。
- 本次调试需要的测试地址、测试凭据和测试数据。
- 读取语雀私有文档时需要 `YUQUE_TOKEN`。

不要求 Node.js、npm、Java、数据库或本地 Web 服务。

`curl`、OpenSSL 和第三方 SDK 不是 Skill 的固定依赖。遇到供应商专用 SDK、证书格式或 Python 标准库无法完成的加解密算法时，Codex 会说明缺少什么，并在安装额外依赖前征求授权。

因此，“安装即可运行”适用于文档分析、公开文档读取和报告生成；读取私有语雀文档需要 Token，完成真实接口调用还需要可访问的测试环境和有效测试凭据，测试回调时还需要可接收回调的地址。

### 准备信息

开始前提供：

1. 第三方文档地址。
2. 测试环境地址、测试凭据和必要测试数据。
3. 本次需要调试的接口范围。
4. 希望验证的业务场景，可选。

测试凭据可以通过环境变量或安全文件提供，不要写进需求文档。

### 发起任务

```text
使用 $debug-third-party-api 调试以下第三方接口：

- 文档：<文档地址>
- 测试环境：<Sandbox 地址和凭据位置>
- 接口范围：<接口列表>
- 测试场景：<可选>
```

如果调试信息已经写在语雀文档中，也可以直接提供语雀链接。

### 配置语雀 Token

只有读取语雀私有文档时才需要 Token。脚本会优先读取环境变量 `YUQUE_TOKEN`；未设置环境变量时，才会读取 `scripts/yuque_doc.py` 中预留的占位符。

#### macOS / Linux：当前终端临时生效

在启动 Codex CLI 的同一个终端执行：

```bash
export YUQUE_TOKEN='<your-token>'
```

这个设置只对当前终端及其启动的程序有效，关闭终端后失效。

检查是否设置成功，但不打印 Token：

```bash
test -n "$YUQUE_TOKEN" && echo "YUQUE_TOKEN 已设置" || echo "YUQUE_TOKEN 未设置"
```

#### macOS / Linux：长期生效

如果使用 zsh，在 `~/.zshrc` 中加入：

```bash
export YUQUE_TOKEN='<your-token>'
```

如果使用 bash，则加入 `~/.bashrc` 或 `~/.bash_profile`。保存后重新打开终端，并重启 Codex。

这种方式会将 Token 以明文保存在本机配置文件中。如果不希望长期保存，使用前面的临时设置方式。

#### macOS：让已安装的 Codex 桌面端读取

如果 Codex 是从访达或 Dock 启动的，可以为当前 macOS 登录会话设置：

```bash
launchctl setenv YUQUE_TOKEN '<your-token>'
```

然后完全退出并重新打开 Codex。这个设置通常会在注销或重启后失效。

检查是否已经设置，但不打印 Token：

```bash
test -n "$(launchctl getenv YUQUE_TOKEN)" \
  && echo "YUQUE_TOKEN 已设置" \
  || echo "YUQUE_TOKEN 未设置"
```

不再使用时可以清除：

```bash
launchctl unsetenv YUQUE_TOKEN
```

#### Windows PowerShell：当前窗口临时生效

```powershell
$env:YUQUE_TOKEN = '<your-token>'
```

#### Windows PowerShell：当前用户长期生效

```powershell
[Environment]::SetEnvironmentVariable('YUQUE_TOKEN', '<your-token>', 'User')
```

长期设置后，关闭并重新打开 PowerShell 和 Codex。

#### 直接填写脚本占位符

也可以把 `scripts/yuque_doc.py` 中的：

```python
YUQUE_TOKEN = "PASTE_YOUR_YUQUE_TOKEN_HERE"
```

替换为自己的 Token。环境变量存在时仍然优先使用环境变量。

直接填写安装目录中的脚本后，下一次更新会覆盖 Token。这个仓库也会同步到公开 GitHub，因此不要把填写过真实 Token 的脚本提交或推送；公开版本必须保留占位符。长期使用更适合配置环境变量。

### 查看结果

最终会得到一个可以直接用浏览器打开的 HTML 文件，主要包括：

- 每个接口的字段、请求、响应和错误码。
- 官方文档与真实调用不一致的地方。
- 鉴权、签名、加解密方式及验证结果。
- 支持机构、国家、地区、币种及其他限制。
- 下单、查询、回调等跨接口场景的执行情况。
- 仍需第三方确认的问题及优先级。

报告中的敏感凭据和个人信息会被隐藏。

## 如何更新

GitHub 的 `main` 分支是发布源，本地安装目录不要保存独立修改。

更新时，把同一个 GitHub 地址交给 Codex：

```text
更新已安装的 debug-third-party-api Skill，发布源是：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

请用 GitHub 最新版本替换本机现有安装，只处理
~/.codex/skills/debug-third-party-api；完成后验证 Skill 结构并告诉我结果。
```

`$skill-installer` 不会直接覆盖同名目录，因此更新操作会先替换旧安装，再重新下载。上面的提示词已经把允许替换的范围限制在这个 Skill，不应影响其他 Skill。更新从下一轮对话开始生效；未生效时重启 Codex。

维护者应先修改仓库中的 `skills/debug-third-party-api`，验证后合并并推送到 GitHub `main`，最后再让 Codex 更新本机安装。

常见修改位置：

- 调整调试原则或报告要求：`SKILL.md`
- 调整测试范围和判断规则：`references/`
- 调整报告样式：`assets/report-template.html`
- 调整报告生成或检查逻辑：`scripts/render_report.py`、`scripts/validate_report.py`
- 调整语雀读取与编辑能力：`scripts/yuque_doc.py`

更新后至少使用一份真实或脱敏数据重新生成报告，并在浏览器中检查：

- 所有接口页签能正常切换。
- 请求、响应和字段内容完整可读。
- 文档差异、场景状态和待确认事项表达清楚。
- 页面没有暴露 Token、密钥、个人信息或签名原文。

分享前不要包含：

```text
真实 Token
__pycache__/
*.pyc
.DS_Store
```

## Skill 能力

- 读取普通网页、本地文件和语雀文档中的调试需求。
- 调用第三方测试环境，核对接口字段、请求、响应和错误行为。
- 直接标注文档错误、实测差异和建议接入方式。
- 验证鉴权、签名、验签、加密和解密算法。
- 重点探测金额、手机号、账户号、账户名等金融关键字段。
- 核对日期格式、时区及时间戳的类型和精度。
- 验证下单、查询、退款、回调、重发等跨接口场景。
- 明确展示未执行、无法执行和被外部条件阻塞的测试。
- 生成术语一致、一个接口一个页签的单文件 HTML 报告。

Skill 默认只在确认安全的测试环境中执行操作。涉及真实资金、生产数据、外部通知或破坏性操作时，需要明确授权。

## 结构

```text
debug-third-party-api/
├── SKILL.md                 # 核心能力和执行要求
├── README.md                # 使用和维护说明
├── agents/                  # Codex 界面信息
├── assets/                  # HTML 报告模板
├── references/              # 输入、测试和报告规则
└── scripts/                 # 报告与语雀工具
```
