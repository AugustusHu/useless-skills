# 第三方 API 调试

用真实测试环境核对第三方 API 文档，并生成便于接入、评审和沟通的单文件 HTML 报告。

## 如何使用

### 本地安装

把以下提示交给 Codex：

```text
使用 $skill-installer，把这个 Skill 安装到当前项目的
.agents/skills/debug-third-party-api：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api
```

本地安装只对当前项目生效。

### 全局安装

```text
使用 $skill-installer，全局安装这个 Skill：
https://github.com/AugustusHu/useless-skills/tree/main/skills/debug-third-party-api
```

全局安装对所有项目生效。安装后从下一轮对话开始可用；未出现时重启 Codex。

也可以直接复制目录：

```text
本地：<项目根目录>/.agents/skills/debug-third-party-api/
全局：~/.codex/skills/debug-third-party-api/
```

目录结构见文末；`SKILL.md` 必须直接位于 `debug-third-party-api` 目录中。

安装或更新时若默认下载遇到 SSL 证书错误，改用安装器的 Git 模式，不要关闭 TLS 校验。

### 运行条件

- Codex 桌面端、CLI 或 IDE 扩展。
- Python 3.10+。
- 读取语雀私有文档时需要 `YUQUE_TOKEN`。
- 测试回调时需要可接收回调的地址。
- 供应商指定 SDK 或密码学算法时需要相应依赖。

### 发起调试

读取本地需求文件：

```text
使用 $debug-third-party-api，读取这个本地需求文件并执行调试：
<需求文件绝对路径>
```

读取在线需求文档：

```text
使用 $debug-third-party-api，读取这个链接并执行调试：
<需求文档链接>
```

### 配置语雀 Token

macOS / Linux 当前会话：

```bash
# 添加
export YUQUE_TOKEN='<your-token>'

# 删除
unset YUQUE_TOKEN
```

用户根目录持久化（zsh）：

```bash
# 添加
echo "export YUQUE_TOKEN='<your-token>'" >> ~/.zshrc
source ~/.zshrc

# 删除
sed -i.bak '/^export YUQUE_TOKEN=/d' ~/.zshrc
rm ~/.zshrc.bak
unset YUQUE_TOKEN
```

使用 bash 时，将 `~/.zshrc` 换成 `~/.bashrc`。

配置后重启 Codex。不要把真实 Token 写入公开仓库。

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

GitHub `main` 是发布源。更新后从下一轮对话开始生效；未出现时重启 Codex。

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
