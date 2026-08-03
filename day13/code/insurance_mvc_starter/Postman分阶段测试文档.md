# 保险精准营销系统 · Postman 分阶段测试文档

> **配套使用**：每完成一个阶段的 AI 开发，就按本文档对应章节用 Postman 逐接口验证，全部通过再进入下一阶段。
> **依据**：以 `docs/03_API接口文档.md` v1.0 为准（共 29 个接口）。提示词清单中对部分接口做了简化描述，实际以本测试文档为准。
> **BaseURL**：`http://127.0.0.1:5000/api/v1`

---

## 〇、通用准备（开始前必做）

### 0.1 Postman 环境变量配置

在 Postman 里新建一个 Environment，叫"保险系统"，添加以下变量：

| 变量名             | 初始值                            | 说明            |
| --------------- | ------------------------------ | ------------- |
| `base_url`      | `http://127.0.0.1:5000/api/v1` | 接口基础地址        |
| `admin_token`   | （留空）                           | admin 登录后自动填入 |
| `user_token`    | （留空）                           | 普通用户登录后自动填入   |
| `admin_id`      | 1                              | admin 用户 id   |
| `user_id`       | （留空）                           | 普通用户 id       |
| `experiment_id` | （留空）                           | 训练后填入         |
| `record_id`     | （留空）                           | 邮件记录 id       |

> 所有接口 URL 写成 `{{base_url}}/auth/login` 这种形式，切换环境就能改地址。

### 0.2 请求头约定

| 场景     | Headers                                                          |
| ------ | ---------------------------------------------------------------- |
| 无鉴权接口  | `Content-Type: application/json`                                 |
| 需鉴权接口  | 上面 + `Authorization: Bearer {{admin_token}}`（或 `{{user_token}}`） |
| 文件上传接口 | **不要**手动设 Content-Type，Postman 选 form-data 后自动加 boundary         |

### 0.3 统一响应校验

每个接口的响应都先校验这三点，再做业务字段校验：

1. HTTP 状态码符合预期（200 / 400 / 401 / 403 / 404 / 500）
2. 响应体是 `{code, message, data}` 三段结构
3. `code` 值符合 API 文档 0.5 节业务码表

### 0.4 测试流程总览

| 阶段       | 测试方式                | 接口数 | 前置依赖                   |
| -------- | ------------------- | --- | ---------------------- |
| 0 认证骨架   | Postman             | 5   | 无（starter 已完成）         |
| 1 数据模块   | Postman             | 5   | 阶段 0 拿到 token          |
| 2 模型模块   | Postman             | 8   | 阶段 1 已上传数据             |
| 3 大模型层   | Python 内联           | 0   | 阶段 2 完成（无 HTTP 接口）     |
| 4 邮件模块   | Postman             | 10  | 阶段 2 已预测 + 阶段 3 LLM 可用 |
| 5 日志模块   | Postman             | 1   | 前面阶段产生操作记录             |
| 6 前端集成   | 浏览器                 | —   | 阶段 1～5 全通              |
| 7 集成测试   | 脚本 + Postman        | 全部  | 阶段 6 完成                |
| 8 Docker | docker 命令 + Postman | 回归  | 阶段 7 完成                |

---

## 阶段 0：认证骨架回归测试（5 接口）

> starter 已实现，每次进入新阶段前先跑一遍确认基线没被改坏。

### 0.1 注册普通用户

```http
POST {{base_url}}/auth/register
Content-Type: application/json

{
  "username": "student01",
  "password": "stu123456"
}
```

**预期**：`200`，`code=0`，`data.user.role="user"`，`data.access_token` 非空。

**异常**：重复注册同一用户名 → `400` / `code=1004`。

> 测试脚本（Tests 标签页）把 token 存到环境变量：
> `pm.environment.set("user_token", pm.response.json().data.access_token);`

### 0.2 admin 登录

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**预期**：`200`，`code=0`，`data.user.role="admin"`。

> 测试脚本：`pm.environment.set("admin_token", pm.response.json().data.access_token);`



![47c25e2a-8cfd-43e1-875a-590b8bf252a7](file:///C:/Users/qiuxingyu/OneDrive/Pictures/Typedown/47c25e2a-8cfd-43e1-875a-590b8bf252a7.png)

### 0.3 普通用户登录（验证同一接口）

用 0.1 注册的 `student01` 调同一个 `/login`：

```json
{ "username": "student01", "password": "stu123456" }
```

**预期**：`200`，`code=0`，`data.user.role="user"`。

> 对比 0.2：同一接口，admin 返回 role=admin，user 返回 role=user——角色来自数据库。

### 0.4 获取当前用户 /me

```http
GET {{base_url}}/auth/me
Authorization: Bearer {{admin_token}}
```

![3e5b1a41-b032-4a97-96e5-c419ba9a1fb9](file:///C:/Users/qiuxingyu/OneDrive/Pictures/Typedown/3e5b1a41-b032-4a97-96e5-c419ba9a1fb9.png)

**预期**：`200`，`code=0`，`data={id:1, username:"admin", role:"admin"}`。

换 `{{user_token}}` 再请求 → `data.role="user"`。

**异常**：不带 Authorization 头 → `401` / `code=1002` / "未提供Token"。

### 0.5 用户列表（RBAC 守卫）

```http
GET {{base_url}}/auth/users
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，`data` 是数组，含 admin 和 student01。

**异常（关键）**：换 `{{user_token}}` → `403` / `code=1003` / "权限不足"。

> 这一步验证 RBAC 闭环：admin 放行、user 被拦。

### 阶段 0 验收清单

- [ ] 0.1～0.5 全部返回 code=0
- [ ] 0.4 不带 token 返回 1002
- [ ] 0.5 user token 返回 1003
- [ ] `admin_token` 和 `user_token` 已存入环境变量

---

## 阶段 1：数据模块测试（5 接口）

> 前置：阶段 0 通过，`admin_token` 可用。准备一个测试 Excel（用 `python -m app.scripts.gen_sample` 生成 `data/sample_customers.xlsx`）。

### 1.1 上传 Excel 数据

```http
POST {{base_url}}/data/upload
Authorization: Bearer {{admin_token}}
```

Body 选 **form-data**，加一个 key：`file`，类型选 **File**，选 `sample_customers.xlsx`。

![420427e5-3e4a-4179-aa18-da0b226658fb](file:///C:/Users/qiuxingyu/OneDrive/Pictures/Typedown/420427e5-3e4a-4179-aa18-da0b226658fb.png)

**预期**：`200`，`code=0`，响应类似：

```json
{
  "code": 0,
  "data": {
    "imported_count": 1000,
    "quality_report": {
      "total_rows": 1000,
      "total_cols": 12,
      "missing_values": { ... },
      "duplicates": 0,
      "dtypes": { ... }
    }
  }
}
```

**异常**：

- 不带 file 字段 → `400` / `code=1001`
- 上传非 Excel 文件 → `400` / `code=2002`
- 不带 token → `401` / `code=1002`

> 注意：上传会**清空 customers 旧数据**重新导入（覆盖策略），重复上传不会累积。

### 1.2 客户列表分页

```http
GET {{base_url}}/data/customers?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，分页结构：

```json
{
  "code": 0,
  "data": {
    "items": [ { "id":1, "gender":"Male", "age":44, ..., "predicted_prob": null } ],
    "total": 1000,
    "page": 1,
    "per_page": 20,
    "pages": 50
  }
}
```

**过滤参数测试**：加 `?gender=Female&age_min=30&age_max=50` 验证筛选生效（total 应变小）。

### 1.3 数据概览统计

```http
GET {{base_url}}/data/statistics
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，响应含：

```json
{
  "data": {
    "total": 1000,
    "gender_distribution": { "Male": 540, "Female": 460 },
    "response_distribution": { "0": 870, "1": 130 },
    "age_stats": { "min": 20, "max": 80, "avg": 38.5 }
  }
}
```

> 重点看 `response_distribution`：约 87:13，验证不平衡数据特征。

### 1.4 数据质量报告

```http
GET {{base_url}}/data/quality
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，`data` 含 `total_rows/total_cols/missing_values/duplicates/dtypes`。

### 1.5 EDA 可视化

依次测试 4 种图表类型：

```http
GET {{base_url}}/data/visualization/response_distribution
GET {{base_url}}/data/visualization/gender_response
GET {{base_url}}/data/visualization/age_distribution
GET {{base_url}}/data/visualization/premium_distribution
Authorization: Bearer {{admin_token}}
```

**预期**：每个都 `200`，`code=0`，`data` 含 `image_base64`（长字符串）和 `format:"png"`。

**验证图片**：把 `image_base64` 值复制到浏览器地址栏前加 `data:image/png;base64,`，能看到图且**中文不乱码**。

**异常**：未知 chart_type（如 `/visualization/xxx`）→ `400` / `code=1001`。

### 阶段 1 验收清单

- [ ] 1.1 上传 1000 行成功，imported_count=1000
- [ ] 1.2 分页 total=1000，过滤生效
- [ ] 1.3 response_distribution 约 87:13
- [ ] 1.4 质量报告字段齐全
- [ ] 1.5 四张图都能渲染，中文不乱码
- [ ] 不带 token 访问任一接口返回 1002

---

## 阶段 2：模型模块测试（8 接口）

> 前置：阶段 1 已上传数据。本阶段训练耗时约 10～30 秒（1000 行数据）。

### 2.1 训练模型（全部三算法）

```http
POST {{base_url}}/model/train
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{}
```

不传 body 或传 `{}` 表示训练全部三算法（logistic_regression / xgboost / random_forest）。

**预期**：`200`，`code=0`，响应含三算法指标：

```json
{
  "data": {
    "best_model": "xgboost",
    "results": {
      "logistic_regression": { "accuracy":0.87, "precision":..., "recall":..., "f1_score":..., "roc_auc":0.84 },
      "xgboost":              { ..., "roc_auc":0.86 },
      "random_forest":        { ..., "roc_auc":0.85 }
    }
  }
}
```

**单算法训练**：`{"models": ["xgboost"]}` 只训 xgboost。

**自定义超参**：`{"models":["xgboost"], "params":{"xgboost":{"n_estimators":200}}}`。

**异常**：

- 用 `{{user_token}}` → `403` / `code=1003`（仅 admin 可训练）
- 未上传数据就训练 → `400` / `code=2001`
- 训练异常 → `500` / `code=3001`

### 2.2 实验记录列表

```http
GET {{base_url}}/model/experiments?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，分页结构，`items` 每条含 `id/model_name/accuracy/.../roc_auc/is_best/created_at`。

> 找到 `is_best=true` 的那条，记下其 id，存到环境变量 `experiment_id`。

**过滤**：`?model_name=xgboost` 只看 xgboost 记录。

### 2.3 获取最佳模型

```http
GET {{base_url}}/model/best
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，`data={model_name, roc_auc, experiment_id}`。

**异常**：未训练就查 → `400` / `code=3002`。

### 2.4 全量预测（概率回写）

```http
POST {{base_url}}/model/predict
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{}
```

**预期**：`200`，`code=0`，`data={model_name, predicted_count:1000}`。

**验证回写**：回头调 1.2 `/data/customers`，看 `items` 里的 `predicted_prob` 字段**不再是 null**，是 0～1 之间的小数。

**异常**：未训练就预测 → `code=3002`。

### 2.5 上传数据预测（不入库）

```http
POST {{base_url}}/model/predict_upload
Authorization: Bearer {{admin_token}}
```

Body 选 **form-data**：`file`（File 类型，选一个 Excel）。

**预期**：`200`，`code=0`，`data={model_name, total_count, statistics, predictions}`，predictions 直接返回每条预测概率。

> 对比 2.4：本接口对**新数据**预测并返回，不覆盖训练数据、不入库。

### 2.6 模型评估可视化

```http
GET {{base_url}}/model/visualization/roc_curve
GET {{base_url}}/model/visualization/metrics_comparison
GET {{base_url}}/model/visualization/confusion_matrix?model=xgboost
GET {{base_url}}/model/visualization/feature_importance?model=xgboost
Authorization: Bearer {{admin_token}}
```

**预期**：每个 `200`，`code=0`，含 `image_base64`。

> `confusion_matrix` 和 `feature_importance` 必须带 `?model=` 参数，值是 `logistic_regression`/`xgboost`/`random_forest`。

**异常**：confusion_matrix 不带 model 参数 → `400` / `code=1001`。

### 2.7 导出模型文件

```http
GET {{base_url}}/model/export/xgboost
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，响应是二进制文件流（.joblib），`Content-Disposition: attachment`。Postman 会提示保存文件。

**异常**：

- 用 `{{user_token}}` → `403` / `code=1003`
- 导出不存在的模型 → `code=3002`

### 2.8 导入模型文件

```http
POST {{base_url}}/model/import
Authorization: Bearer {{admin_token}}
```

Body 选 **form-data**：`file`（File 类型，选 2.7 导出的 .joblib）。

**预期**：`200`，`code=0`，`data={model_name, path}`。

**异常**：上传非 .joblib 文件 → `code=1001`；user token → `403`。

### 阶段 2 验收清单

- [ ] 2.1 三算法训练成功，best_model 有值
- [ ] 2.2 实验记录 is_best 标记正确
- [ ] 2.3 最佳模型 roc_auc > 0.8
- [ ] 2.4 预测后 customers 的 predicted_prob 非 null
- [ ] 2.5 上传预测返回 predictions 数组
- [ ] 2.6 四张图都能渲染，中文不乱码
- [ ] 2.7 导出 .joblib 文件可保存
- [ ] 2.8 导入后能再用该模型预测
- [ ] user token 调 train/export/import 返回 1003

---

## 阶段 3：大模型层测试（无 HTTP 接口）

> 本阶段只建 `llm_service.py` + `prompt_template` 模型，没有独立路由。用 Python 内联验证，不涉及 Postman。

### 3.1 Python 内联测试 LLM 连接

启动虚拟环境后，在项目根目录执行：

```python
# 临时测试脚本 test_llm.py（测完可删）
from app.services.llm_service import test_connection, generate_marketing_content
from app.models.prompt_template import PromptTemplate
from app.core.database import SessionLocal

# 1. 测连通性
print("LLM 连通:", test_connection())  # 期望 True

# 2. 测生成
db = SessionLocal()
tpl = PromptTemplate.find_active(db)
mock_customer = {
    "gender": "Male", "age": 44, "annual_premium": 40000,
    "vehicle_age": "1-2 Year", "predicted_prob": 0.87
}
result = generate_marketing_content(mock_customer, tpl)
print("subject:", result["subject"])
print("content:", result["content"][:200])
print("tokens:", result.get("usage_tokens"))
db.close()
```

**预期**：

- `test_connection()` 返回 `True`
- `generate_marketing_content` 返回的 subject 是邮件标题、content 是针对该客户特征的营销文案

**异常排查**：

- 返回 False → 检查 `.env` 的 `LLM_API_KEY` / `LLM_BASE_URL`
- 超时 → 调大 `LLM_TIMEOUT`
- 限流 → 加重试或降低频率

### 阶段 3 验收清单

- [ ] test_connection() 返回 True
- [ ] generate_marketing_content 返回非空 subject + content
- [ ] 文案里能看到客户特征（age/gender 等被填入）

> 本阶段没有 Postman 测试。LLM 的端到端验证在阶段 4（邮件生成）完成。

---

## 阶段 4：邮件模块测试（10 接口）

> 前置：阶段 2 已预测（customers 有 predicted_prob）+ 阶段 3 LLM 可用。

### 4.1 筛选高潜客户

```http
GET {{base_url}}/email/targets?percentile=0.9&page=1&per_page=20
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`：

```json
{
  "data": {
    "threshold": 0.72,
    "total": 100,
    "customers": [ { "id":1, "gender":"Male", "age":44, "annual_premium":40000, "predicted_prob":0.91 } ]
  }
}
```

> threshold 是 top 10% 的概率分界线；customers 按 predicted_prob 降序。

**异常**：未预测就调 → `code=3002`。

### 4.2 生成营销邮件（自动取 top N）

```http
POST {{base_url}}/email/generate
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{ "limit": 5 }
```

**预期**：`200`，`code=0`：

```json
{
  "data": {
    "generated_count": 5,
    "failed_count": 0,
    "records": [ { "customer_id":1, "status":"generated", "subject":"..." } ]
  }
}
```

**指定客户生成**：`{"customer_ids": [1, 2, 3]}`。

**异常**：未配 LLM_API_KEY → records 里 status="failed"，failed_count 等于 limit。

> 记下任一 record 的 customer_id，后面 4.6 查详情要用（用 customer_id 或 record_id）。

### 4.3 获取 Prompt 模板

```http
GET {{base_url}}/email/prompt
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，`data={name, content}`，content 含 `{gender}`/`{age}` 等占位符。

### 4.4 更新 Prompt 模板

```http
PUT {{base_url}}/email/prompt
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "content": "尊敬的客户您好，我们是XX保险。根据您的画像（性别：{gender}，年龄：{age}），为您推荐..."
}
```

**预期**：`200`，`code=0`，返回更新后的 `{name, content}`。

> 更新后再调 4.2 生成邮件，验证文案用了新模板。

### 4.5 邮件记录列表

```http
GET {{base_url}}/email/records?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，分页结构，items 每条含 `id/customer_id/subject/status/created_at`。

- admin 能看全部，且含 `created_by_username`
- user 只看自己生成的

**过滤**：`?status=failed` 只看失败的。

> 记下任一记录的 id，存到环境变量 `record_id`。

### 4.6 邮件详情

```http
GET {{base_url}}/email/records/{{record_id}}
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，含完整 `content` 正文。

**异常**：record_id 不存在 → `code=2001`。

### 4.7 更新邮件记录

```http
PUT {{base_url}}/email/records/{{record_id}}
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{ "email_subject": "修改后的标题", "email_content": "修改后的正文" }
```

**预期**：`200`，`code=0`。再调 4.6 验证内容已更新。

### 4.8 标记邮件状态

```http
PATCH {{base_url}}/email/records/{{record_id}}
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{ "status": "sent" }
```

**预期**：`200`，`code=0`。再调 4.6 验证 status 变成 sent。

### 4.9 删除单条邮件

```http
DELETE {{base_url}}/email/records/{{record_id}}
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，`data={success:true}`。

> 删除后再调 4.6 应返回 `code=2001`。

### 4.10 批量删除邮件

先调 4.2 重新生成几条拿 record_id，然后：

```http
DELETE {{base_url}}/email/records
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{ "record_ids": [11, 12, 13] }
```

**预期**：`200`，`code=0`，`data={deleted_count:3}`。

### 阶段 4 验收清单

- [ ] 4.1 targets 返回高潜客户，按概率降序
- [ ] 4.2 generate 生成 5 封邮件，generated_count=5
- [ ] 4.3/4.4 prompt 模板可读可写
- [ ] 4.5 records 列表 admin 看全部、user 看自己
- [ ] 4.6 详情含完整 content
- [ ] 4.7/4.8 更新和标记状态生效
- [ ] 4.9/4.10 单删和批删都返回 success
- [ ] 邮件文案针对客户特征个性化（能看到 age/gender 被填入）

---

## 阶段 5：日志模块测试（1 接口）

> 前置：前面阶段已产生操作记录（登录/上传/训练/预测/生成邮件）。

### 5.1 操作日志查询

```http
GET {{base_url}}/logs?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```

**预期**：`200`，`code=0`，分页结构，items 每条含 `id/user_id/action/details/created_at`。

**验证埋点**：检查 items 里能看到这些 action：

- `login`（阶段 0 登录产生）
- `upload` 或 `data_upload`（阶段 1 上传产生）
- `model_training`（阶段 2 训练产生）
- `prediction`（阶段 2 预测产生）
- `email_generation`（阶段 4 生成邮件产生）

**过滤测试**：

- `?user_id=1` 只看 admin 的操作
- `?action=model_training` 只看训练记录

**异常**：用 `{{user_token}}` → `403` / `code=1003`（仅 admin 可查全部日志）。

### 阶段 5 验收清单

- [ ] 5.1 返回日志列表，含至少 5 种 action
- [ ] user_id 过滤生效
- [ ] action 过滤生效
- [ ] user token 返回 1003

---

## 阶段 6：前端集成测试（浏览器，非 Postman）

> 前置：阶段 1～5 全部 Postman 测试通过。本阶段用浏览器验证前端串联。

### 6.1 启动与登录

1. `python run.py` 启动服务
2. 浏览器打开 `http://127.0.0.1:5000`
3. **预期**：看到登录页，有用户名/密码输入框和登录按钮
4. 输入 `admin/admin123` 登录
5. **预期**：进入主界面，顶部显示用户名 admin 和角色徽章，左侧出现 Tab 导航

### 6.2 数据管理 Tab

1. 切到"数据管理"Tab
2. 点上传，选 `sample_customers.xlsx`
3. **预期**：显示进度条 → 上传成功提示 → 显示 imported_count
4. 切到客户列表，翻页能看数据
5. **预期**：表格显示客户字段，分页器可点

### 6.3 模型训练 Tab

1. 切到"模型训练"Tab
2. 选算法 xgboost，点训练
3. **预期**：loading 遮罩 → 训练完成显示指标（accuracy/auc 等）+ ROC 曲线图
4. **预期**：图中文不乱码
5. 点"全量预测"按钮
6. **预期**：成功提示，predicted_count=1000

### 6.4 预测结果 Tab

1. 切到"预测结果"Tab
2. **预期**：表格显示 top 客户，按 predicted_prob 降序，高潜客户排前面

### 6.5 邮件生成 Tab

1. 切到"邮件生成"Tab
2. 点"生成邮件"，top_n=5
3. **预期**：loading → 成功提示 generated_count=5
4. 邮件列表卡片展示 subject + 部分正文
5. 点详情看完整 content
6. **预期**：文案针对客户特征个性化

### 6.6 操作日志 Tab（admin 可见）

1. 切到"操作日志"Tab
2. **预期**：时间线展示操作记录，能看到刚才的训练/预测/生成动作

### 6.7 RBAC 验证（普通用户视角）

1. 登出，用 `student01/stu123456` 登录
2. **预期**：左侧 Tab 不显示"模型训练"（或显示但点训练被拦）
3. 访问训练接口被拦（前端弹 403 提示）

### 6.8 401 自动跳登录

1. 登录后，在浏览器 DevTools → Application → Local Storage 删掉 token
2. 点任意操作
3. **预期**：自动跳回登录页

### 阶段 6 验收清单

- [ ] 6.1 登录页 → 主界面正常
- [ ] 6.2 上传 + 客户列表展示
- [ ] 6.3 训练 + ROC 图（中文不乱码）
- [ ] 6.4 预测结果按概率排序
- [ ] 6.5 邮件生成 + 详情查看
- [ ] 6.6 操作日志展示
- [ ] 6.7 普通用户被 RBAC 拦截
- [ ] 6.8 token 失效自动跳登录

---

## 阶段 7：集成测试（端到端）

> 前置：阶段 1～6 全通。本阶段跑自动化脚本 + Postman 全量回归。

### 7.1 冒烟测试脚本

```powershell
python -m app.scripts.smoke_test
```

**预期**：脚本顺序跑完 13 步，每步打印 ✓，末尾汇总：

```
========================================
冒烟测试结果：13/13 通过
总耗时：xx.xs
========================================
```

**任一步失败**：脚本会停止并打印失败接口的响应体，按响应体排查。

### 7.2 Postman 全量回归

用阶段 7 提示词生成的 `docs/postman_collection.json` 导入 Postman，用 Runner 跑全部 29 个接口。

**预期**：全部 ✓，无失败。

### 7.3 全链路业务流验证

在浏览器走一遍完整业务闭环（不报错即通过）：

```
登录 admin → 上传 Excel → 训练 xgboost → 预测 → 生成邮件 → 查日志 → 登出
```

### 阶段 7 验收清单

- [ ] 7.1 smoke_test 13/13 通过
- [ ] 7.2 Postman Runner 全绿
- [ ] 7.3 浏览器全链路无报错

---

## 阶段 8：Docker 容器化测试

> 前置：阶段 7 全通。本阶段验证容器化部署后功能等价。

### 8.1 镜像构建

```powershell
docker compose build
```

**预期**：构建成功，无报错。镜像大小 < 1.5GB（`docker images` 查看）。

### 8.2 启动与健康检查

```powershell
docker compose up -d
docker compose ps
```

**预期**：STATUS 显示 `healthy`（约 30 秒后）。

### 8.3 Postman 回归（容器内服务）

- 把 Postman 环境变量的 `base_url` 保持 `http://127.0.0.1:5000/api/v1`（端口已映射）
- 重跑阶段 0、1、2、4、5 的核心接口（每个模块挑 2～3 个代表接口）
- **预期**：全部 code=0

> 注意：容器首次启动数据库是空的，需要重新走 admin 登录 → 上传数据 → 训练。

### 8.4 数据持久化验证

```powershell
docker compose down      # 删容器（数据在 volume）
docker compose up -d     # 重建容器
docker compose ps        # healthy
```

然后调 `GET /data/customers`：

**预期**：数据还在（total 仍是 1000），证明 volume 持久化生效。

### 8.5 中文渲染验证

调 `GET /model/visualization/roc_curve`，把 image_base64 渲染：

**预期**：图中文不乱码（验证容器内字体安装成功）。

### 8.6 日志与排错

```powershell
docker compose logs -f          # 实时日志
docker compose logs --tail 100  # 最近 100 行
```

**预期**：能看到 Flask 启动日志、建表日志、请求日志。

### 阶段 8 验收清单

- [ ] 8.1 镜像构建成功
- [ ] 8.2 容器 healthy
- [ ] 8.3 Postman 回归核心接口全通
- [ ] 8.4 down/up 后数据不丢
- [ ] 8.5 容器内图表中文不乱码
- [ ] 8.6 日志正常输出

---

## 附录 A：测试中常见问题排查

| 现象             | 可能原因                     | 排查                                         |
| -------------- | ------------------------ | ------------------------------------------ |
| 所有接口 401       | token 过期或未设环境变量          | 重新登录，检查 Postman 环境变量                       |
| 403 但用的是 admin | token 用错了（用了 user_token） | 检查 Authorization 头用的是 admin_token          |
| 上传 415 / 400   | 手动设了 Content-Type        | form-data 模式下删掉 Content-Type，让 Postman 自动加 |
| 训练 500 / 3001  | 数据未上传或字段缺失               | 先调 /data/upload，检查 Excel 列名                |
| 预测 3002        | 未训练或模型文件丢失               | 先调 /model/train，再调 /model/best 确认          |
| 邮件全 failed     | LLM_API_KEY 未配或失效        | 检查 .env，跑阶段 3.1 test_connection            |
| 图中文乱码          | 缺中文字体                    | 本地装 SimHei；Docker 确认装了 fonts-noto-cjk      |
| 分页 total=0     | 上传覆盖后数据被清                | 重新上传，注意 upload 是覆盖策略                       |

## 附录 B：测试数据准备

### 生成测试样本

```powershell
python -m app.scripts.gen_sample
# 生成 data/sample_customers.xlsx（1000 行）
```

### 重置数据库（测试间清场）

关闭服务后删除 `instance/starter.db`，重启会自动重建空库 + admin 账号。

> Docker 环境：`docker compose down -v` 会删数据卷，重启后从零开始。
