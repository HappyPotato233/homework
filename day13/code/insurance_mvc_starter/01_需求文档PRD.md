# 保险精准营销系统 · 产品需求文档（PRD）

| 文档属性 | 内容 |
| --- | --- |
| 文档版本 | v1.0 |
| 编写日期 | 2026-07-30 |
| 文档状态 | 初稿 |
| 编写人 | 产品组 |
| 对应技术文档 | 02_AI技术方案 / 03_API接口文档 / 04_技术框架方案 |

---

## 1. 项目概述

### 1.1 项目背景

保险公司拥有海量客户数据，但传统营销方式存在以下痛点：

- **营销效率低**：人工筛选客户、撰写邮件，成本高、周期长；
- **转化率低**：无差别投放，对无意向客户造成骚扰，对高潜客户触达不足；
- **数据利用率低**：客户数据沉睡，未通过数据挖掘释放价值；
- **文案同质化**：千篇一律的营销话术，缺乏个性化，客户响应差。

### 1.2 项目目标

构建一套**保险精准营销闭环系统**，打通「数据导入 → 机器学习建模 → 高潜客户筛选 → 大模型个性化营销文案生成」全流程，实现：

| 目标维度 | 具体指标 |
| --- | --- |
| 效率提升 | 客户筛选自动化，邮件文案生成效率提升 10 倍以上 |
| 转化率提升 | 相比随机投放，精准营销转化率提升 50%+ |
| 可解释性 | 提供模型评估可视化、特征重要性，支撑业务决策 |
| 教学价值 | 3 天内让学员掌握企业级 MVC 分层架构 + AI 工程化落地 |

### 1.3 项目范围

**包含功能（In Scope）**：

- 用户认证（注册/登录/登出/RBAC 角色权限）
- 客户数据 Excel 批量导入与数据质量分析
- EDA 可视化（性别分布、年龄分布、保费分布等）
- 机器学习模型训练（LR / RandomForest / XGBoost 三算法对比 + 自动选优）
- 模型评估可视化（ROC 曲线、混淆矩阵、指标对比、特征重要性）
- 全量客户购买概率预测与回写
- 上传数据即时预测（不落库）
- 模型文件导入/导出
- 高潜客户筛选（按预测概率分位数，默认 top 10%）
- 大模型个性化营销邮件自动生成
- Prompt 模板在线管理
- 邮件记录 CRUD（增删改查 + 批量删除）
- 操作审计日志

**暂不包含（Out of Scope，列为扩展点）**：

- SMTP 真实邮件发送
- 模型训练后台异步任务 / 进度推送
- 多租户与数据隔离
- 模型 A/B 测试平台
- 营销转化效果回收分析

---

## 2. 用户角色与权限

### 2.1 角色定义

| 角色 | 描述 | 典型用户 |
| --- | --- | --- |
| admin（管理员） | 拥有全部接口权限，可训练模型、导入/导出模型、查看操作日志 | 数据科学家、系统管理员 |
| user（普通用户） | 可查看数据、运行预测、生成/管理邮件，但不可训练模型、导入/导出模型、查看日志 | 营销运营人员 |

### 2.2 权限矩阵

| 功能模块 | 具体操作 | admin | user |
| --- | --- | --- | --- |
| 认证 | 登录/注册/获取当前用户/登出 | ✅ | ✅ |
| 数据 | 上传 Excel / 客户列表 / 统计概览 / 质量报告 / EDA 可视化 | ✅ | ✅ |
| 模型 | 训练模型 | ✅ | ❌（403） |
| 模型 | 实验记录 / 最佳模型 / 全量预测 / 上传预测 / 评估可视化 | ✅ | ✅ |
| 模型 | 导出模型文件 / 导入模型文件 | ✅ | ❌（403） |
| 邮件 | 高潜筛选 / 生成邮件 / Prompt 管理 / 邮件 CRUD / 批量删除 | ✅ | ✅（仅看自己生成的） |
| 日志 | 操作日志查询 | ✅ | ❌（403） |

### 2.3 默认账号

系统首次启动自动创建管理员账号：

- 用户名：`admin`
- 密码：`admin123`

---

## 3. 功能需求

### 3.1 认证模块（/auth）

#### FR-AUTH-001 用户登录

| 项 | 说明 |
| --- | --- |
| 需求描述 | 用户通过用户名 + 密码登录系统，获取 JWT 令牌 |
| 输入 | username（string，必填）、password（string，必填） |
| 处理逻辑 | 1. 查询用户是否存在；2. bcrypt 校验密码哈希；3. 签发有效期 24h 的 JWT |
| 输出 | access_token、token_type=bearer、expires_in=86400、用户信息（id/username/role） |
| 异常 | 用户名或密码错误 → 统一返回「用户名或密码错误」（防枚举） |

#### FR-AUTH-002 用户注册

| 项 | 说明 |
| --- | --- |
| 需求描述 | 新用户自助注册账号 |
| 输入 | username、password（不含 role 字段） |
| 处理逻辑 | 1. 检查用户名是否唯一；2. bcrypt 哈希密码；3. **服务端硬编码 role=user**（防越权注册 admin） |
| 输出 | 同登录（注册后自动登录） |
| 异常 | 用户名已存在 → code=1004 |

#### FR-AUTH-003 获取当前用户

| 项 | 说明 |
| --- | --- |
| 需求描述 | 根据 Token 返回当前登录用户的基本信息 |
| 前置条件 | 已登录，携带有效 JWT |
| 输出 | `{ id, username, role }` |

#### FR-AUTH-004 退出登录

| 项 | 说明 |
| --- | --- |
| 需求描述 | 用户主动登出 |
| 处理逻辑 | JWT 无状态，前端丢弃 Token 即可 |
| 输出 | 提示「已登出」 |

---

### 3.2 数据模块（/data）

#### FR-DATA-001 上传 Excel 数据

| 项 | 说明 |
| --- | --- |
| 需求描述 | 批量导入保险客户数据集（Excel 格式） |
| 前置条件 | 已登录 |
| 输入 | .xlsx/.xls 文件，必须包含 12 列：id / Gender / Age / Driving_License / Region_Code / Previously_Insured / Vehicle_Age / Vehicle_Damage / Annual_Premium / Policy_Sales_Channel / Vintage / Response |
| 处理逻辑 | 1. 清空 `customers` 旧数据（教学版覆盖策略）；2. pandas 解析 Excel；3. 批量入库（每 5000 条一批，防锁库）；4. 生成数据质量报告 |
| 输出 | imported_count + quality_report（total_rows / total_cols / missing_values / duplicates / dtypes） |
| 异常 | 文件缺失 → 1001；解析失败 → 2002 |

#### FR-DATA-002 客户列表分页查询

| 项 | 说明 |
| --- | --- |
| 需求描述 | 分页查看客户数据，支持多条件筛选 |
| 查询参数 | page（默认1）、per_page（默认50）、gender（Male/Female）、age_min/age_max、previously_insured（0/1）、keyword（按 id 搜索） |
| 输出 | 分页结构 items + total + page + per_page + pages，items 含全字段 + predicted_prob |

#### FR-DATA-003 数据概览统计

| 项 | 说明 |
| --- | --- |
| 需求描述 | 首页展示数据的关键统计指标 |
| 输出 | total（客户总数）、gender_distribution（男女人数）、response_distribution（正负样本比，展示 87:13 不平衡）、age_stats（min/max/avg） |

#### FR-DATA-004 数据质量报告

| 项 | 说明 |
| --- | --- |
| 需求描述 | 独立接口返回当前数据的质量情况，便于数据治理 |
| 输出 | `{ total_rows, total_cols, missing_values, duplicates, dtypes }` |

#### FR-DATA-005 EDA 可视化

| 项 | 说明 |
| --- | --- |
| 需求描述 | 生成探索性数据分析图表，前端直接渲染 base64 PNG |
| 图表类型（chart_type） | `response_distribution`（正负样本柱状图）、`gender_response`（性别-购买交叉热力图）、`age_distribution`（年龄分布直方图）、`premium_distribution`（年保费分布 KDE 图） |
| 输出 | `{ chart_type, image_base64, format: "png" }`，前端 `<img src="data:image/png;base64,...">` 直接显示 |
| 异常 | 未知 chart_type → 1001 |

---

### 3.3 模型模块（/model）

#### FR-MODEL-001 训练模型

| 项 | 说明 |
| --- | --- |
| 需求描述 | 训练机器学习模型，三算法对比并自动选优 |
| 前置条件 | 已登录且角色为 admin；已导入客户数据 |
| 输入（均可选） | models（默认训练全部 3 种，可传子集如 ["xgboost"]）、test_size（默认 0.2）、random_state（默认 42）、params（按模型名覆盖超参） |
| 处理逻辑 | 1. 特征工程（Label 编码 + Ordinal 编码 + StandardScaler 标准化）；2. 分层拆分 stratify=y（保证训练/测试集正负比均为 87:13）；3. 对每种算法启用内置不平衡处理（LR/RF 用 class_weight=balanced，XGBoost 用 scale_pos_weight≈6.7）；4. 计算各模型 Accuracy / Precision / Recall / F1 / **ROC-AUC（选优指标）**；5. 序列化评估数据（ROC 坐标、混淆矩阵、特征重要性）存入 experiments.params；6. model + scaler 一并存盘为 .joblib；7. 标记 ROC-AUC 最高者为 is_best |
| 输出 | best_model（最佳模型名）、results（各模型指标字典） |
| 选优指标 | **ROC-AUC**（衡量排序能力，与营销业务目标「把会买的人排在前面」对齐） |
| 异常 | 无数据 → 2001；普通用户调用 → 403/1003；训练异常 → 500/3001 |

#### FR-MODEL-002 实验记录列表

| 项 | 说明 |
| --- | --- |
| 需求描述 | 分页查询历史训练实验，便于对比复现 |
| 查询参数 | page、per_page（默认50）、model_name（可选过滤） |
| 输出 | items 含 id / model_name / accuracy / precision / recall / f1_score / roc_auc / params / model_path / is_best / created_at |

#### FR-MODEL-003 获取最佳模型

| 项 | 说明 |
| --- | --- |
| 需求描述 | 获取当前 is_best=True 的模型元信息 |
| 输出 | `{ model_name, roc_auc, experiment_id }` |
| 异常 | 无最佳模型 → 3002 |

#### FR-MODEL-004 全量预测

| 项 | 说明 |
| --- | --- |
| 需求描述 | 用最佳（或指定）模型对 customers 全量客户预测购买概率，并回写 DB |
| 前置条件 | 已登录；至少存在一个最佳模型 |
| 输入（可选） | model_name（缺省用最佳模型） |
| 处理逻辑 | 1. 加载 model + scaler（必须复用训练时的 scaler，否则特征分布不一致导致预测失真）；2. 对所有客户执行 predict_proba[:, 1]（取正类概率，而非硬标签）；3. 批量回写 `customers.predicted_prob` 字段 |
| 输出 | `{ model_name, predicted_count }` |
| 关键约束 | 必须用 `predict_proba` 而非 `predict`（保留连续概率用于 top N 排序） |
| 异常 | 模型丢失 → 3002；预测异常 → 500/3002 |

#### FR-MODEL-005 上传数据即时预测

| 项 | 说明 |
| --- | --- |
| 需求描述 | 对上传的新一批客户数据直接预测并返回，不覆盖训练库 |
| 输入 | file（Excel，含 11 个特征列，不含 Response）、可选 model |
| 输出 | `{ model_name, total_count, statistics, predictions }`（直接返回预测结果） |
| 区别点 | 与 FR-MODEL-004 的核心区别：预测结果不入库，仅用于即时分析 |

#### FR-MODEL-006 模型评估可视化

| 项 | 说明 |
| --- | --- |
| 需求描述 | 从 experiments.params 反序列化评估数据，生成评估图表 |
| chart_type | `roc_curve`（ROC 曲线）、`metrics_comparison`（三模型指标对比柱状图）、`confusion_matrix`（混淆矩阵热力图，需 query 参数 model）、`feature_importance`（特征重要性排序，需 query 参数 model） |
| 输出 | `{ chart_type, image_base64, format: "png" }` |

#### FR-MODEL-007 导出模型文件

| 项 | 说明 |
| --- | --- |
| 需求描述 | 下载指定模型的 .joblib 文件，便于离线复用 |
| 前置条件 | admin 角色 |
| 路径参数 | model_name（logistic_regression / xgboost / random_forest） |
| 输出 | 二进制文件流，Content-Disposition: attachment |
| 异常 | 模型不存在 → 3002；普通用户 → 403/1003 |

#### FR-MODEL-008 导入模型文件

| 项 | 说明 |
| --- | --- |
| 需求描述 | 上传外部训练好的 .joblib 模型文件，替换现有同名模型 |
| 前置条件 | admin 角色 |
| 输入 | file（.joblib 文件） |
| 输出 | `{ model_name, path }` |
| 异常 | 非 .joblib → 1001；普通用户 → 403/1003 |

---

### 3.4 邮件模块（/email）

#### FR-EMAIL-001 筛选高潜客户

| 项 | 说明 |
| --- | --- |
| 需求描述 | 按预测概率分位数筛选高潜客户（默认 top 10%） |
| 前置条件 | 已执行 FR-MODEL-004 全量预测，predicted_prob 非空 |
| 查询参数 | percentile（默认 0.9 = top 10%）、page、per_page |
| 处理逻辑 | `threshold = np.quantile(all_probs, percentile)`，取 predicted_prob >= threshold 的客户 |
| 输出 | `{ threshold, total, customers: [...] }`，customers 含 id/性别/年龄/年保费/预测概率 |
| 为什么用分位数 | 不同模型概率分布差异大（LR 偏 0.5，XGBoost 偏两端），分位数保证「永远取 top N%」，策略稳定与模型无关 |
| 异常 | 无预测数据 → 3002 |

#### FR-EMAIL-002 生成营销邮件

| 项 | 说明 |
| --- | --- |
| 需求描述 | 为高潜客户调用大模型批量生成个性化营销邮件 |
| 前置条件 | 已登录；已有预测数据 |
| 输入（二选一） | customer_ids（指定客户 ID 数组）或 limit（缺省自动取 top N，默认 5） |
| 处理链路 | 1. 确定目标客户（指定 / top N）；2. 将客户的 0/1 编码值**反编码为自然语言**（如 driving_license=1 → "有驾照"，vehicle_damage=Yes → "车辆曾受损"）—— 这是 ML → LLM 的桥梁；3. 从 DB 读取激活的 Prompt 模板，用 str.format 注入客户画像；4. 调用 qwen-flash（OpenAI 兼容协议，temperature=0.7）；5. 正则清理 LLM 输出可能的 ```json markdown 包裹；6. json.loads 解析 subject + content；7. 逐条写入 email_records（含成功/失败状态）；8. 记录操作日志 |
| LLM 降级策略 | 未配置 LLM_API_KEY 或单次调用失败时，不抛出异常拖垮整体，仅该条记录 status=failed，其他客户继续 |
| 输出 | `{ generated_count, failed_count, records: [{customer_id, status, subject}] }` |

#### FR-EMAIL-003 获取 Prompt 模板

| 项 | 说明 |
| --- | --- |
| 需求描述 | 查看当前生效的营销邮件 Prompt 模板 |
| 输出 | `{ name, content }`，content 中含 `{gender}` / `{age}` 等命名占位符 |

#### FR-EMAIL-004 更新 Prompt 模板

| 项 | 说明 |
| --- | --- |
| 需求描述 | 运营人员在线编辑 Prompt 模板，无需重新部署 |
| 输入 | `{ content: string }`（需保留必要占位符） |
| 处理逻辑 | 将旧模板 is_active 置为 False，插入新模板并标记 is_active=True（保留历史版本可追溯） |
| 输出 | 更新后的 `{ name, content }` |

#### FR-EMAIL-005 邮件记录列表

| 项 | 说明 |
| --- | --- |
| 需求描述 | 分页查询已生成的邮件记录 |
| 查询参数 | page、per_page（默认50）、status（generated / failed / sent） |
| 权限差异 | user 角色仅看到自己 created_by=当前用户的记录；admin 看到全部记录，并附带 created_by_username |
| 输出 | items 含 id / customer_id / subject / status / created_at |

#### FR-EMAIL-006 邮件详情

| 项 | 说明 |
| --- | --- |
| 需求描述 | 查看单封邮件的完整 HTML 正文 |
| 路径参数 | record_id |
| 输出 | 含 content（完整正文）的全部字段 |
| 异常 | 记录不存在 → 2001 |

#### FR-EMAIL-007 更新邮件内容

| 项 | 说明 |
| --- | --- |
| 需求描述 | 运营人员手动微调 LLM 生成的邮件主题/正文 |
| 输入 | `{ email_subject?, email_content? }`（均可选，只传要改的字段） |
| 处理 | 记录操作日志 action=email_update |

#### FR-EMAIL-008 标记邮件状态

| 项 | 说明 |
| --- | --- |
| 需求描述 | 标记邮件为 sent / 重新 failed 等（预留 SMTP 发送后回写） |
| 输入 | `{ status: string }` |
| 处理 | 记录操作日志 action=email_mark |

#### FR-EMAIL-009 删除单条邮件

| 项 | 说明 |
| --- | --- |
| 需求描述 | 删除一条邮件记录 |
| 路径参数 | record_id |
| 处理 | 记录操作日志 action=email_delete |
| 输出 | `{ success: true }` |

#### FR-EMAIL-010 批量删除邮件

| 项 | 说明 |
| --- | --- |
| 需求描述 | 一次性删除多条邮件记录 |
| 输入 | `{ record_ids: array<int> }` |
| 输出 | `{ deleted_count: int }` |

---

### 3.5 日志模块（/logs）

#### FR-LOG-001 操作日志查询

| 项 | 说明 |
| --- | --- |
| 需求描述 | 管理员审计全量关键操作 |
| 前置条件 | admin 角色 |
| 查询参数 | page、per_page（默认50）、user_id（按用户过滤）、action（按操作类型过滤） |
| action 枚举 | `model_training` / `prediction` / `model_import` / `email_generation` / `email_update` / `email_mark` / `email_delete` |
| 输出 | items 含 id / user_id / action / details（JSON，操作详情） / created_at |
| 异常 | 普通用户调用 → 403/1003 |

---

### 3.6 根路由

#### FR-ROOT-001 前端 SPA 入口

| 项 | 说明 |
| --- | --- |
| 需求描述 | GET / 返回前端单页应用 index.html |
| 鉴权 | 否 |

---

## 4. 非功能需求

### 4.1 性能需求

| 编号 | 需求 | 指标 |
| --- | --- | --- |
| NFR-PERF-001 | 38 万行 Excel 导入时间 | ≤ 30 秒（分批 5000 条 commit） |
| NFR-PERF-002 | 三模型训练时间（38 万行） | ≤ 5 分钟（XGBoost 最慢，同步框架可接受） |
| NFR-PERF-003 | 全量预测时间 | ≤ 30 秒 |
| NFR-PERF-004 | 单客户邮件生成延迟 | ≤ 5 秒（含 LLM API 往返） |
| NFR-PERF-005 | 普通查询接口响应时间 | ≤ 2 秒（P95） |

### 4.2 安全需求

| 编号 | 需求 | 实现方式 |
| --- | --- | --- |
| NFR-SEC-001 | 密码安全存储 | bcrypt 哈希（自带随机盐），禁止明文 |
| NFR-SEC-002 | 防撞库枚举 | 登录失败统一返回「用户名或密码错误」，不区分不存在/密码错 |
| NFR-SEC-003 | 防越权注册 admin | 注册接口硬编码 role=user，忽略请求中的 role 字段 |
| NFR-SEC-004 | Token 安全 | JWT 用 JWT_SECRET_KEY 签名，校验签名 + 过期，有效期 24h |
| NFR-SEC-005 | 防异常堆栈泄露 | 三级异常处理器（BizException → HTTPException → Exception），任何异常返回统一信封，生产 500 不暴露堆栈 |
| NFR-SEC-006 | 防 SQL 注入 | 全部用 ORM 或参数化 text()，严禁字符串拼接 SQL |
| NFR-SEC-007 | RBAC 权限隔离 | 训练/导入导出模型/日志接口严格校验 admin 角色 |

### 4.3 可用性需求

| 编号 | 需求 |
| --- | --- |
| NFR-AVAIL-001 | LLM 故障不拖垮业务：调用失败降级为 status=failed，其他流程继续 |
| NFR-AVAIL-002 | Prompt 模板库可降级：DB 无激活模板时使用代码内置 DEFAULT_PROMPT_TEMPLATE 兜底 |
| NFR-AVAIL-003 | 数据可重建：SQLite 数据库为文件级，支持备份恢复 |

### 4.4 可扩展性需求

| 编号 | 需求 |
| --- | --- |
| NFR-EXT-001 | 新增算法：在 ML 服务的模型工厂函数加 elif 分支即可 |
| NFR-EXT-002 | 新增业务模块：新增 api/v1/xxx.py 蓝图 + 在蓝图聚合处注册 |
| NFR-EXT-003 | 换数据库：仅改 .env 的 DATABASE_URL（SQLite → MySQL/PostgreSQL 零代码改动） |
| NFR-EXT-004 | 换大模型：仅改 .env 的 LLM_API_BASE / LLM_MODEL（OpenAI 兼容协议） |
| NFR-EXT-005 | 加角色：role_required("editor") 装饰器可直接复用 |

### 4.5 可维护性需求

| 编号 | 需求 |
| --- | --- |
| NFR-MAIN-001 | 严格分层：路由只做请求/响应，业务逻辑在 services，数据逻辑在 models，工具在 utils |
| NFR-MAIN-002 | 模型层与框架解耦：使用原生 SQLAlchemy 2.0，模型可被 CLI/测试直接复用 |
| NFR-MAIN-003 | 统一响应格式 + 业务异常机制：路由代码清爽无重复 if-err |

### 4.6 兼容性需求

| 编号 | 需求 |
| --- | --- |
| NFR-COMP-001 | Python 版本 ≥ 3.10 |
| NFR-COMP-002 | 操作系统：Windows / macOS / Linux 均可用 |
| NFR-COMP-003 | 浏览器：Chrome / Edge / Firefox 最新版（前端 SPA） |

---

## 5. 数据需求

### 5.1 数据库表结构（6 张表）

| 表名 | 模型名 | 核心字段 | 说明 |
| --- | --- | --- | --- |
| users | User | id, username(唯一), password_hash, role, created_at | 登录账号表；role ∈ {admin, user} |
| customers | Customer | id, gender, age, driving_license, region_code, previously_insured, vehicle_age, vehicle_damage, annual_premium, policy_sales_channel, vintage, response(标签), predicted_prob(预测概率回写字段) | 客户数据表；predicted_prob 初始为 NULL，全量预测后更新 |
| experiments | Experiment | id, model_name, accuracy, precision, recall, f1_score, roc_auc, params(JSON 序列化的评估数据:ROC/混淆矩阵/特征重要性), model_path(.joblib 文件路径), is_best(是否最佳模型), created_at | 训练实验记录表；is_best 最多一个为 True |
| email_records | EmailRecord | id, customer_id(FK→customers), email_subject, email_content(HTML), status(generated/failed/sent), error_msg, created_by(FK→users), created_at | LLM 生成邮件表；一个客户可有多封记录 |
| operation_logs | OperationLog | id, user_id(FK→users), action(枚举), details(JSON), created_at | 操作审计表；action 见 FR-LOG-001 |
| prompt_templates | PromptTemplate | id, name, content(Prompt 正文含占位符), is_active, created_at | Prompt 模板表；is_active=True 为当前生效版本 |

### 5.2 数据关系（ER）

```
users 1 ──N operation_logs        （一个用户多条操作日志）
users 1 ──N email_records         （一个用户生成多封邮件）
customers 1 ──N email_records     （一个客户对应多封生成邮件）
experiments 独立存在              （is_best=True 标记当前最佳模型）
prompt_templates 独立存在         （is_active=True 标记当前模板）
```

### 5.3 关键数据约束

| 约束 | 说明 |
| --- | --- |
| users.username UNIQUE | 用户名唯一索引 |
| customers.id PRIMARY KEY | 客户主键，对应 Excel 的 id 列 |
| experiments UNIQUE(is_best=True) | 仅允许一条 is_best=True（标记前先把旧 best 置为 False） |
| prompt_templates UNIQUE(is_active=True) | 仅允许一条激活模板 |
| customers.response ∈ {0, 1} | 标签列，13% 正样本 / 87% 负样本 |

### 5.4 数据量

| 表 | 预期行数 |
| --- | --- |
| users | 个位数（教学环境） |
| customers | ~38 万行（公开数据集规模） |
| experiments | 数十条（每次训练 3 条） |
| email_records | 数千条（top 10% × 多次生成） |
| operation_logs | 数千条 |
| prompt_templates | 个位数 |

---

## 6. AI 业务流程（端到端闭环）

### 6.1 核心业务闭环

```
步骤 1（数据导入）：运营上传 Excel 客户数据 → 入库 customers → 校验质量报告
          ↓
步骤 2（模型训练）：管理员发起 POST /model/train → 三算法训练 + ROC-AUC 选优 → 存 .joblib + 写 experiments
          ↓
步骤 3（全量预测）：POST /model/predict → 加载最佳模型 + scaler → predict_proba → 回写 predicted_prob
          ↓
步骤 4（高潜筛选）：GET /email/targets?percentile=0.9 → top 10% 高潜客户
          ↓
步骤 5（邮件生成）：POST /email/generate → ML编码反编码为自然语言 → Prompt 注入 → 调 qwen-flash → 邮件入库
          ↓
步骤 6（人工校对/发送）：GET /email/records → 运营微调 → PATCH 标记 sent → 记录操作日志
```

### 6.2 ML → LLM 衔接桥梁（反编码）

| ML 编码字段 | 编码值 | 喂给 LLM 的自然语言 |
| --- | --- | --- |
| Gender | 0 | 性别男 |
| Gender | 1 | 性别女 |
| Driving_License | 0 | 暂无驾照 |
| Driving_License | 1 | 持有驾照 |
| Vehicle_Age | 0 | 车龄不满 1 年 |
| Vehicle_Age | 1 | 车龄 1-2 年 |
| Vehicle_Age | 2 | 车龄超过 2 年 |
| Vehicle_Damage | 0 | 车辆未受损 |
| Vehicle_Damage | 1 | 车辆曾受损 |
| Previously_Insured | 0 | 未投过保 |
| Previously_Insured | 1 | 已投过保 |

---

## 7. 统一响应与业务码

### 7.1 统一响应信封

所有接口（成功/失败）必须返回：

```json
{ "code": 0, "message": "success", "data": { ... } }
```

### 7.2 业务码表

| code | HTTP 状态码 | 含义 |
| --- | --- | --- |
| 0 | 200 | 成功 |
| 1001 | 400 | 参数校验错误 |
| 1002 | 401 | 未授权 / 用户名或密码错误 / Token 无效或过期 |
| 1003 | 403 | 权限不足 |
| 1004 | 400 | 用户名已存在 |
| 2001 | 404 | 资源不存在 |
| 2002 | 400 | Excel 解析失败 |
| 3001 | 500 | 训练失败 |
| 3002 | 400 / 500 | 无最佳模型 / 模型丢失 / 预测失败 / 无预测数据 |
| 4001 | 500 | 邮件生成失败 |
| 5000 | 500 | 服务器内部错误（兜底） |

---

## 8. 验收标准（Acceptance Criteria）

### 8.1 认证模块

- [ ] AC-AUTH-01：默认 admin/admin123 可正常登录并返回 JWT
- [ ] AC-AUTH-02：新用户注册成功后 role 必为 user（即使请求带 role=admin 也无效）
- [ ] AC-AUTH-03：密码错误和用户不存在返回相同错误信息（防枚举）
- [ ] AC-AUTH-04：超过 24h 的旧 Token 访问 /auth/me 返回 401

### 8.2 数据模块

- [ ] AC-DATA-01：导入 38 万行 Excel 后，statistics 显示正:负 ≈ 13:87
- [ ] AC-DATA-02：重名用户上传后 data/quality 返回 duplicates > 0
- [ ] AC-DATA-03：4 种 EDA 图表均返回合法 base64 PNG，可在浏览器渲染
- [ ] AC-DATA-04：按 gender=Male 筛选后，返回 items 中无 Female

### 8.3 模型模块

- [ ] AC-MODEL-01：三模型训练后，best_model 对应的 results.roc_auc 为三者最大值
- [ ] AC-MODEL-02：全量预测后，customers 表 predicted_prob 全部非空且范围 [0, 1]
- [ ] AC-MODEL-03：上传预测接口返回的 predictions 数量与 Excel 行数一致
- [ ] AC-MODEL-04：user 角色调 /model/train 返回 403/code=1003
- [ ] AC-MODEL-05：修改模型文件名后调 /model/predict 返回 3002（识别丢失）

### 8.4 邮件模块

- [ ] AC-EMAIL-01：percentile=0.9 时，返回的 total ≈ 客户总数 × 10%
- [ ] AC-EMAIL-02：配置有效 LLM_API_KEY 后，POST /email/generate?limit=2 返回 generated_count=2
- [ ] AC-EMAIL-03：未配置 LLM_API_KEY 时，生成的 records 中 status 全为 failed，generated_count=0
- [ ] AC-EMAIL-04：修改 Prompt 模板后，下次生成使用新文案
- [ ] AC-EMAIL-05：user 角色在邮件列表中看不到其他用户生成的记录
- [ ] AC-EMAIL-06：删除不存在的 record_id 返回 2001

### 8.5 日志模块

- [ ] AC-LOG-01：admin 调 /logs 可看到最近一次 model_training / email_generation 记录
- [ ] AC-LOG-02：user 角色调 /logs 返回 403

### 8.6 非功能验收

- [ ] AC-NFR-01：故意触发除零错误，接口返回 5000 而非 Python 堆栈
- [ ] AC-NFR-02：切换 DATABASE_URL 为 MySQL 后代码零改动正常运行
- [ ] AC-NFR-03：大模型调用超时，generated_count 正常（失败的记录标记为 failed）

---

## 9. 风险与对策（业务视角）

| 风险类别 | 具体风险 | 业务影响 | 对策 |
| --- | --- | --- | --- |
| 数据质量 | Excel 缺列/格式错误 | 导入失败或数据失真 | 上传时严格校验 12 列结构 + 返回质量报告 |
| 数据不平衡 | 正负样本 1:6.7 导致模型偏向猜 0 | 高潜客户被漏判 | 三算法启用 class_weight / scale_pos_weight + ROC-AUC 选优 |
| 模型一致性 | 预测时用错 scaler | 概率全部失真，营销效果归零 | model+scaler 绑定存盘 + 绑定加载，强制复用 |
| LLM 稳定性 | 输出非 JSON（markdown 包裹） | 邮件解析失败，批量生成批量挂 | 正则清理 ```json 包裹 + try/except 降级 + 单条失败不影响其他 |
| LLM 可用性 | API 服务不可用 / Key 未配 | 营销邮件功能不可用 | client=None 兜底 + 记录 failed 不抛异常，其余业务正常 |
| 成本控制 | 对全量 38 万调用 LLM | 单次营销成本过高 | 仅对 top 10% 高潜客户调用，预计 3.8 万次 |
| 安全越权 | 用户注册为 admin | 数据泄露/模型被篡改 | 注册接口硬编码 role=user，admin 仅启动时 seed 创建 |
| 性能瓶颈 | 38 万行一次 commit 锁库 | 导入超时 + 其他请求阻塞 | bulk_insert_mappings 分批 5000 条，每批 commit |

---

## 10. 文档变更记录

| 版本 | 日期 | 变更内容 | 编写人 |
| --- | --- | --- | --- |
| v1.0 | 2026-07-30 | 首版需求文档，基于 AI 技术方案、API 文档、技术框架方案整合完成 | 产品组 |
