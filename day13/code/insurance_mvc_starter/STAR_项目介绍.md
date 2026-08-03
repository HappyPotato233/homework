# 保险精准营销系统 · 项目介绍（STAR 法则）

> 本文档基于项目实际代码扫描生成，用于面试 / 述职 / 项目展示场景下的结构化项目介绍。

---

## 一、S — Situation（情境）

### 1.1 业务背景

保险行业长期面临**精准营销**的核心痛点：

- **传统营销"广撒网"效率低**：电销团队无差别外呼，转化率不足 2%，人力成本高
- **客户洞察缺失**：海量客户数据沉睡在 Excel 中，无法识别"高潜购买意向"客户
- **营销内容同质化**：业务员手写邮件，千人一面，缺乏个性化触达
- **全链路断层**：数据 → 预测 → 内容生成 → 投放，四个环节各自为战，无统一系统支撑

### 1.2 技术挑战

| 挑战 | 具体描述 |
| --- | --- |
| **全链路打通** | 数据导入 → ML 训练/预测 → LLM 生成邮件 → 记录管理，需在一个系统内闭环 |
| **双模型协同** | ML 模型（scikit-learn / XGBoost）预测购买概率 + LLM（DeepSeek）生成营销文案 |
| **权限与安全** | 多角色（admin/user）、敏感操作审计、密码与 Token 安全 |
| **工程质量** | 分层清晰、可扩展、可测试、统一异常处理、配置与代码分离 |

---

## 二、T — Task（任务）

构建一个**保险精准营销系统后端**，交付以下能力：

### 2.1 功能目标

| 模块 | 目标 |
| --- | --- |
| **认证 (auth)** | 用户注册/登录/登出/当前用户/用户列表，JWT 无状态认证 + RBAC 权限 |
| **数据 (data)** | Excel 上传入库、分页查询、数据概览、质量报告、EDA 可视化 |
| **模型 (model)** | 多模型训练（LR/RF/XGBoost）、实验记录、最佳模型、全量预测、上传预测、评估可视化、模型导入导出 |
| **邮件 (email)** | 高潜客户筛选、LLM 生成营销邮件、Prompt 模板管理、邮件记录 CRUD、批量操作 |
| **日志 (log)** | 操作日志查询（admin），覆盖训练/预测/导入导出/邮件操作 |

### 2.2 非功能目标

- **可启动即用**：`python run.py` 一键启动，自动建表、自动 seed 管理员账号
- **统一响应**：所有接口返回 `{code, message, data}` 信封，前端只处理一种结构
- **安全合规**：密码 bcrypt 哈希、JWT 鉴权、角色守卫、500 不暴露堆栈
- **架构可扩展**：MVC 分层 + 应用工厂，新增业务模块只需加蓝图

---

## 三、A — Action（行动）

### 3.1 架构设计：MVC + 应用工厂

采用**应用工厂模式（App Factory）** + **严格分层**，项目结构如下：

```
insurance_mvc_starter/
├── app/                          # 应用包
│   ├── __init__.py               # 应用工厂 create_app()
│   ├── api/v1/                   # 【Controller 层】路由
│   │   ├── __init__.py           #   蓝图聚合 register_blueprints()
│   │   ├── auth.py               #   认证路由（6 接口）
│   │   ├── data.py               #   数据路由（5 接口）
│   │   ├── model.py              #   模型路由（8 接口）
│   │   ├── email.py              #   邮件路由（10 接口）
│   │   └── log.py                #   日志路由（1 接口）
│   ├── core/                     # 【基础设施层】
│   │   ├── config.py             #   Pydantic-Settings 配置（读 .env）
│   │   ├── database.py           #   SQLAlchemy 2.0 引擎/会话
│   │   ├── security.py           #   bcrypt + JWT
│   │   ├── dependencies.py       #   login_required / role_required
│   │   └── response.py           #   统一响应 + BizException
│   ├── models/                   # 【Model 层】ORM
│   ├── schemas/                  # 【校验层】Pydantic 请求体
│   ├── services/                 # 【业务服务层】data/ml/email/log
│   └── utils/                    # 【工具层】可视化/文件
├── run.py                        # 启动脚本
├── requirements.txt              # 依赖清单
└── .env                          # 环境变量
```

**为什么用应用工厂？**
- 延迟初始化：`import app` 不触发建表，只有 `create_app()` 才真正初始化
- 多实例支持：测试/生产可创建不同配置的 app 实例
- 顺序可控：先注册蓝图/异常处理器，再 `with app_context()` 建表 + seed

### 3.2 技术选型

| 领域 | 选型 | 理由 |
| --- | --- | --- |
| Web 框架 | Flask 3.0.3 | 轻量、灵活，适合中小型系统 |
| ORM | SQLAlchemy 2.0（原生） | 不用 Flask-SQLAlchemy，Model 层独立于 Web 框架，可被 CLI/测试复用 |
| 参数校验 | Pydantic 2.7 | 类型安全、自动校验、错误信息友好 |
| 认证 | python-jose (JWT) + bcrypt 4.1 | 避开 passlib 与 bcrypt 4.x 的兼容性坑 |
| ML | scikit-learn 1.9 + XGBoost 3.3 | 业界主流，支持 LR/RF/XGBoost 多模型对比 |
| LLM | openai SDK 2.52 | DeepSeek 兼容 OpenAI 协议，无缝接入 |
| 数据处理 | pandas 2.2 + openpyxl 3.1 | Excel 读写 + 数据清洗 |
| 可视化 | matplotlib 3.11 + seaborn 0.13 | EDA 图表 + 模型评估图表 |
| 测试 | pytest 8.3 | 标准测试框架 |

### 3.3 安全设计

| 安全点 | 实现 |
| --- | --- |
| **密码存储** | bcrypt 哈希（cost factor 12），不存明文 |
| **登录态** | JWT 无状态 Token（HS256 签名，24h 过期） |
| **权限控制** | RBAC：`@login_required` 校验登录，`@role_required("admin")` 校验角色 |
| **防越权注册** | 注册接口服务端硬编码 `role="user"`，拒绝请求体里的 role 字段 |
| **防用户名枚举** | 登录失败统一返回"用户名或密码错误"，不区分用户名是否存在 |
| **异常不泄露堆栈** | 兜底 `@app.errorhandler(Exception)` 返回"服务器内部错误"，堆栈只打印到终端 |
| **三级异常处理器** | `BizException`（业务）→ `HTTPException`（404/405）→ `Exception`（500 兜底），全部转统一信封 |

### 3.4 工程实践亮点

**① 统一响应信封**
```python
{ "code": 0, "message": "success", "data": {...} }
```
业务码体系：`0` 成功，`1xxx` 参数/认证错误，`2xxx` 资源不存在，`3xxx` 模型错误，`5xxx` 服务器错误。

**② 请求级 DB 会话管理**
- `get_db()` 从 Flask `g` 取/建会话，同一请求复用
- `teardown_appcontext` 钩子自动关闭，防连接泄漏

**③ 启动幂等初始化**
- `Base.metadata.create_all()` 自动建表
- `_init_admin()` 首次启动建 `admin/admin123`，已存在则跳过
- `_init_prompt_template()` 同步默认 Prompt 模板

**④ 相对导入避免循环查找**
包内部统一用 `from .config import settings`，避免 `app/__init__.py` 加载期触发顶层包重复查找。

**⑤ 配置与代码分离**
`Pydantic-Settings` 读 `.env`，`BASE_DIR` 用 `__file__` 推导，代码拷到任何机器都能正确定位 `instance/starter.db`。

### 3.5 核心接口实现（30+ 接口）

| 模块 | 方法 | 路径 | 权限 | 功能 |
| --- | --- | --- | --- | --- |
| 认证 | POST | `/api/v1/auth/register` | 公开 | 注册（自动登录） |
| 认证 | POST | `/api/v1/auth/login` | 公开 | 登录返回 JWT |
| 认证 | GET | `/api/v1/auth/me` | 登录 | 获取当前用户 |
| 认证 | POST | `/api/v1/auth/logout` | 登录 | 登出 |
| 认证 | GET | `/api/v1/auth/users` | admin | 用户列表 |
| 数据 | POST | `/api/v1/data/upload` | 登录 | 上传 Excel |
| 数据 | GET | `/api/v1/data/customers` | 登录 | 分页查询客户 |
| 数据 | GET | `/api/v1/data/statistics` | 登录 | 数据概览 |
| 数据 | GET | `/api/v1/data/quality` | 登录 | 质量报告 |
| 数据 | GET | `/api/v1/data/visualization/<type>` | 登录 | EDA 图表 |
| 模型 | POST | `/api/v1/model/train` | admin | 训练多模型 |
| 模型 | GET | `/api/v1/model/experiments` | 登录 | 实验记录 |
| 模型 | GET | `/api/v1/model/best` | 登录 | 最佳模型 |
| 模型 | POST | `/api/v1/model/predict` | 登录 | 全量预测 |
| 模型 | POST | `/api/v1/model/predict_upload` | 登录 | 上传预测 |
| 模型 | GET | `/api/v1/model/visualization/<type>` | 登录 | 评估图表 |
| 模型 | GET | `/api/v1/model/export/<name>` | admin | 导出模型 |
| 模型 | POST | `/api/v1/model/import` | admin | 导入模型 |
| 邮件 | GET | `/api/v1/email/targets` | 登录 | 高潜客户筛选 |
| 邮件 | POST | `/api/v1/email/generate` | 登录 | LLM 生成邮件 |
| 邮件 | GET/PUT | `/api/v1/email/prompt` | 登录 | Prompt 模板 |
| 邮件 | GET | `/api/v1/email/records` | 登录 | 邮件列表 |
| 邮件 | GET/PUT/PATCH/DELETE | `/api/v1/email/records/<id>` | 登录 | 邮件 CRUD |
| 邮件 | DELETE | `/api/v1/email/records` | 登录 | 批量删除 |
| 日志 | GET | `/api/v1/logs` | admin | 操作日志查询 |
| 健康检查 | GET | `/health` | 公开 | 探针 |

---

## 四、R — Result（结果）

### 4.1 交付成果

- ✅ **5 大业务模块、30+ RESTful 接口**全部实现并验证通过
- ✅ **一键启动**：`python run.py` 自动建表 + seed admin + seed prompt，零配置可用
- ✅ **全链路闭环**：数据上传 → ML 训练/预测 → LLM 生成邮件 → 记录管理，一个系统内完成
- ✅ **双模型协同**：ML（XGBoost）预测购买概率 → LLM（DeepSeek）生成个性化营销文案
- ✅ **完整文档体系**：PRD / AI 技术方案 / API 文档 / 技术框架 / Postman 测试文档 / 讲义

### 4.2 架构成果

| 维度 | 成果 |
| --- | --- |
| **分层清晰** | Controller / Service / Model / Infra 四层，职责单一，新增模块只需加蓝图 |
| **安全合规** | bcrypt + JWT + RBAC + 三级异常处理，所有接口鉴权到位 |
| **可扩展性** | v1 蓝图聚合，未来加 v2 不影响 v1；业务码体系支撑错误溯源 |
| **可维护性** | 统一响应信封、相对导入、配置分离、代码注释完整（含 MVC 归属标注） |
| **可测试性** | 原生 SQLAlchemy 让 Model 层独立于 Web 框架，pytest 可直接测业务逻辑 |

### 4.3 技术沉淀

过程中解决的关键工程问题：

1. **`ImportError: create_app (unknown location)`** — 根因是 `app/__init__.py` 丢失导致 namespace 包 + 绝对导入循环查找，改相对导入修复
2. **SQLite 路径 `WinError 123`** — `sqlite:///` 前缀被 Windows 当非法盘符，用 `BASE_DIR` 推导绝对路径修复
3. **`.env` 算术表达式不解析** — pydantic-settings 不认 `60 * 24`，改为数值 `1440`
4. **bcrypt 4.x 兼容性** — 直接用 bcrypt 库而非 passlib，避开 `AttributeError: __about__`
5. **包导入期循环** — `core/__init__.py` 不做提前 export，按需显式导入

---

## 五、一句话总结

> 基于 Flask + SQLAlchemy 2.0 构建**保险精准营销系统**后端，采用 MVC + 应用工厂架构，打通"数据导入 → ML 训练/预测 → LLM 生成营销邮件 → 操作审计"全链路，实现 30+ RESTful 接口，含 JWT 认证、RBAC 权限、统一异常处理，一键启动即用。

---

*文档生成时间：2026-08-03 · 基于项目代码实际扫描*
