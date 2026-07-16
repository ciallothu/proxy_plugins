# proxy_plugins

Surge / Egern 外部模块、脚本与规则依赖的自托管镜像。

## 目录

- `modules/`：配置直接引用的模块文件。
- `scripts/widgets/`：Egern 小组件脚本。
- `scripts/vendor/`：模块内嵌的 `script-path` / `script_url` 依赖。
- `rules/vendor/`：模块内嵌的远程规则依赖。
- `audit/SECURITY_AUDIT.md`：安全审计结论。
- `MANIFEST.json`：来源、CDN URL、SHA-256、大小与同步时间。
- `tools/sync_plugins.py`：可复现同步与 URL 重写脚本。

## 使用条件

Surge 与 Egern 通过 jsDelivr 读取本仓库，URL 格式为：

`https://cdn.jsdelivr.net/gh/ciallothu/proxy_plugins@main/<path>`

jsDelivr 只能分发公开 GitHub 仓库，因此本仓库必须为 **Public**。不要向本仓库提交订阅令牌、API Key、MITM CA 私钥、未脱敏客户端配置或其他凭据。

## 更新与缓存

- `Sync plugins` 每日抓取一次上游，并把变化提交到草稿 PR；审核后才合并到 `main`。
- `Purge jsDelivr cache` 在 `main` 的镜像文件变化后逐个刷新 `MANIFEST.json` 中记录的 CDN URL。
- 仓库从 Private 改成 Public 后，需要手动运行一次 `Purge jsDelivr cache`。
- 生产环境也可以使用具体 commit SHA 替代 `@main`，获得不可变内容；使用 `@main` 时依赖缓存刷新工作流及时生效。

## 上游与许可证

所有文件保留原作者头部和来源记录。各文件仍受各自上游许可证与版权条款约束；本仓库不对第三方代码重新授权。
