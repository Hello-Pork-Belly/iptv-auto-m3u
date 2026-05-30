# iptv-auto-m3u

这是一个极简的、无需 VPS 和服务器部署的 IPTV 直播源自动生成器。
本方案完全依赖 GitHub Actions 定时运行，实现远程多源抓取、过滤、测速去重，并生成最终可供播放器直读的 `.m3u` 播放列表。

## 🎯 项目定位
- ❌ **无 VPS、无 Docker**：完全免费托管在 GitHub。
- ❌ **不转发直播流、不做代理**：只做 URL 的静态文本处理。
- ❌ **无复杂数据库或 Web 服务**：纯 Python 脚本 + 文本配置。
- ✅ **极简自动化**：每天两次定时生成静态文件。

## ⚙️ 如何工作

1. 读取 `config/channels.txt` 获取你需要的频道白名单。
2. 读取 `config/local.m3u` 导入你手动维护的高优先级稳定源。
3. 读取 `config/sources.txt` 从远端抓取开源列表。
4. 过滤非白名单频道、去重、发起轻量 HTTP 检测踢除无效链接。
5. 最终生成 `output/result.m3u`。

## 🚀 播放器如何使用

生成的播放列表可直接作为订阅链接添加进任何支持 m3u 的播放器（如 TVBox, Jellyfin, APTV, Infuse, Kodi）：

```text
https://raw.githubusercontent.com/<你的GitHub用户名>/iptv-auto-m3u/main/output/result.m3u
```
*(注意：请将 `<你的GitHub用户名>` 替换为实际用户名)*

## 🛠️ 如何配置与修改

你只需要在 GitHub 页面上直接编辑 `config` 目录下的三个文件即可：

- **`config/channels.txt`**：在这里写入你想要的频道（支持 `#` 注释，空行忽略）。
- **`config/sources.txt`**：在这里贴入第三方的 m3u 或 txt 直播源链接。
- **`config/local.m3u`**：如果你有自己抓取的不易失效的链接，按 m3u 格式写在这里，优先级最高。

## ⚡ 如何手动触发运行

1. 进入当前仓库的 **Actions** 标签页。
2. 在左侧选择 **Build IPTV Playlist**。
3. 点击右侧的 **Run workflow** 按钮。
4. 几分钟后，运行完成，仓库会自动新增一条 `Update IPTV playlist` 的 Commit。

## ⚠️ 免责与安全声明

- **本项目不提供任何真实有效直播源**：默认配置均为空白或示例 URL，需要用户自行提供订阅源。
- **开源源不稳定**：由于依赖网络公开抓取的流，GitHub Actions 测试时有效，不代表你家里播放时有效，也无法保证长久稳定。它也不是实时流媒体转发服务。
- **合规说明**：本项目不抓取需要登录的内容，不突破地区限制，不内置任何侵权盗版视频，仅为个人自动化整理公开链接的编程示例。
