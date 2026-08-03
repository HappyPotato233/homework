/* 邮件营销模块：高潜客户筛选、邮件生成、Prompt 模板、邮件记录管理 */
window.EmailPage = {

    /* ===== 状态 ===== */
    currentTab: 'targets',
    selectedRecords: new Set(),

    // 高潜客户
    targetsPercentile: 0.9,
    targetsPage: 1,
    targetsPerPage: 20,
    targetsData: null,

    // 生成邮件
    generateResult: null,

    // Prompt 模板
    promptData: null,

    // 邮件记录
    recordsPage: 1,
    recordsPerPage: 50,
    recordsStatus: '',
    recordsData: null,

    /* ===== 主渲染 ===== */
    async render() {
        this.currentTab = 'targets';
        this.selectedRecords = new Set();
        this.targetsPage = 1;

        // 预加载首个 Tab（高潜客户），避免闪烁
        let initial = App.loading();
        try {
            this.targetsData = await API.targets({
                percentile: this.targetsPercentile,
                page: 1,
                per_page: this.targetsPerPage,
            });
            initial = this.renderTargets();
        } catch (err) {
            initial = App.emptyState('bi-exclamation-triangle', err.message || '加载失败，请先完成模型预测');
            App.toast(err.message || '加载失败', 'error');
        }
        return this.tabShell(initial);
    },

    /* ===== Tab 外壳 ===== */
    tabShell(content) {
        const tabs = [
            { key: 'targets', label: '高潜客户', icon: 'bi-bullseye' },
            { key: 'generate', label: '生成邮件', icon: 'bi-magic' },
            { key: 'prompt', label: 'Prompt 模板', icon: 'bi-file-earmark-text' },
            { key: 'records', label: '邮件记录', icon: 'bi-envelope' },
        ];
        const tabBtns = tabs.map(t => `
            <li class="nav-item">
                <a class="nav-link ${t.key === this.currentTab ? 'active' : ''}" data-tab="${t.key}"
                   href="#" onclick="EmailPage.switchTab('${t.key}');return false;">
                   <i class="bi ${t.icon}"></i> ${t.label}
                </a>
            </li>`).join('');
        return `
        <ul class="nav nav-tabs mb-3">${tabBtns}</ul>
        <div id="email-content">${content}</div>`;
    },

    /* ===== Tab 切换 ===== */
    switchTab(tabName) {
        this.currentTab = tabName;
        document.querySelectorAll('.nav-tabs .nav-link').forEach(el => {
            el.classList.toggle('active', el.dataset.tab === tabName);
        });
        const el = document.getElementById('email-content');
        if (!el) return;
        el.innerHTML = App.loading();
        if (tabName === 'targets') this.loadTargets(this.targetsPage);
        else if (tabName === 'generate') el.innerHTML = this.renderGenerate();
        else if (tabName === 'prompt') this.loadPrompt();
        else if (tabName === 'records') this.loadRecords(this.recordsPage);
    },

    /* ===== Tab 1：高潜客户 ===== */
    async loadTargets(page) {
        this.targetsPage = page || 1;
        const el = document.getElementById('email-content');
        if (!el) return;
        el.innerHTML = App.loading();
        try {
            this.targetsData = await API.targets({
                percentile: this.targetsPercentile,
                page: this.targetsPage,
                per_page: this.targetsPerPage,
            });
            el.innerHTML = this.renderTargets();
        } catch (err) {
            el.innerHTML = App.emptyState('bi-exclamation-triangle', err.message || '加载失败');
            App.toast(err.message || '加载失败', 'error');
        }
    },

    renderTargets() {
        const d = this.targetsData;
        const topPct = ((1 - this.targetsPercentile) * 100).toFixed(0);
        const rows = (d.customers || []).map(c => [
            c.id,
            c.gender || '--',
            c.age != null ? c.age : '--',
            c.annual_premium != null ? '¥' + Number(c.annual_premium).toLocaleString() : '--',
            App.gauge(c.predicted_prob),
        ]);
        const table = App.table(['ID', 'Gender', 'Age', 'Annual_Premium', 'Predicted_Prob'], rows);
        const pagination = App.pagination(d.total, this.targetsPage, this.targetsPerPage, 'EmailPage.loadTargets');
        const thresholdTxt = d.threshold != null ? d.threshold.toFixed(4) : '--';

        return `
        <div class="row g-3 mb-3">
            <div class="col-lg-8">
                ${App.card('分位数筛选', `
                    <div class="d-flex align-items-center gap-3 flex-wrap">
                        <span class="text-muted" style="white-space:nowrap;">显示</span>
                        <input type="range" class="form-range" style="flex:1;min-width:160px;"
                               id="target-percentile" min="0.5" max="0.99" step="0.01"
                               value="${this.targetsPercentile}"
                               oninput="EmailPage.updatePercentileLabel(this.value)">
                        <span class="badge-custom badge-best" id="target-percentile-label" style="white-space:nowrap;">Top ${topPct}%</span>
                        <button class="btn btn-primary btn-sm" onclick="EmailPage.applyPercentile()">应用</button>
                    </div>
                    <div class="text-muted mt-2" style="font-size:12px;">
                        当前阈值（threshold）：<span class="mono">${thresholdTxt}</span>
                        · 共 <strong>${d.total}</strong> 位高潜客户
                    </div>`)}
            </div>
            <div class="col-lg-4">
                ${App.card('快捷操作', `
                    <button class="btn btn-accent w-100 mb-2" onclick="EmailPage.switchTab('generate')">
                        <i class="bi bi-magic"></i> 生成邮件
                    </button>
                    <div class="text-muted" style="font-size:12px;">基于高潜客户列表批量生成个性化营销邮件</div>`)}
            </div>
        </div>
        ${App.card('高潜客户列表', table + pagination)}`;
    },

    updatePercentileLabel(val) {
        const el = document.getElementById('target-percentile-label');
        if (el) el.textContent = 'Top ' + ((1 - parseFloat(val)) * 100).toFixed(0) + '%';
    },

    applyPercentile() {
        const slider = document.getElementById('target-percentile');
        if (slider) this.targetsPercentile = parseFloat(slider.value);
        this.targetsPage = 1;
        this.loadTargets(1);
    },

    /* ===== Tab 2：生成邮件 ===== */
    renderGenerate() {
        let html = App.card('生成营销邮件', `
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="border rounded p-3 h-100">
                        <h6 class="mb-2"><i class="bi bi-stars text-accent"></i> 自动取 Top N</h6>
                        <div class="text-muted mb-3" style="font-size:12px;">按预测概率降序自动选取前 N 位高潜客户逐条生成邮件</div>
                        <div class="input-group mb-3" style="max-width:220px;">
                            <span class="input-group-text">数量</span>
                            <input type="number" class="form-control" id="gen-limit" min="1" max="100" value="5">
                        </div>
                        <button class="btn btn-accent" onclick="EmailPage.doGenerate()" id="gen-btn-auto">
                            <i class="bi bi-magic"></i> 生成
                        </button>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="border rounded p-3 h-100">
                        <h6 class="mb-2"><i class="bi bi-person-check text-primary"></i> 指定客户 ID</h6>
                        <div class="text-muted mb-3" style="font-size:12px;">输入客户 ID，多个用逗号分隔（如 1, 2, 3），逐条生成</div>
                        <textarea class="form-control mb-3" id="gen-ids" rows="3" placeholder="1, 2, 3"></textarea>
                        <button class="btn btn-primary" onclick="EmailPage.doGenerateByIds()" id="gen-btn-ids">
                            <i class="bi bi-magic"></i> 生成
                        </button>
                    </div>
                </div>
            </div>`);

        if (this.generateResult) {
            html += this.renderGenerateResult();
        } else {
            html += `<div class="mt-3">${App.emptyState('bi-envelope', '尚未生成邮件，请在上方选择生成方式')}</div>`;
        }
        return html;
    },

    renderGenerateResult() {
        const r = this.generateResult;
        const rows = (r.records || []).map(rec => [
            rec.customer_id,
            App.badge(rec.status),
            rec.subject
                ? `<span class="text-truncate d-inline-block" style="max-width:420px;">${this.escape(rec.subject)}</span>`
                : '<span class="text-muted">--</span>',
        ]);
        const total = r.total || (r.generated_count + r.failed_count);
        const done = r.generated_count + r.failed_count;
        const isGenerating = r.isGenerating;
        const pct = total > 0 ? Math.round(done / total * 100) : 100;

        let progressHtml = '';
        if (isGenerating) {
            progressHtml = `
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="text-muted" style="font-size:12px;">正在逐条生成... ${done}/${total}</span>
                        <span class="text-muted" style="font-size:12px;">${pct}%</span>
                    </div>
                    <div class="progress" style="height:6px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" style="width:${pct}%"></div>
                    </div>
                </div>`;
        }

        return `
        <div class="mt-3">
            ${App.card('生成结果', `
                ${progressHtml}
                <div class="row g-2 mb-3">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">成功生成</div>
                            <div class="metric-value text-success">${r.generated_count}</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">失败</div>
                            <div class="metric-value text-danger">${r.failed_count}</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">总计</div>
                            <div class="metric-value">${total}</div>
                        </div>
                    </div>
                </div>
                ${App.table(['Customer_ID', 'Status', 'Subject'], rows)}
                <div class="mt-3 d-flex gap-2 flex-wrap">
                    <button class="btn btn-outline-primary btn-sm" onclick="EmailPage.switchTab('records')">
                        <i class="bi bi-list-ul"></i> 查看邮件记录
                    </button>
                    <button class="btn btn-outline-primary btn-sm" onclick="EmailPage.switchTab('targets')">
                        <i class="bi bi-arrow-left"></i> 返回高潜客户
                    </button>
                </div>`)}
        </div>`;
    },

    async doGenerate() {
        const limit = parseInt(document.getElementById('gen-limit').value) || 5;
        const btn = document.getElementById('gen-btn-auto');
        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 生成中'; }

        try {
            // 先获取 top N 客户 ID
            App.toast('正在获取高潜客户列表...', 'info');
            const targetsData = await API.targets({ percentile: this.targetsPercentile, page: 1, per_page: limit });
            const customerIds = (targetsData.customers || []).map(c => c.id);

            if (customerIds.length === 0) {
                App.toast('无高潜客户数据，请先完成模型预测', 'error');
                if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-magic"></i> 生成'; }
                return;
            }

            await this.generateBatch(customerIds);
        } catch (err) {
            App.toast(err.message || '生成失败', 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-magic"></i> 生成'; }
        }
    },

    async doGenerateByIds() {
        const raw = document.getElementById('gen-ids').value.trim();
        if (!raw) { App.toast('请输入客户 ID', 'error'); return; }
        const ids = raw.split(/[,，\s]+/).map(s => parseInt(s.trim())).filter(n => !isNaN(n));
        if (ids.length === 0) { App.toast('请输入有效的客户 ID', 'error'); return; }

        const btn = document.getElementById('gen-btn-ids');
        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 生成中'; }

        try {
            await this.generateBatch(ids);
        } catch (err) {
            App.toast(err.message || '生成失败', 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-magic"></i> 生成'; }
        }
    },

    /* 逐条生成邮件，每生成一封立即更新结果区域（与邮件记录同步） */
    async generateBatch(customerIds) {
        const total = customerIds.length;
        this.generateResult = {
            generated_count: 0,
            failed_count: 0,
            records: [],
            total: total,
            isGenerating: true,
        };

        // 渲染初始状态（显示进度条）
        document.getElementById('email-content').innerHTML = this.renderGenerate();

        // 逐条生成
        for (const id of customerIds) {
            try {
                const result = await API.generateEmails({ customer_ids: [id] });
                this.generateResult.generated_count += result.generated_count;
                this.generateResult.failed_count += result.failed_count;
                this.generateResult.records.push(...(result.records || []));
            } catch (err) {
                this.generateResult.failed_count += 1;
                this.generateResult.records.push({ customer_id: id, status: 'failed', subject: '' });
            }
            // 每条完成后立即更新结果区域
            document.getElementById('email-content').innerHTML = this.renderGenerate();
        }

        this.generateResult.isGenerating = false;
        document.getElementById('email-content').innerHTML = this.renderGenerate();
        this.notifyGenerateResult();
    },

    notifyGenerateResult() {
        const r = this.generateResult;
        if (r.generated_count > 0) {
            App.toast(`成功生成 ${r.generated_count} 封邮件`, 'success');
        }
        if (r.failed_count > 0 && r.generated_count === 0) {
            App.toast('未配置 LLM_API_KEY，所有邮件标记为 failed', 'info');
        }
    },

    /* ===== Tab 3：Prompt 模板 ===== */
    async loadPrompt() {
        const el = document.getElementById('email-content');
        if (!el) return;
        el.innerHTML = App.loading();
        try {
            this.promptData = await API.getPrompt();
            el.innerHTML = this.renderPrompt();
        } catch (err) {
            el.innerHTML = App.emptyState('bi-exclamation-triangle', err.message || '加载失败');
            App.toast(err.message || '加载失败', 'error');
        }
    },

    renderPrompt() {
        const p = this.promptData || {};
        const vars = ['{gender}', '{age}', '{driving_license}', '{vehicle_age}',
                      '{vehicle_damage}', '{previously_insured}', '{annual_premium}'];
        const varChips = vars.map(v => `<code class="mono">${v}</code>`).join(' ');
        return App.card('Prompt 模板' + (p.name ? ` · ${this.escape(p.name)}` : ''), `
            <div class="mb-2 text-muted" style="font-size:12px;">
                <i class="bi bi-info-circle"></i> 可用变量（生成时自动替换为客户画像）：
                ${varChips}
            </div>
            <textarea class="form-control mono" id="prompt-content" rows="14"
                      style="font-size:13px;">${this.escape(p.content || '')}</textarea>
            <div class="mt-3 d-flex gap-2">
                <button class="btn btn-primary" onclick="EmailPage.doSavePrompt()">
                    <i class="bi bi-save"></i> 保存模板
                </button>
                <button class="btn btn-outline-primary" onclick="EmailPage.loadPrompt()">
                    <i class="bi bi-arrow-counterclockwise"></i> 重载
                </button>
            </div>`);
    },

    async doSavePrompt() {
        const content = document.getElementById('prompt-content').value;
        if (content.trim().length < 10) {
            App.toast('模板内容至少 10 个字符', 'error');
            return;
        }
        try {
            this.promptData = await API.updatePrompt(content);
            App.toast('模板保存成功', 'success');
        } catch (err) {
            App.toast(err.message || '保存失败', 'error');
        }
    },

    /* ===== Tab 4：邮件记录 ===== */
    async loadRecords(page) {
        this.recordsPage = page || 1;
        const el = document.getElementById('email-content');
        if (!el) return;
        el.innerHTML = App.loading();
        try {
            this.recordsData = await API.emailRecords({
                page: this.recordsPage,
                per_page: this.recordsPerPage,
                status: this.recordsStatus || undefined,
            });
            this.selectedRecords = new Set();
            el.innerHTML = this.renderRecords();
        } catch (err) {
            el.innerHTML = App.emptyState('bi-exclamation-triangle', err.message || '加载失败');
            App.toast(err.message || '加载失败', 'error');
        }
    },

    renderRecords() {
        const d = this.recordsData || {};
        const isAdmin = App.state.user?.role === 'admin';
        const items = d.items || [];

        // 状态筛选
        const statusOpts = [
            { v: '', label: '全部' },
            { v: 'generated', label: 'generated' },
            { v: 'failed', label: 'failed' },
            { v: 'sent', label: 'sent' },
        ];
        const opts = statusOpts.map(o =>
            `<option value="${o.v}" ${o.v === this.recordsStatus ? 'selected' : ''}>${o.label}</option>`
        ).join('');

        // 表头
        const allChecked = items.length > 0 && items.every(r => this.selectedRecords.has(r.id));
        const headers = [
            `<th style="width:36px;"><input type="checkbox" class="form-check-input" ${allChecked ? 'checked' : ''} onchange="EmailPage.toggleAllRecords(this.checked)"></th>`,
            '<th>ID</th>', '<th>Customer_ID</th>', '<th>Subject</th>',
            '<th>Status</th>', '<th>Created_At</th>',
        ];
        if (isAdmin) headers.push('<th>Created_By</th>');
        headers.push('<th style="width:180px;">操作</th>');

        // 表体
        let body;
        if (items.length === 0) {
            body = `<tr><td colspan="${headers.length}" style="padding:0;">${App.emptyState('bi-inbox', '暂无邮件记录')}</td></tr>`;
        } else {
            body = items.map(r => {
                const checked = this.selectedRecords.has(r.id) ? 'checked' : '';
                const actions = `
                    <div class="d-flex gap-1">
                        <button class="btn btn-sm btn-outline-primary" title="查看" onclick="event.stopPropagation();EmailPage.viewRecord(${r.id})"><i class="bi bi-eye"></i></button>
                        <button class="btn btn-sm btn-outline-primary" title="编辑" onclick="event.stopPropagation();EmailPage.editRecord(${r.id})"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-outline-success" title="标记已发送" onclick="event.stopPropagation();EmailPage.markSent(${r.id})"><i class="bi bi-send"></i></button>
                        <button class="btn btn-sm btn-outline-danger" title="删除" onclick="event.stopPropagation();EmailPage.confirmDelete(${r.id})"><i class="bi bi-trash"></i></button>
                    </div>`;
                const cells = [
                    `<td><input type="checkbox" class="form-check-input" ${checked} onclick="event.stopPropagation()" onchange="event.stopPropagation();EmailPage.toggleRecord(${r.id}, this.checked)"></td>`,
                    `<td>${r.id}</td>`,
                    `<td>${r.customer_id}</td>`,
                    `<td class="text-truncate" style="max-width:240px;">${r.subject ? this.escape(r.subject) : '<span class="text-muted">--</span>'}</td>`,
                    `<td>${App.badge(r.status)}</td>`,
                    `<td class="mono" style="font-size:12px;">${App.fmtTime(r.created_at)}</td>`,
                ];
                if (isAdmin) cells.push(`<td>${r.created_by_username || '--'}</td>`);
                cells.push(`<td>${actions}</td>`);
                return `<tr style="cursor:pointer;" onclick="EmailPage.viewRecord(${r.id})">${cells.join('')}</tr>`;
            }).join('');
        }

        const table = `<div class="table-container"><table class="table"><thead><tr>${headers.join('')}</tr></thead><tbody>${body}</tbody></table></div>`;
        const pagination = App.pagination(d.total, this.recordsPage, this.recordsPerPage, 'EmailPage.loadRecords');

        return `
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
            <div class="d-flex align-items-center gap-2">
                <label class="form-label mb-0">状态筛选</label>
                <select class="form-select form-select-sm" style="width:auto;" id="records-status" onchange="EmailPage.applyRecordsFilter()">
                    ${opts}
                </select>
            </div>
            <div class="d-flex gap-2 align-items-center">
                <span class="text-muted" id="records-selected-info" style="font-size:12px;">${this.selectedRecords.size > 0 ? '已选 ' + this.selectedRecords.size + ' 项' : ''}</span>
                <button class="btn btn-danger btn-sm" id="records-bulk-delete" ${this.selectedRecords.size === 0 ? 'disabled' : ''} onclick="EmailPage.confirmBulkDelete()">
                    <i class="bi bi-trash"></i> 批量删除
                </button>
                <button class="btn btn-outline-primary btn-sm" onclick="EmailPage.loadRecords(EmailPage.recordsPage)">
                    <i class="bi bi-arrow-clockwise"></i> 刷新
                </button>
            </div>
        </div>
        ${table}
        ${pagination}`;
    },

    applyRecordsFilter() {
        this.recordsStatus = document.getElementById('records-status').value;
        this.recordsPage = 1;
        this.loadRecords(1);
    },

    toggleRecord(id, checked) {
        if (checked) this.selectedRecords.add(id);
        else this.selectedRecords.delete(id);
        this.updateSelectedInfo();
    },

    toggleAllRecords(checked) {
        const items = this.recordsData?.items || [];
        if (checked) items.forEach(r => this.selectedRecords.add(r.id));
        else items.forEach(r => this.selectedRecords.delete(r.id));
        document.getElementById('email-content').innerHTML = this.renderRecords();
    },

    updateSelectedInfo() {
        const info = document.getElementById('records-selected-info');
        if (info) info.textContent = this.selectedRecords.size > 0 ? '已选 ' + this.selectedRecords.size + ' 项' : '';
        const btn = document.getElementById('records-bulk-delete');
        if (btn) btn.disabled = this.selectedRecords.size === 0;
    },

    confirmBulkDelete() {
        const ids = Array.from(this.selectedRecords);
        if (ids.length === 0) return;
        App.modal('批量删除', '确定要删除选中的 ' + ids.length + ' 封邮件吗？', 'EmailPage.doBulkDelete()', '删除');
    },

    async doBulkDelete() {
        const ids = Array.from(this.selectedRecords);
        if (ids.length === 0) { App.closeModal(); return; }
        try {
            const data = await API.bulkDeleteEmailRecords(ids);
            App.closeModal();
            App.toast(`成功删除 ${data.deleted_count} 封邮件`, 'success');
            this.selectedRecords = new Set();
            this.loadRecords(1);
        } catch (err) {
            App.toast(err.message || '删除失败', 'error');
            App.closeModal();
        }
    },

    /* ===== 详情 / 编辑 / 状态 / 删除 ===== */
    async viewRecord(id) {
        App.modal('邮件详情', App.loading(), null);
        try {
            const r = await API.emailRecord(id);
            App.modal(`邮件详情 #${r.id}`, this.detailModalHtml(r), null);
        } catch (err) {
            App.closeModal();
            App.toast(err.message || '加载失败', 'error');
        }
    },

    detailModalHtml(r) {
        // 统一用 iframe 渲染邮件内容（HTML 隔离，可滚动，样式不冲突）
        let iframeSrc;
        if (r.content) {
            // 判断是否已经是 HTML 格式
            const isHtml = /<[a-z][\s\S]*>/i.test(r.content);
            if (isHtml) {
                iframeSrc = r.content;
            } else {
                // 纯文本包装成 HTML
                iframeSrc = `<div style="font-family:sans-serif;padding:16px;color:#333;white-space:pre-wrap;">${this.escape(r.content)}</div>`;
            }
        }
        const contentHtml = iframeSrc
            ? `<iframe srcdoc="${this.escape(iframeSrc)}" style="width:100%;height:400px;border:1px solid var(--color-border);border-radius:var(--radius);background:#fff;" sandbox="allow-same-origin"></iframe>`
            : '<span class="text-muted">（无内容）</span>';
        return `
            <div class="mb-2">
                <div class="text-muted" style="font-size:12px;">主题</div>
                <div class="fw-semibold">${r.subject ? this.escape(r.subject) : '<span class="text-muted">（无主题）</span>'}</div>
            </div>
            <div class="mb-3 d-flex align-items-center gap-2">
                <span class="text-muted" style="font-size:12px;">状态：</span>${App.badge(r.status)}
            </div>
            <div class="mb-3">
                <div class="text-muted mb-1" style="font-size:12px;">正文</div>
                ${contentHtml}
            </div>
            <div class="text-muted mb-3" style="font-size:12px;">
                客户 ID：${r.customer_id} · 创建时间：${App.fmtTime(r.created_at)}
            </div>
            <div class="d-flex gap-2 flex-wrap">
                <button class="btn btn-primary btn-sm" onclick="EmailPage.editRecord(${r.id})">
                    <i class="bi bi-pencil"></i> 编辑
                </button>
                <button class="btn btn-outline-success btn-sm" onclick="EmailPage.markSent(${r.id})">
                    <i class="bi bi-send"></i> 标记已发送
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="EmailPage.confirmDelete(${r.id})">
                    <i class="bi bi-trash"></i> 删除
                </button>
            </div>`;
    },

    async editRecord(id) {
        App.modal('编辑邮件', App.loading(), null);
        try {
            const r = await API.emailRecord(id);
            App.modal(`编辑邮件 #${r.id}`, `
                <div class="mb-3">
                    <label class="form-label">邮件主题</label>
                    <textarea class="form-control" id="edit-subject" rows="2">${this.escape(r.subject || '')}</textarea>
                </div>
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <label class="form-label mb-0">邮件正文（HTML）</label>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary active" id="edit-mode-source" onclick="EmailPage.toggleEditPreview('source')">源码编辑</button>
                            <button class="btn btn-outline-primary" id="edit-mode-preview" onclick="EmailPage.toggleEditPreview('preview')">预览</button>
                        </div>
                    </div>
                    <textarea class="form-control mono" id="edit-content" rows="12" style="font-size:13px;">${this.escape(r.content || '')}</textarea>
                    <iframe id="edit-preview" srcdoc="" style="width:100%;height:300px;border:1px solid var(--color-border);border-radius:var(--radius);background:#fff;display:none;" sandbox="allow-same-origin"></iframe>
                </div>`, `EmailPage.doSaveRecord(${r.id})`, '保存');
        } catch (err) {
            App.closeModal();
            App.toast(err.message || '加载失败', 'error');
        }
    },

    toggleEditPreview(mode) {
        const textarea = document.getElementById('edit-content');
        const preview = document.getElementById('edit-preview');
        const btnSource = document.getElementById('edit-mode-source');
        const btnPreview = document.getElementById('edit-mode-preview');
        if (!textarea || !preview) return;

        if (mode === 'preview') {
            // 更新预览内容
            const raw = textarea.value;
            const isHtml = /<[a-z][\s\S]*>/i.test(raw);
            preview.srcdoc = isHtml ? raw : `<div style="font-family:sans-serif;padding:16px;color:#333;white-space:pre-wrap;">${this.escape(raw)}</div>`;
            textarea.style.display = 'none';
            preview.style.display = 'block';
            btnSource.classList.remove('active');
            btnPreview.classList.add('active');
        } else {
            textarea.style.display = 'block';
            preview.style.display = 'none';
            btnSource.classList.add('active');
            btnPreview.classList.remove('active');
        }
    },

    async doSaveRecord(id) {
        const subject = document.getElementById('edit-subject').value;
        const content = document.getElementById('edit-content').value;
        try {
            await API.updateEmailRecord(id, { email_subject: subject, email_content: content });
            App.closeModal();
            App.toast('邮件保存成功', 'success');
            if (this.currentTab === 'records') this.loadRecords(this.recordsPage);
        } catch (err) {
            App.toast(err.message || '保存失败', 'error');
        }
    },

    async markSent(id) {
        try {
            await API.markEmailRecord(id, 'sent');
            App.closeModal();
            App.toast('已标记为 sent', 'success');
            if (this.currentTab === 'records') this.loadRecords(this.recordsPage);
        } catch (err) {
            App.toast(err.message || '操作失败', 'error');
        }
    },

    confirmDelete(id) {
        App.modal('确认删除', '确定要删除这封邮件吗？', 'EmailPage.doDelete(' + id + ')', '删除');
    },

    async doDelete(id) {
        try {
            await API.deleteEmailRecord(id);
            App.closeModal();
            App.toast('删除成功', 'success');
            if (this.currentTab === 'records') this.loadRecords(this.recordsPage);
        } catch (err) {
            App.toast(err.message || '删除失败', 'error');
            App.closeModal();
        }
    },

    /* ===== 工具 ===== */
    escape(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    },
};
