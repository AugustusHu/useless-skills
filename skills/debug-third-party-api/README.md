# 第三方 API 调试

用真实测试环境核对第三方 API 文档，并生成便于接入、评审和沟通的单文件 HTML 报告。

## 如何使用

### 安装

把以下提示交给 Codex：

```text
使用 $skill-installer 安装：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

如果默认下载遇到 SSL 证书错误，改用安装器的 Git 模式；
不要关闭 TLS 校验。
```

Skill 默认安装到 `~/.codex/skills/debug-third-party-api`，从下一轮对话开始可用；未出现时重启 Codex。

### 运行条件

- Codex 桌面端、CLI 或 IDE 扩展。
- Python 3.10+；无需安装 Python 第三方包，也不依赖 Node.js、Java、数据库或本地 Web 服务。
- 能访问第三方文档和测试环境的网络。
- 真实调试所需的测试地址、凭据和测试数据。
- 测试回调时需要可接收回调的地址；读取语雀私有文档时需要 `YUQUE_TOKEN`。

供应商专用 SDK 或额外密码学依赖不属于固定环境。确有需要时，由 Codex 说明用途并申请安装。

### 发起调试

提供四项信息：

1. 第三方文档地址。
2. 测试环境信息。
3. 本次接口范围。
4. 测试场景，可选。

```text
使用 $debug-third-party-api：

- 文档：<文档地址>
- 测试环境：<Sandbox 地址和凭据位置>
- 接口范围：<接口列表>
- 测试场景：<可选>
```

如果这些信息已经写在语雀文档中，直接提供文档链接即可。测试凭据应放在环境变量或安全文件中，不要写入需求文档。

### 配置语雀 Token

只有读取语雀私有文档时需要。脚本优先读取环境变量 `YUQUE_TOKEN`。

macOS / Linux 当前终端：

```bash
export YUQUE_TOKEN='<your-token>'
```

需要长期生效时，把同一行加入 `~/.zshrc`、`~/.bashrc` 或 `~/.bash_profile`。

从访达或 Dock 启动 Codex 桌面端时：

```bash
launchctl setenv YUQUE_TOKEN '<your-token>'
```

设置后完全退出并重新打开 Codex；清除时执行 `launchctl unsetenv YUQUE_TOKEN`。

Windows PowerShell 当前窗口：

```powershell
$env:YUQUE_TOKEN = '<your-token>'
```

Windows 当前用户长期生效：

```powershell
[Environment]::SetEnvironmentVariable('YUQUE_TOKEN', '<your-token>', 'User')
```

检查是否生效，不会打印 Token（Windows 通常使用 `python`，macOS / Linux 通常使用 `python3`）：

```bash
python3 -c "import os; print('已设置' if os.getenv('YUQUE_TOKEN') else '未设置')"
```

也可以填写 `scripts/yuque_doc.py` 中的 Token 占位符，但更新会覆盖该值。公开仓库必须保留占位符，不能提交真实 Token。

## 如何更新

把以下提示交给 Codex：

```text
更新 debug-third-party-api：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api

用 GitHub main 的最新版本替换
~/.codex/skills/debug-third-party-api，不要修改其他 Skill。
如果默认下载遇到 SSL 证书错误，改用 Git 模式；不要关闭 TLS 校验。
```

更新从下一轮对话开始生效；未生效时重启 Codex。

维护者以 GitHub `main` 为发布源：

- `SKILL.md`：调试原则和报告要求。
- `references/`：输入、测试和报告规则。
- `assets/report-template.html`：报告样式。
- `scripts/`：报告生成、检查和语雀工具。

发布前用脱敏数据重新生成报告，检查页面、内容和敏感信息处理。

## Skill 能力

- 读取网页、本地文件和语雀文档中的调试需求。
- 实际调用测试环境，核对接口字段、请求、响应和错误行为。
- 标注文档错误、实测差异和建议接入方式。
- 验证鉴权、签名、验签、加密和解密算法。
- 探测金额、手机号、账户号、账户名等金融关键字段。
- 核对日期格式、时区及时间戳类型和精度。
- 验证下单、查询、退款、回调、重发等跨接口场景。
- 展示支持范围、阻塞原因和外部待确认事项。
- 生成一个接口一个页签的 HTML 报告，并隐藏凭据和个人信息。

仅在确认安全的测试环境中执行操作。真实资金、生产数据、外部通知或破坏性操作需要明确授权。

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
