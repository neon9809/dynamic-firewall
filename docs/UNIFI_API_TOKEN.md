# 如何获取 UniFi API Token

本文档详细说明如何获取 UniFi API Token，用于配置 `dynamic-firewall` 项目。

---

## 方法一：云端 UniFi（推荐）

如果您使用的是 UniFi Cloud（通过 unifi.ui.com 管理），这是最简单的方法。

### 步骤 1: 登录 UniFi Site Manager

访问 [https://unifi.ui.com/](https://unifi.ui.com/) 并使用您的 Ubiquiti 账号登录。

### 步骤 2: 进入 API 设置

1. 点击页面右上角的 **设置图标**（齿轮图标）
2. 在左侧菜单中选择 **API** 或 **API Keys**

### 步骤 3: 创建新的 API Key

1. 点击 **Create New API Key** 按钮
2. 输入一个描述性的名称，例如：`dynamic-firewall`
3. 点击 **Create**

### 步骤 4: 复制 API Token

- 系统会显示生成的 API Token
- **重要**：这个 Token 只会显示一次，请立即复制并安全保存
- 将此 Token 填入 `.env` 文件的 `UNIFI_API_TOKEN` 变量中

### 步骤 5: 获取 Site ID

您的 Site ID 可以从浏览器地址栏的 URL 中获取：

```
https://unifi.ui.com/sites/abc123def456/dashboard
                         ^^^^^^^^^^^^^^
                         这就是您的 Site ID
```

将此 Site ID 填入 `config/config.yaml` 文件的 `site_id` 字段中。

---

## 方法二：本地 UniFi 控制器

如果您使用本地部署的 UniFi 控制器（如 UniFi Dream Machine、Cloud Key），配置方式略有不同。

### 注意事项

**本地控制器的 API 支持可能有限**，建议优先使用云端管理方式。如果必须使用本地控制器，请参考以下步骤：

### 步骤 1: 登录本地控制器

访问您的本地控制器地址，例如：

- UniFi Dream Machine: `https://192.168.1.1`
- Cloud Key: `https://your-cloudkey-ip:8443`

### 步骤 2: 创建本地用户（如果需要）

1. 进入 **Settings** → **Admins**
2. 创建一个专用的管理员账号用于 API 访问
3. 记录用户名和密码

### 步骤 3: 配置说明

**重要**：本地控制器可能不支持 API Token 认证，而是使用传统的 Cookie-based 认证。

如果您的本地控制器版本较旧，可能需要：

1. 使用用户名和密码进行登录认证
2. 使用 `/api/login` 端点获取 session cookie
3. 在后续请求中携带 cookie

**建议**：升级到最新版本的 UniFi Network Application，或考虑迁移到云端管理。

---

## 配置示例

### 云端 UniFi 配置

```yaml
# config/config.yaml

syncers:
  unifi:
    enabled: true
    api_url: "https://api.ui.com"
    api_token: "${UNIFI_API_TOKEN}"  # 从 .env 读取
    site_id: "abc123def456"  # 您的 Site ID
    verify_ssl: true
```

```dotenv
# .env

UNIFI_API_TOKEN=your_actual_api_token_here
```

### 本地控制器配置（如果支持 API Token）

```yaml
# config/config.yaml

syncers:
  unifi:
    enabled: true
    api_url: "https://192.168.1.1"  # 您的控制器 IP
    api_token: "${UNIFI_API_TOKEN}"
    site_id: "default"  # 通常是 default
    verify_ssl: false  # 自签名证书
```

---

## 常见问题

### Q1: API Token 在哪里查看？

API Token 在创建时只显示一次。如果丢失，需要删除旧的 Token 并创建新的。

### Q2: 一个 API Token 可以管理多个 Site 吗？

是的，一个 API Token 可以访问您账号下的所有 Site，但您需要在配置中指定具体的 `site_id`。

### Q3: API Token 会过期吗？

API Token 默认不会过期，除非您手动删除或撤销。

### Q4: 如何撤销 API Token？

1. 登录 [unifi.ui.com](https://unifi.ui.com/)
2. 进入 **Settings** → **API Keys**
3. 找到对应的 Token，点击删除按钮

### Q5: 本地控制器不支持 API Token 怎么办？

建议：

1. 升级到最新版本的 UniFi Network Application
2. 或者迁移到云端管理（免费）
3. 或者等待项目后续版本支持传统认证方式

---

## 安全建议

1. **妥善保管 API Token**：不要将 Token 提交到 Git 仓库或公开分享
2. **使用环境变量**：始终通过 `.env` 文件管理敏感信息
3. **定期轮换**：建议定期更换 API Token
4. **最小权限原则**：如果可能，为 API Token 配置最小必要权限

---

## 参考资源

- [UniFi Network API 官方文档](https://developer.ui.com/)
- [UniFi Site Manager](https://unifi.ui.com/)

---

如有问题，请在项目 GitHub 仓库提交 Issue。
