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



```text
也可以手动下载当前项目，手动复制到目录中：

本地：<项目根目录>/.agents/skills/debug-third-party-api/

全局：~/.codex/skills/debug-third-party-api/
```

推荐使用 Codex 以发挥最佳效果。也可以安装到WorkBuddy等其它Agent尝试。

### 发起调试

开始前提供：

1. 第三方文档地址。
2. 测试环境地址、测试凭据和必要测试数据。
3. 本次需要调试的接口范围。
4. 希望验证的业务场景，可选。

假设包含上述信息的debug文档已经在本地目录中：

```text
/debug-third-party-api @通过弹窗选取<Debug需求文件>
```

读取在线需求文档（需要先配置语雀 Token）：

```text
/debug-third-party-api <需求文档链接>
```

### 配置语雀 Token

把Token配置在机器的环境变量中即可：YUQUE_TOKEN='<your-token>'

```bash
# 参考配置

# 选择一 macOS：让已安装的 Codex 桌面端读取
launchctl setenv YUQUE_TOKEN '<your-token>'

# 选择二 在用户根目录持久化
echo "export YUQUE_TOKEN='<your-token>'" >> ~/.zshrc
source ~/.zshrc

```

## 如何更新

还是让Agent代劳最省力

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
