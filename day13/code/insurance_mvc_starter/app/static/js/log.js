/* 操作日志模块：查询、筛选、分页 */
window.LogPage = {
    perPage: 50,
    currentFilters: { user_id: null, action: null },

    async render() {
        this.currentFilters = { user_id: null, action: null };
        setTimeout(() => this.loadLogs(1), 0);
        return `
        <div class="card mb-3">
            <div class="card-header"><i class="bi bi-funnel"></i> 筛选条件</div>
            <div class="card-body">
                <div class="row g-2 align-items-end">
                    <div class="col-md-3">
                        <label class="form-label">用户 ID</label>
                        <input type="number" class="form-control" id="log-filter-user" placeholder="按用户 ID 筛选">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">操作类型</label>
                        <select class="form-select" id="log-filter-action">
                            <option value="">全部</option>
                            <option value="model_training">model_training</option>
                            <option value="prediction">prediction</option>
                            <option value="model_import">model_import</option>
                            <option value="email_generation">email_generation</option>
                            <option value="email_update">email_update</option>
                            <option value="email_mark">email_mark</option>
                            <option value="email_delete">email_delete</option>
                        </select>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-primary" onclick="LogPage.loadLogs(1)"><i class="bi bi-search"></i> 查询</button>
                    </div>
                </div>
            </div>
        </div>
        <div id="log-content">${App.loading()}</div>`;
    },

    async loadLogs(page = 1) {
        const userIdEl = document.getElementById('log-filter-user');
        const actionEl = document.getElementById('log-filter-action');
        const user_id = userIdEl && userIdEl.value.trim() ? userIdEl.value.trim() : null;
        const action = actionEl && actionEl.value ? actionEl.value : null;
        this.currentFilters = { user_id, action };

        const content = document.getElementById('log-content');
        if (!content) return;
        content.innerHTML = App.loading();

        try {
            const params = { page, per_page: this.perPage };
            if (user_id) params.user_id = user_id;
            if (action) params.action = action;
            const data = await API.logs(params);
            this.renderTable(data, page);
        } catch (err) {
            App.toast(err.message || '加载日志失败', 'error');
            content.innerHTML = App.emptyState('bi-exclamation-triangle', '日志加载失败');
        }
    },

    renderTable(data, page) {
        const content = document.getElementById('log-content');
        if (!content) return;
        const items = data.items || [];
        const headers = ['ID', '用户 ID', '操作', '详情', '创建时间'];
        const rows = items.map(it => [
            it.id,
            it.user_id,
            this.actionBadge(it.action),
            this.fmtDetails(it.details),
            App.fmtTime(it.created_at)
        ]);
        const tableHtml = App.table(headers, rows);
        const paginationHtml = App.pagination(data.total || 0, page, this.perPage, 'LogPage.loadLogs');
        content.innerHTML = App.card(`操作日志（共 ${data.total || 0} 条）`, tableHtml + paginationHtml);
    },

    actionBadge(action) {
        const styles = {
            model_training: 'background:rgba(232,168,56,0.15);color:var(--color-accent-dark)',
            prediction: 'background:rgba(13,79,79,0.12);color:var(--color-primary)',
            model_import: 'background:rgba(232,168,56,0.15);color:var(--color-accent-dark)',
            email_generation: 'background:rgba(45,125,79,0.12);color:var(--color-success)',
            email_update: 'background:rgba(45,125,79,0.12);color:var(--color-success)',
            email_mark: 'background:rgba(45,125,79,0.12);color:var(--color-success)',
            email_delete: 'background:rgba(45,125,79,0.12);color:var(--color-success)'
        };
        const style = styles[action] || 'background:var(--color-border);color:var(--color-muted)';
        return `<span class="badge-custom" style="${style}">${this.escapeHtml(action || '--')}</span>`;
    },

    fmtDetails(details) {
        if (details === null || details === undefined || details === '') {
            return '<span class="text-muted">--</span>';
        }
        const str = typeof details === 'string' ? details : JSON.stringify(details);
        const maxLen = 60;
        const display = str.length > maxLen ? str.substring(0, maxLen) + '…' : str;
        return `<span title="${this.escapeHtml(str)}" style="font-family:var(--font-mono);font-size:12px;word-break:break-all">${this.escapeHtml(display)}</span>`;
    },

    escapeHtml(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
};
