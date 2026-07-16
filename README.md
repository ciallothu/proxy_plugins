# proxy_plugins

Surge / Egern 外部模块、脚本与规则依赖的自托管镜像。

## 目录

- `modules/`：配置直接引用的模块文件。
- `scripts/widgets/`：Egern 小组件脚本。
- `scripts/vendor/`：模块内嵌的 `script-path` / `script_url` 依赖。
- `rules/vendor/`：模块内嵌的远程规则依赖。
- `audit/SECURITY_AUDIT.md`：安全审计结论。
- `MANIFEST.json`：来源、SHA-256、大小与同步时间。
- `tools/sync_plugins.py`：可复现同步与 URL 重写脚本。

## 使用条件

远程配置客户端不能匿名读取 GitHub 私有仓库内容。本仓库必须为 **Public**，配置中的 `raw.githubusercontent.com` URL 才能直接工作。不要向本仓库提交订阅令牌、API Key、MITM CA 私钥或其他凭据。

## 更新

GitHub Actions 每日同步一次，也可在 Actions 页面手动运行 `Sync plugins`。

## 上游与许可证

所有文件保留原作者头部和来源记录。各文件仍受各自上游许可证与版权条款约束；本仓库不对第三方代码重新授权。
