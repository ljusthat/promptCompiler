# Prompt Compiler

**基于语义编译与自适应优化的 Prompt 输出系统**

一个智能的 Prompt 编译优化系统，通过规则引擎和 AI 调优模块，将用户输入转化为结构化、高质量、可复现的 Prompt。

## 🌟 核心功能

### 1. **智能编译**

- 意图提取：自动识别用户需求的任务类型、领域和目标
- 模板匹配：根据意图智能选择最合适的 Prompt 模板
- 结构化输出：生成包含角色、目标、约束条件的完整 Prompt

### 2. **AI 优化**

- 多级别优化：支持低、中、高三档优化级别
- 智能重写：使用智谱 AI glm-4-flash 模型进行 Prompt 优化
- 自检机制：自动验证优化效果，确保质量提升

### 3. **质量评估**

- 多维度指标：结构合规率、目标一致性、语义完整度、表达清晰度
- 实时反馈：即时提供改进建议
- 持续学习：基于用户反馈不断优化

### 4. **模板管理**

- 模板库：预置多种场景模板
- 自定义模板：支持创建和管理个性化模板
- 使用统计：跟踪模板使用频率和质量评分

### 5. **历史记录**

- 版本管理：保存所有编译历史

# Prompt Compiler

基于语义编译与自适应优化的 Prompt 输出系统。该项目将用户输入通过意图提取、模板匹配与 AI 优化，生成结构化且高质量的 Prompt，适合用于构建可复用的 Prompt 工程流程。

本 README 给出面向 GitHub 访问者的快速上手步骤（包括 Windows PowerShell 示例命令）。

## 主要功能

- 意图提取、模板匹配与结构化输出
- 基于智谱 AI 的 Prompt 优化与质量评估
- 模板管理与历史记录

## 先决条件

- Python 3.9+（建议使用 venv 或虚拟环境）
- Node.js 18+（用于前端开发）
- 可用的 MongoDB 实例（远程或本地）
- 智谱 AI API Key（从 https://open.bigmodel.cn/ 获取）

> 安全提示：所有凭证（例如 API Key、数据库密码）应放在环境变量或本地 `.env` 文件中，不要提交到仓库。

仓库已包含 `backend/env.example` 作为配置模板，并新增了 `.gitignore` 来忽略 `.env` 等本地敏感文件。

## 快速开始（Windows PowerShell）

1. 克隆仓库并进入目录：

```powershell
git clone <repository-url>
cd promptCompiler
```

2. 后端（Python）

```powershell
cd backend
# 创建并激活虚拟环境
python -m venv .venv
# PowerShell 激活
. .\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 复制示例 env 文件并编辑（不要提交 .env）
Copy-Item env.example .env
# 使用编辑器填写 .env 中的 MONGODB_URL、MONGODB_DB_NAME、ZHIPU_API_KEY 等

# 可选：测试数据库连接
python test_connection.py

# 启动后端（开发模式）
python main.py
```

启动后，后端默认在 `http://localhost:8000` 提供服务；API 文档：`/docs`（Swagger） 和 `/redoc`。

3. 前端（Node / Vite）

```powershell
cd frontend
npm install
npm run dev
```

前端开发服务器默认在 `http://localhost:5173`。

4. 运行测试（后端）

```powershell
cd backend
pytest tests/
```

## 配置说明

- `backend/env.example` 包含所有需要的环境变量占位：

  - MONGODB_URL
  - MONGODB_DB_NAME
  - ZHIPU_API_KEY
  - SERVER_HOST / SERVER_PORT / DEBUG
  - CORS_ORIGINS

- `backend/config.py` 使用 pydantic-settings 从 `.env` 加载配置，推荐在生产使用真实环境变量（CI/CD secrets）而非 `.env`。

## 推送到 GitHub（安全建议）

- 在推送前请确保本地没有把 `.env` 或凭证文件加入版本控制：

```powershell
git status --porcelain
```

- 如果你曾经把凭证提交到了历史，请务必：
  1. 在对应服务（例如智谱 AI、数据库）中撤销并重新生成密钥；
  2. 使用 `git filter-repo` 或 BFG 清理仓库历史（这会改变历史并需要强推）；
  3. 在仓库的 README 或贡献指南中写明不要提交凭证。

## CI / 部署建议

- 在 GitHub Actions 或其他 CI 中，将敏感值（`ZHIPU_API_KEY`、`MONGODB_URL` 等）配置为仓库 Secrets，并在 workflow 环境中注入。
- 可在 CI 中加入一个敏感信息扫描步骤（例如使用 gitleaks 或 truffleHog）以在 PR 时阻止凭证泄露。

示例（概念性）：在 workflow 中设置环境变量

```yaml
env:
  MONGODB_URL: ${{ secrets.MONGODB_URL }}
  ZHIPU_API_KEY: ${{ secrets.ZHIPU_API_KEY }}
```

## 常见问题

- 健康检查失败：先运行 `python test_connection.py` 检查 MongoDB 配置是否正确。
- 智谱 AI 访问失败：确认 `ZHIPU_API_KEY` 正确且网络能访问 open.bigmodel.cn。

## 贡献

欢迎通过 Issue 或 PR 参与改进。请注意：不要在 PR 中包含任何凭证或个人信息。

## 许可证

本项目采用 MIT 许可证，详见 `LICENSE` 文件。

---

如果你希望我：

- 添加一个 GitHub Actions workflow 来在 PR 时自动扫描敏感信息（gitleaks）；
- 或帮你生成一个示例 `deploy` 脚本（systemd / Dockerfile / docker-compose）以便生产部署；

告诉我你想先做哪一项，我会继续实现。
