/* 主应用：路由、布局、状态管理、通用组件 */
const App = {
    state: { user: null },

    /* ===== 路由表 ===== */
    routes: {
        '/auth/login': { render: () => Auth.renderLogin(), public: true, title: '登录' },
        '/auth/register': { render: () => Auth.renderRegister(), public: true, title: '注册' },
        '/dashboard': { render: () => App.renderDashboard(), title: '仪表盘' },
        '/data': { render: () => DataPage.render(), title: '数据管理' },
        '/model': { render: () => ModelPage.render(), title: '模型管理' },
        '/email': { render: () => EmailPage.render(), title: '邮件营销' },
        '/logs': { render: () => LogPage.render(), title: '操作日志', admin: true },
        '/auth/profile': { render: () => Auth.renderProfile(), title: '个人设置' },
    },

    /* ===== 初始化 ===== */
    async init() {
        window.addEventListener('popstate', () => this.router());
        const token = API.getToken();
        if (token) {
            try { this.state.user = await API.me(); }
            catch { API.clearToken(); }
        }
        const path = location.pathname;
        if (!path || path === '/') {
            this.navigate(token ? '/dashboard' : '/auth/login');
        } else {
            this.router();
        }
    },

    /* ===== 路由跳转（history 模式） ===== */
    navigate(path) {
        history.pushState(null, '', path);
        this.router();
    },

    /* ===== 路由器 ===== */
    async router() {
        const path = location.pathname || '/auth/login';
        const route = this.routes[path];
        if (!route) { this.navigate('/dashboard'); return; }

        // 路由守卫
        if (!route.public && !API.getToken()) { this.navigate('/auth/login'); return; }
        if (route.admin && this.state.user?.role !== 'admin') { this.navigate('/dashboard'); return; }

        // 渲染
        try {
            if (route.public) {
                document.getElementById('app').innerHTML = await route.render();
            } else {
                if (!this.state.user) this.state.user = await API.me();
                document.getElementById('app').innerHTML = this.layout(route.title);
                const content = document.getElementById('page-content');
                content.innerHTML = '<div class="loading-spinner"></div>';
                content.innerHTML = await route.render() || '';
            }
            this.bindLayoutEvents();
        } catch (err) {
            this.toast(err.message || '加载失败', 'error');
        }
    },

    /* ===== 布局 ===== */
    layout(title) {
        const u = this.state.user;
        const isAdmin = u?.role === 'admin';
        return `
        <div class="app-layout">
            <nav class="sidebar">
                <div class="sidebar-brand">
                    <div class="radar-icon"></div>
                    <h5>精准营销</h5>
                </div>
                <div class="sidebar-nav">
                    <div class="nav-section">主功能</div>
                    ${this.navItem('/dashboard', 'bi-speedometer2', '仪表盘')}
                    ${this.navItem('/data', 'bi-database', '数据管理')}
                    ${this.navItem('/model', 'bi-cpu', '模型管理')}
                    ${this.navItem('/email', 'bi-envelope', '邮件营销')}
                    ${isAdmin ? '<div class="nav-section">管理</div>' : ''}
                    ${isAdmin ? this.navItem('/logs', 'bi-list-check', '操作日志') : ''}
                    <div class="nav-section">账号</div>
                    ${this.navItem('/auth/profile', 'bi-person-gear', '个人设置')}
                </div>
                <div class="sidebar-footer">v1.0 · 保险精准营销系统</div>
            </nav>
            <div class="main-area">
                <header class="topbar">
                    <h4>${title}</h4>
                    <div class="topbar-user">
                        <span class="role-badge ${u?.role}">${u?.role || ''}</span>
                        <span>${u?.username || ''}</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="App.logout()"><i class="bi bi-box-arrow-right"></i></button>
                    </div>
                </header>
                <main class="content" id="page-content"></main>
            </div>
        </div>`;
    },

    navItem(path, icon, label) {
        const active = location.pathname === path ? 'active' : '';
        return `<a href="${path}" class="${active}"><i class="bi ${icon}"></i> ${label}</a>`;
    },

    bindLayoutEvents() {},

    async logout() {
        try { await API.logout(); } catch {}
        API.clearToken();
        this.state.user = null;
        this.navigate('/auth/login');
    },

    /* ===== Dashboard ===== */
    async renderDashboard() {
        let stats, best, targets;
        try { stats = await API.statistics(); } catch { stats = null; }
        try { best = await API.bestModel(); } catch { best = null; }
        try { targets = await API.targets({ percentile: 0.9, page: 1, per_page: 1 }); } catch { targets = null; }

        const total = stats?.total || 0;
        const predicted = total > 0 ? total : 0; // predicted_prob 不单独统计
        const highPot = targets?.total || 0;
        const rocAuc = best?.roc_auc ? (best.roc_auc * 100).toFixed(1) + '%' : '--';

        return `
        <div class="funnel mb-4">
            <div class="funnel-step">
                <div class="step-icon"><i class="bi bi-people"></i></div>
                <div class="step-value">${total.toLocaleString()}</div>
                <div class="step-label">总客户数</div>
            </div>
            <div class="funnel-step">
                <div class="step-icon"><i class="bi bi-graph-up"></i></div>
                <div class="step-value">${best ? total.toLocaleString() : '0'}</div>
                <div class="step-label">已预测</div>
            </div>
            <div class="funnel-step">
                <div class="step-icon"><i class="bi bi-stars"></i></div>
                <div class="step-value">${highPot}</div>
                <div class="step-label">高潜客户</div>
            </div>
            <div class="funnel-step">
                <div class="step-icon"><i class="bi bi-envelope-check"></i></div>
                <div class="step-value">--</div>
                <div class="step-label">已生成邮件</div>
            </div>
        </div>
        <div class="row g-3 mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">客户总数</div>
                    <div class="metric-value">${total.toLocaleString()}</div>
                    <div class="metric-sub">${stats ? `男 ${stats.gender_distribution?.Male || 0} / 女 ${stats.gender_distribution?.Female || 0}` : ''}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card accent">
                    <div class="metric-label">正样本比例</div>
                    <div class="metric-value">${stats?.response_distribution ? ((stats.response_distribution['1'] || 0) / total * 100).toFixed(1) + '%' : '--'}</div>
                    <div class="metric-sub">Response=1 占比</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">最佳模型 AUC</div>
                    <div class="metric-value">${best ? best.roc_auc.toFixed(4) : '--'}</div>
                    <div class="metric-sub">${best ? best.model_name : '未训练'}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">年龄范围</div>
                    <div class="metric-value">${stats?.age_stats ? `${stats.age_stats.min}-${stats.age_stats.max}` : '--'}</div>
                    <div class="metric-sub">平均 ${stats?.age_stats?.avg || '--'} 岁</div>
                </div>
            </div>
        </div>
        <div class="row g-3">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">快捷操作</div>
                    <div class="card-body d-grid gap-2">
                        <a href="/data" class="btn btn-primary"><i class="bi bi-upload"></i> 上传数据</a>
                        <a href="/model" class="btn btn-accent ${this.state.user?.role === 'admin' ? '' : 'disabled'}"><i class="bi bi-cpu"></i> 训练模型</a>
                        <a href="/email" class="btn btn-outline-primary"><i class="bi bi-envelope"></i> 生成邮件</a>
                    </div>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">系统状态</div>
                    <div class="card-body">
                        <table class="table">
                            <tbody>
                                <tr><td>数据状态</td><td>${total > 0 ? '<span class="text-success">已导入 ' + total + ' 条</span>' : '<span class="text-danger">未导入</span>'}</td></tr>
                                <tr><td>模型状态</td><td>${best ? '<span class="text-success">已训练 (' + best.model_name + ')</span>' : '<span class="text-danger">未训练</span>'}</td></tr>
                                <tr><td>预测状态</td><td>${targets ? '<span class="text-success">已预测</span>' : '<span class="text-muted">未预测</span>'}</td></tr>
                                <tr><td>当前用户</td><td>${this.state.user?.username} (${this.state.user?.role})</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>`;
    },

    /* ===== 组件 ===== */
    card(title, content, actions = '') {
        return `<div class="card"><div class="card-header d-flex justify-content-between align-items-center">${title}${actions}</div><div class="card-body">${content}</div></div>`;
    },

    table(headers, rows, options = {}) {
        if (!rows || rows.length === 0) return this.emptyState('bi-inbox', '暂无数据');
        const ths = headers.map(h => `<th>${h}</th>`).join('');
        const trs = rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('');
        return `<div class="table-container"><table class="table"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table></div>`;
    },

    pagination(total, page, per_page, onPage) {
        const pages = Math.ceil(total / per_page) || 1;
        if (pages <= 1 && total <= per_page) return '';
        let btns = '';
        for (let i = 1; i <= Math.min(pages, 7); i++) {
            btns += `<button class="${i === page ? 'active' : ''}" onclick="${onPage}(${i})">${i}</button>`;
        }
        if (pages > 7) btns += `<button disabled>...</button><button onclick="${onPage}(${pages})">${pages}</button>`;
        return `<div class="pagination-bar"><span class="page-info">共 ${total} 条，第 ${page}/${pages} 页</span><div class="page-btns">${btns}</div></div>`;
    },

    gauge(prob) {
        if (prob === null || prob === undefined) return '<span class="text-muted">--</span>';
        const pct = (prob * 100).toFixed(1);
        const color = prob >= 0.7 ? 'var(--color-accent)' : prob >= 0.4 ? 'var(--color-warning)' : 'var(--color-muted)';
        return `<div class="gauge"><div class="gauge-bar"><div class="gauge-fill" style="width:${pct}%;background:${color}"></div></div><span class="gauge-value">${pct}%</span></div>`;
    },

    badge(status) {
        const map = { generated: 'badge-generated', failed: 'badge-failed', sent: 'badge-sent' };
        const cls = map[status] || 'badge-failed';
        return `<span class="badge-custom ${cls}">${status}</span>`;
    },

    modal(title, body, onConfirm = null, confirmText = '确认') {
        const m = document.getElementById('modal-container');
        m.classList.add('active');
        m.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-dialog" onclick="event.stopPropagation()">
                <div class="modal-header"><h5>${title}</h5><button class="btn-close" onclick="App.closeModal()"></button></div>
                <div class="modal-body">${body}</div>
                ${onConfirm ? `<div class="modal-footer"><button class="btn btn-outline-primary" onclick="App.closeModal()">取消</button><button class="btn btn-primary" onclick="${onConfirm}">${confirmText}</button></div>` : ''}
            </div>`;
        // 点击 overlay/container 外部关闭弹窗，点击 dialog 内部已被 stopPropagation 阻止
        m.onclick = function() { App.closeModal(); };
    },

    closeModal() {
        const m = document.getElementById('modal-container');
        m.classList.remove('active');
        m.innerHTML = '';
        m.onclick = null;
    },

    toast(message, type = 'info') {
        const c = document.getElementById('toast-container');
        const t = document.createElement('div');
        t.className = `toast-item ${type}`;
        t.textContent = message;
        c.appendChild(t);
        setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 3000);
    },

    loading() { return '<div class="loading-spinner"></div>'; },

    emptyState(icon, message) {
        return `<div class="empty-state"><i class="bi ${icon}"></i><p>${message}</p></div>`;
    },

    fmtTime(t) {
        if (!t) return '--';
        return t.replace('T', ' ').substring(0, 19);
    },
};
