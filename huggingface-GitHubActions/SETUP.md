# GitHub Actions 和 HuggingFace Spaces 部署设置指南

## 一、GitHub Actions 设置（构建预构建镜像）

### 1. 创建 Docker Hub 仓库
1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击 "Create Repository"
3. 仓库名称：`openclaw-clawmate`
4. 可见性：Public（公开）
5. 点击 "Create"

### 2. 生成 Docker Hub 访问令牌
1. 在 Docker Hub 点击右上角头像 → Account Settings
2. 选择 "Security" → "New Access Token"
3. 描述：`GitHub Actions`
4. 权限：`Read, Write, Delete`
5. 点击 "Generate"
6. **重要**：复制生成的令牌（只显示一次）

### 3. 在 GitHub 仓库中添加 Secrets
1. 进入你的 GitHub 仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加以下两个 secrets：

   **Secret 1:**
   - Name: `DOCKERHUB_USERNAME`
   - Value: 你的 Docker Hub 用户名（例如：`viciy2023`）

   **Secret 2:**
   - Name: `DOCKERHUB_TOKEN`
   - Value: 刚才复制的 Docker Hub 访问令牌

### 4. 运行 GitHub Actions 工作流
1. 进入 GitHub 仓库的 "Actions" 标签
2. 选择 "Build Prebuilt OpenClaw Image" 工作流
3. 点击 "Run workflow" → "Run workflow"
4. 等待构建完成（约 30-60 分钟）
5. 构建成功后，镜像会推送到 Docker Hub: `viciy2023/openclaw-clawmate:latest`

## 二、HuggingFace Spaces 部署

### 1. 准备文件
在 HuggingFace Spaces 仓库中需要以下文件：

```
your-hf-space/
├── Dockerfile          # 从 huggingface-GitHubActions/Dockerfile-hf 复制并重命名
└── entrypoint.sh       # 从 huggingface-new/entrypoint.sh-supabase 复制并重命名
```

### 2. 上传文件到 Supabase
确保以下文件已上传到 Supabase：
- `.env`
- `openclaw.json`
- `patches/clawmate/*.ts`
- `characters/maggie/*`
- `AGENTS.md`, `TOOLS.md` 等配置文件

### 3. 配置 HF Spaces Secrets
在 HuggingFace Spaces 设置中添加：
- `SUPABASE_ANON_KEY`: 你的 Supabase 匿名密钥
- `DEPLOY_FILES_BASE_URL`: Supabase 文件存储的基础 URL

### 4. 触发构建
推送文件到 HF Spaces 后，会自动触发构建和部署。

## 三、工作流说明

### GitHub Actions 工作流
- **文件**: `.github/workflows/build-prebuilt-image.yml`
- **触发方式**: 手动触发（workflow_dispatch）
- **功能**: 构建包含 OpenClaw + ClawMate + 所有依赖的基础镜像
- **输出**: Docker Hub 镜像 `viciy2023/openclaw-clawmate:latest`

### HuggingFace Spaces 部署
- **文件**: `huggingface-GitHubActions/Dockerfile-hf`
- **基础镜像**: `viciy2023/openclaw-clawmate:latest`（从 Docker Hub 拉取）
- **功能**: 在预构建镜像基础上添加 entrypoint.sh 启动脚本
- **运行时**: 从 Supabase 下载配置文件和补丁

## 四、故障排查

### GitHub Actions 构建失败
1. **权限错误**: 检查 DOCKERHUB_USERNAME 和 DOCKERHUB_TOKEN 是否正确设置
2. **仓库不存在**: 确保在 Docker Hub 创建了 `openclaw-clawmate` 仓库
3. **构建超时**: GitHub Actions 免费版有 6 小时限制，通常足够

### HuggingFace Spaces 部署失败
1. **镜像拉取失败**: 确保 GitHub Actions 已成功构建并推送镜像
2. **文件缺失**: 检查 entrypoint.sh 是否在 HF Spaces 仓库根目录
3. **Supabase 连接失败**: 检查 Secrets 配置是否正确

## 五、注意事项

1. **不要将 huggingface-new 目录上传到 GitHub**
   - 该目录包含敏感配置文件
   - 只需要将必要的文件上传到 Supabase 和 HF Spaces

2. **Docker Hub 镜像是公开的**
   - 预构建镜像不包含任何敏感信息
   - 配置文件在运行时从 Supabase 下载

3. **构建时间**
   - GitHub Actions 首次构建约 30-60 分钟
   - HF Spaces 部署约 5-10 分钟（使用预构建镜像）
