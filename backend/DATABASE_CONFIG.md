# MongoDB 数据库配置说明

## 数据库连接信息

本项目需要配置 MongoDB 数据库连接，请填写以下信息：

- **服务器地址**: your_host:port
- **数据库名称**: your_database_name
- **用户名**: your_username
- **密码**: your_password
- **权限**: readWrite

**⚠️ 安全提示**：以上信息为示例，请填写你的实际数据库配置。

## 配置步骤

### 1. 创建 `.env` 文件

在 `backend/` 目录下创建 `.env` 文件（如果不存在），添加以下内容：

```bash
# MongoDB Configuration
# 请填写实际的数据库连接信息
MONGODB_URL=mongodb://username:password@host:port/database_name?authSource=auth_database
MONGODB_DB_NAME=your_database_name

# Zhipu AI Configuration (从 https://open.bigmodel.cn/ 获取)
ZHIPU_API_KEY=your_zhipu_api_key_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. 连接字符串说明

MongoDB 连接字符串格式：

```
mongodb://[用户名]:[密码]@[主机]:[端口]/[数据库]?authSource=[认证数据库]
```

配置示例：

```
mongodb://username:password@host:port/database_name?authSource=auth_database
```

参数说明：

- `username`: 数据库用户名
- `password`: 数据库密码
- `host:port`: MongoDB 服务器地址和端口
- `database_name`: 数据库名称
- `authSource=auth_database`: 认证数据库（通常与目标数据库相同）

### 3. 测试连接

运行测试脚本验证数据库连接：

```bash
cd backend
python test_connection.py
```

成功输出示例：

```
正在测试 MongoDB 连接...
连接地址: your_host:port/your_database
数据库名: your_database
✓ 数据库连接成功！
✓ 当前数据库中的集合: ['templates', 'history', 'feedback']
✓ 写入测试成功，文档ID: 507f1f77bcf86cd799439011
✓ 读取测试成功: {'_id': ObjectId('...'), 'test': 'connection'}
✓ 清理测试数据成功

✅ 所有数据库连接测试通过！
```

### 4. 数据库集合说明

系统会自动创建以下集合：

1. **templates** - 存储 Prompt 模板

   - 索引：`template_id` (unique), `created_at`

2. **history** - 存储编译历史记录

   - 索引：`version_id` (unique), `created_at`

3. **feedback** - 存储用户反馈
   - 索引：`prompt_id`, `created_at`

### 5. 常见问题

#### Q1: 连接超时

**可能原因**：

- 网络问题，无法访问远程服务器
- 防火墙阻止了 5004 端口
- MongoDB 服务未启动

**解决方案**：

```bash
# 测试网络连通性
ping your_host

# 测试端口是否开放
telnet your_host your_port
# 或使用 nc (netcat)
nc -zv your_host your_port
```

#### Q2: 认证失败

**可能原因**：

- 用户名或密码错误
- 用户权限不足
- authSource 配置错误

**解决方案**：

- 检查用户名是否正确
- 检查密码是否正确
- 确认 authSource 配置正确

#### Q3: 权限不足

**可能原因**：

- 用户只有 read 权限，没有 write 权限
- 数据库名称错误

**解决方案**：
确认用户权限：

```javascript
// 在 MongoDB shell 中执行
use your_database_name
db.getUser("your_username")
```

### 6. 安全建议

⚠️ **重要提醒**：

- `.env` 文件包含敏感信息，已添加到 `.gitignore`
- 不要将 `.env` 文件提交到版本控制系统
- 生产环境建议使用环境变量而非 `.env` 文件
- 定期更换数据库密码
- 使用 SSL/TLS 加密连接（如果支持）

### 7. 生产环境配置

生产环境推荐使用更安全的连接方式：

```bash
# 使用 SSL 连接
MONGODB_URL=mongodb://username:password@host:port/database_name?authSource=auth_database&ssl=true&ssl_cert_reqs=CERT_REQUIRED

# 或使用 MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## 技术支持

如遇到数据库连接问题，请检查：

1. MongoDB 服务状态
2. 网络连接
3. 防火墙配置
4. 用户权限配置
5. 日志文件：查看 backend 目录下的日志输出
