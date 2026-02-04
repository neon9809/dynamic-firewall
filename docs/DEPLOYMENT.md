# dynamic-firewall 部署指南

本文档提供了 `dynamic-firewall` 项目的详细部署指南，包括使用 Docker Compose 部署和手动构建部署两种方式。

## 目录

- [使用 Docker Compose 部署（推荐）](#使用-docker-compose-部署推荐)
- [手动构建和部署](#手动构建和部署)
- [UniFi 网关配置](#unifi-网关配置)
- [常见问题](#常见问题)

---

## 使用 Docker Compose 部署（推荐）

这是最简单和推荐的部署方式，适合大多数用户。

### 1. 准备工作

确保您的系统已经安装了以下软件：

- **Docker**: [安装指南](https://docs.docker.com/get-docker/)
- **Docker Compose**: [安装指南](https://docs.docker.com/compose/install/)

### 2. 下载项目

```bash
git clone https://github.com/neon9809/dynamic-firewall.git
cd dynamic-firewall
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填入您的敏感信息：

```bash
cp .env.example .env
nano .env  # 或使用您喜欢的编辑器
```

在 `.env` 文件中填入以下信息：

```dotenv
# AbuseIPDB API Key (如果启用 abuseipdb 采集器)
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here

# UniFi API Token (如果启用 unifi 同步器)
UNIFI_API_TOKEN=your_unifi_api_token_here
```

### 4. 配置应用

编辑 `config/config.yaml` 文件，根据您的需求进行配置。

**最重要的配置项**：

```yaml
syncers:
  unifi:
    enabled: true
    api_url: "https://api.ui.com"  # 云端使用此地址
    api_token: "${UNIFI_API_TOKEN}"  # 从 .env 读取
    site_id: "your_site_id"  # 您的 Site ID
```

### 5. 启动服务

使用 Docker Compose 启动服务：

```bash
docker-compose up -d
```

服务将在后台运行。

### 6. 查看日志

查看服务运行日志：

```bash
docker-compose logs -f
```

按 `Ctrl+C` 退出日志查看。

### 7. 停止服务

```bash
docker-compose down
```

### 8. 更新服务

当有新版本发布时，更新服务：

```bash
docker-compose pull
docker-compose up -d
```

---

## 手动构建和部署

如果您希望从源代码构建 Docker 镜像，可以使用以下方式。

### 1. 克隆项目

```bash
git clone https://github.com/neon9809/dynamic-firewall.git
cd dynamic-firewall
```

### 2. 构建 Docker 镜像

```bash
docker build -t dynamic-firewall:latest .
```

### 3. 运行容器

```bash
docker run -d \
  --name dynamic-firewall \
  --restart unless-stopped \
  -e UNIFI_API_TOKEN="your_api_token" \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/data:/app/data \
  dynamic-firewall:latest
```

### 4. 查看日志

```bash
docker logs -f dynamic-firewall
```

### 5. 停止容器

```bash
docker stop dynamic-firewall
docker rm dynamic-firewall
```

---

## UniFi 网关配置

`dynamic-firewall` 通过 UniFi Network API 来管理防火墙规则。以下是配置步骤：

### 1. 获取 UniFi API Token

#### 步骤 1: 登录 UniFi Site Manager

访问 [unifi.ui.com](https://unifi.ui.com/) 并登录您的账号。

#### 步骤 2: 创建 API Key

1. 点击右上角的设置图标
2. 选择 **Settings** → **API Keys**（或在 GA 版本中选择 **API** 部分）
3. 点击 **Create New API Key**
4. 复制生成的 API Key 并安全保存（**只显示一次**）

### 2. 获取 Site ID

您的 Site ID 可以从 UniFi Site Manager 的 URL 中获取：

- 例如，如果您的 URL 是：`https://unifi.ui.com/sites/abc123def456/dashboard`
- 那么您的 `site_id` 就是：`abc123def456`

### 3. 配置 `config.yaml`

在 `config/config.yaml` 中配置 UniFi 同步器：

```yaml
syncers:
  unifi:
    enabled: true
    
    # 云端 UniFi 使用此地址
    api_url: "https://api.ui.com"
    
    # 如果使用本地控制器，使用类似以下地址：
    # api_url: "https://192.168.1.1:8443"
    
    # 您的 API Token
    api_token: "${UNIFI_API_TOKEN}"
    
    # 您的 Site ID
    site_id: "abc123def456"
    
    # 防火墙地址组名称
    group_name: "d-firewall-blacklist"
    
    # 云端使用 true，本地自签名证书使用 false
    verify_ssl: true
```

### 4. 验证防火墙规则

启动服务后，登录 UniFi Site Manager，导航到 **Settings → Security → Firewall**，您应该能看到：

- 一个名为 `d-firewall-blacklist` 的地址组，包含了恶意 IP 列表。

### 5. 创建防火墙规则（可选）

`dynamic-firewall` 只负责更新地址组，您可以手动创建防火墙规则来使用这个地址组：

1. 在 UniFi 控制器中，进入 **Settings → Security → Firewall**
2. 点击 **Create New Rule**
3. 配置规则：
   - **Type**: Internet In 或 LAN In（根据需求）
   - **Action**: Drop
   - **Source**: 选择 `d-firewall-blacklist` 地址组
   - **Destination**: Any
4. 保存规则

---

## 常见问题

### 1. 如何验证服务是否正常运行？

查看日志：

```bash
docker-compose logs -f
```

正常运行时，您应该看到类似以下的日志：

```
2026-02-03 08:00:00 - engine - INFO - Starting dynamic-firewall engine...
2026-02-03 08:00:01 - collector.ipsum - INFO - Successfully fetched 1234 IPs (min_score=3)
2026-02-03 08:00:02 - syncer.unifi - INFO - Successfully synced to unifi
```

### 2. 如何更改更新频率？

在 `config/config.yaml` 中修改 `global.update_interval` 参数（单位：秒）：

```yaml
global:
  update_interval: 3600  # 每小时更新一次
```

修改后重启服务：

```bash
docker-compose restart
```

### 3. 如何启用更多的数据源？

在 `config/config.yaml` 中启用相应的采集器：

```yaml
collectors:
  ipsum:
    enabled: true
  abuseipdb:
    enabled: true  # 启用 AbuseIPDB
    api_key: "${ABUSEIPDB_API_KEY}"
  cncert:
    enabled: true  # 启用 CNCERT
```

确保在 `.env` 文件中提供了必要的 API 密钥。

### 4. 如何查看数据库中的 IP 数量？

查看日志中的统计信息，或者直接查询 SQLite 数据库：

```bash
docker exec -it dynamic-firewall sqlite3 /app/data/ips.db "SELECT COUNT(*) FROM malicious_ips;"
```

### 5. UniFi 同步失败怎么办？

**可能的原因**：

- API Token 无效或过期
- Site ID 错误
- API URL 错误
- 网络连接问题

**解决方法**：

1. 确认 API Token 正确且有效
2. 确认 Site ID 正确（从 URL 中获取）
3. 确认 `api_url` 正确（云端使用 `https://api.ui.com`）
4. 查看详细日志：

```bash
docker-compose logs -f
```

### 6. 如何手动触发一次更新？

重启服务会立即触发一次更新：

```bash
docker-compose restart
```

或者进入容器手动执行：

```bash
docker exec -it dynamic-firewall python /app/app/main.py --once
```

### 7. 数据会持久化吗？

是的，数据库文件存储在 `./data/ips.db`，通过 Docker 卷挂载，即使容器重启也不会丢失数据。

### 8. 如何备份数据？

直接备份 `data` 目录：

```bash
cp -r data data_backup_$(date +%Y%m%d)
```

### 9. 本地 UniFi 控制器如何配置？

如果您使用本地部署的 UniFi 控制器（如 UniFi Dream Machine），配置如下：

```yaml
syncers:
  unifi:
    enabled: true
    api_url: "https://192.168.1.1"  # 您的控制器 IP
    api_token: "${UNIFI_API_TOKEN}"
    site_id: "default"  # 通常是 default
    verify_ssl: false  # 自签名证书使用 false
```

**注意**：本地控制器可能需要使用不同的 API 端点格式，具体请参考 UniFi 官方文档。

---

## 高级配置

### 自定义最小置信度分数

在 `config.yaml` 中设置 `global.min_score`，只有分数大于等于此值的 IP 才会被同步到防火墙：

```yaml
global:
  min_score: 5  # 只同步出现在 5 个或以上黑名单的 IP
```

### 定期清理旧数据

目前项目不会自动清理旧数据。如果需要，可以手动清理：

```bash
docker exec -it dynamic-firewall sqlite3 /app/data/ips.db \
  "DELETE FROM malicious_ips WHERE last_seen < datetime('now', '-30 days');"
```

---

## 技术支持

如果您在部署过程中遇到问题，请：

1. 查看 [常见问题](#常见问题) 部分。
2. 查看项目的 [Issues](https://github.com/neon9809/dynamic-firewall/issues)。
3. 提交新的 Issue 并提供详细的日志信息。

---

**祝您部署顺利！**
