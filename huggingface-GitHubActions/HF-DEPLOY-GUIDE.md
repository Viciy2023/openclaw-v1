# HuggingFace Spaces 部署指南

## ✅ 前置条件

- [x] GitHub Actions 已成功构建镜像：`viciy2026/openclaw-viciy2026:latest`
- [ ] 已在 Supabase 上传配置文件
- [ ] 已创建 HuggingFace Space

## 📁 需要上传到 HF Spaces 的文件

### 文件清单

| 本地文件 | HF Spaces 文件名 | 说明 |
|---------|-----------------|------|
| `huggingface-GitHubActions/Dockerfile-hf` | `Dockerfile` | 容器构建文件 |
| `huggingface-new/entrypoint.sh-supabase` | `entrypoint.sh` | 容器启动脚本 |
| `huggingface-new/README.md` | `README.md` | 说明文档（可选） |

### ⚠️ 注意事项

1. **不要上传 `deploy-to-hf.sh`**
   - 这是本地辅助脚本，不是容器启动脚本
   - 容器启动脚本是 `entrypoint.sh-supabase`

2. **文件必须重命名**
   - `Dockerfile-hf` → `Dockerfile`
   - `entrypoint.sh-supabase` → `entrypoint.sh`

## 🚀 部署步骤

### 步骤 1：准备文件

在本地创建临时文件夹并复制文件：

```bash
# Windows PowerShell
mkdir hf-deploy
Copy-Item huggingface-GitHubActions\Dockerfile-hf hf-deploy\Dockerfile
Copy-Item huggingface-new\entrypoint.sh-supabase hf-deploy\entrypoint.sh
Copy-Item huggingface-new\README.md hf-deploy\README.md
```

或者使用 Git Bash：

```bash
mkdir hf-deploy
cp huggingface-GitHubActions/Dockerfile-hf hf-deploy/Dockerfile
cp huggingface-new/entrypoint.sh-supabase hf-deploy/entrypoint.sh
cp huggingface-new/README.md hf-deploy/README.md
```

### 步骤 2：上传配置文件到 Supabase

确保以下文件已上传到 Supabase Storage（Private Bucket）：

```
supabase-bucket/
├── .env                          # 环境变量配置
├── openclaw.json                 # OpenClaw 配置
├── patches/
│   └── clawmate/
│       ├── companion.ts
│       ├── maggie-character.ts
│       └── ...
├── characters/
│   └── maggie/
│       ├── images/
│       └── ...
├── AGENTS.md                     # Agent 配置
├── TOOLS.md                      # 工具配置
└── ...其他配置文件
```

### 步骤 3：配置 HF Spaces Secrets

在 HuggingFace Spaces 设置页面添加以下 Secrets：

1. **SUPABASE_ANON_KEY**
   - 值：你的 Supabase 匿名密钥
   - 获取位置：Supabase Project Settings → API → anon public

2. **DEPLOY_FILES_BASE_URL**
   - 值：Supabase 文件存储的基础 URL
   - 格式：`https://xxx.supabase.co/storage/v1/object/your-bucket-name`
   - 示例：`https://abcdefgh.supabase.co/storage/v1/object/hf-deploy`

### 步骤 4：推送到 HF Spaces

#### 方法 1：使用 Git（推荐）

```bash
cd hf-deploy

# 初始化 Git 仓库（如果还没有）
git init

# 添加 HF Spaces 远程仓库
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# 添加文件
git add Dockerfile entrypoint.sh README.md

# 提交
git commit -m "Initial deployment with prebuilt image"

# 推送
git push origin main
```

#### 方法 2：使用 HF Web UI

1. 访问你的 HF Space
2. 点击 "Files" 标签
3. 点击 "Add file" → "Upload files"
4. 上传 `Dockerfile`、`entrypoint.sh`、`README.md`
5. 点击 "Commit changes to main"

### 步骤 5：等待构建

推送后，HF Spaces 会自动：
1. 拉取预构建镜像：`viciy2026/openclaw-viciy2026:latest`
2. 添加 `entrypoint.sh` 启动脚本
3. 启动容器
4. 容器启动时会从 Supabase 下载配置文件

构建时间：约 5-10 分钟（因为使用了预构建镜像）

## 🔍 验证部署

### 检查构建日志

在 HF Spaces 页面查看 "Logs" 标签，应该看到：

```
=== Downloading deploy files from Supabase ===
✅ Downloaded: .env
✅ Downloaded: openclaw.json
✅ Downloaded: patches/clawmate/companion.ts
...
=== Starting OpenClaw Gateway ===
```

### 检查服务状态

1. 访问 HF Space URL
2. 应该看到 OpenClaw 界面
3. 端口 7860 应该可以访问

## 🐛 故障排查

### 问题 1：镜像拉取失败

**错误信息**：`failed to pull viciy2026/openclaw-viciy2026:latest`

**解决方法**：
- 确认 GitHub Actions 构建成功
- 确认 Docker Hub 仓库是 Public
- 访问 https://hub.docker.com/r/viciy2026/openclaw-viciy2026 确认镜像存在

### 问题 2：Supabase 下载失败

**错误信息**：`❌ Failed: .env` 或 `401 Unauthorized`

**解决方法**：
- 检查 `SUPABASE_ANON_KEY` 是否正确
- 检查 `DEPLOY_FILES_BASE_URL` 格式是否正确
- 确认 Supabase Bucket 权限设置（需要允许匿名读取或使用正确的密钥）

### 问题 3：容器启动失败

**错误信息**：`entrypoint.sh: not found` 或权限错误

**解决方法**：
- 确认 `entrypoint.sh` 文件存在于 HF Spaces 根目录
- 检查文件权限（Dockerfile 中已设置 `chmod +x`）
- 确认文件格式是 Unix 格式（LF），不是 Windows 格式（CRLF）

### 问题 4：端口访问失败

**错误信息**：无法访问 7860 端口

**解决方法**：
- 检查 Dockerfile 中的 `EXPOSE 18789 7860`
- 确认 entrypoint.sh 中启动命令绑定了正确的端口
- HF Spaces 默认使用 7860 端口

## 📚 相关文档

- [HuggingFace Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Docker Hub 镜像](https://hub.docker.com/r/viciy2026/openclaw-viciy2026)
- [GitHub Actions 工作流](https://github.com/Viciy2023/openclaw-v1/actions)

## 🎉 部署成功

如果一切顺利，你应该能够：
1. 访问 HF Space URL 看到 OpenClaw 界面
2. 在日志中看到成功下载配置文件
3. 服务正常运行并响应请求

恭喜！你已经成功部署了 OpenClaw 到 HuggingFace Spaces！
