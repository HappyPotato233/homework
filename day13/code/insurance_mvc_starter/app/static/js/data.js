/* 数据管理页面：上传/客户列表/统计/质量/EDA 可视化 */
const DataPage = {
    currentTab: 'upload',
    currentFilters: { page: 1, per_page: 50, gender: '', age_min: null, age_max: null, previously_insured: '', keyword: '' },

    async render() {
        const html = `
        <ul class="nav nav-tabs mb-3">
            <li class="nav-item"><a class="nav-link active" data-tab="upload" onclick="DataPage.switchTab('upload')">数据上传</a></li>
            <li class="nav-item"><a class="nav-link" data-tab="customers" onclick="DataPage.switchTab('customers')">客户列表</a></li>
            <li class="nav-item"><a class="nav-link" data-tab="statistics" onclick="DataPage.switchTab('statistics')">数据统计</a></li>
            <li class="nav-item"><a class="nav-link" data-tab="quality" onclick="DataPage.switchTab('quality')">质量报告</a></li>
            <li class="nav-item"><a class="nav-link" data-tab="visualization" onclick="DataPage.switchTab('visualization')">EDA 可视化</a></li>
        </ul>
        <div id="data-content"></div>`;
        setTimeout(() => this.switchTab('upload'), 0);
        return html;
    },

    switchTab(tab) {
        this.currentTab = tab;
        document.querySelectorAll('[data-tab]').forEach(el => el.classList.toggle('active', el.dataset.tab === tab));
        const c = document.getElementById('data-content');
        if (!c) return;
        c.innerHTML = App.loading();
        if (tab === 'upload') this.renderUpload();
        else if (tab === 'customers') this.loadCustomers(1);
        else if (tab === 'statistics') this.loadStatistics();
        else if (tab === 'quality') this.loadQuality();
        else if (tab === 'visualization') this.renderVisualization();
    },

    /* ===== Tab 1: Upload ===== */
    renderUpload() {
        document.getElementById('data-content').innerHTML = `
        <div class="card">
            <div class="card-header">上传 Excel 数据</div>
            <div class="card-body">
                <div class="upload-zone" id="upload-zone" onclick="document.getElementById('upload-file').click()">
                    <i class="bi bi-cloud-arrow-up"></i>
                    <p>点击或拖拽 Excel 文件到此处上传<br><small class="text-muted">支持 .xlsx / .xls 格式，须含 12 列字段</small></p>
                    <input type="file" id="upload-file" accept=".xlsx,.xls" style="display:none" onchange="DataPage.doUpload()">
                </div>
                <div id="upload-result" class="mt-3"></div>
            </div>
        </div>`;
        // 拖拽支持
        const zone = document.getElementById('upload-zone');
        if (zone) {
            zone.ondragover = (e) => { e.preventDefault(); zone.classList.add('dragover'); };
            zone.ondragleave = () => zone.classList.remove('dragover');
            zone.ondrop = (e) => {
                e.preventDefault(); zone.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                if (file) { document.getElementById('upload-file').files = e.dataTransfer.files; this.doUpload(); }
            };
        }
    },

    async doUpload() {
        const fileInput = document.getElementById('upload-file');
        const file = fileInput.files[0];
        if (!file) return;
        const resultDiv = document.getElementById('upload-result');
        resultDiv.innerHTML = App.loading();
        try {
            const data = await API.uploadData(file);
            const qr = data.quality_report || {};
            const missingRows = qr.missing_values ? Object.entries(qr.missing_values).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('') : '';
            const dtypeRows = qr.dtypes ? Object.entries(qr.dtypes).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('') : '';
            resultDiv.innerHTML = `
                <div class="alert alert-success"><i class="bi bi-check-circle"></i> 成功导入 <strong>${data.imported_count}</strong> 条数据</div>
                <div class="card">
                    <div class="card-header">数据质量报告</div>
                    <div class="card-body">
                        <div class="row g-3 mb-3">
                            <div class="col-md-3"><div class="metric-card"><div class="metric-label">总行数</div><div class="metric-value">${qr.total_rows || 0}</div></div></div>
                            <div class="col-md-3"><div class="metric-card"><div class="metric-label">总列数</div><div class="metric-value">${qr.total_cols || 0}</div></div></div>
                            <div class="col-md-3"><div class="metric-card"><div class="metric-label">重复行</div><div class="metric-value">${qr.duplicates || 0}</div></div></div>
                            <div class="col-md-3"><div class="metric-card accent"><div class="metric-label">导入行数</div><div class="metric-value">${data.imported_count}</div></div></div>
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <h6 class="mb-2">缺失值</h6>
                                <div class="table-container"><table class="table"><thead><tr><th>列名</th><th>缺失数</th></tr></thead><tbody>${missingRows || '<tr><td colspan="2" class="text-center text-muted">无缺失</td></tr>'}</tbody></table></div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="mb-2">数据类型</h6>
                                <div class="table-container"><table class="table"><thead><tr><th>列名</th><th>类型</th></tr></thead><tbody>${dtypeRows || '<tr><td colspan="2" class="text-center text-muted">无</td></tr>'}</tbody></table></div>
                            </div>
                        </div>
                    </div>
                </div>`;
            App.toast('数据上传成功', 'success');
        } catch (err) {
            resultDiv.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-circle"></i> ${err.message}</div>`;
            App.toast(err.message, 'error');
        }
    },

    /* ===== Tab 2: Customers ===== */
    async loadCustomers(page) {
        this.currentFilters.page = page;
        const f = this.currentFilters;
        const params = {
            page: f.page, per_page: f.per_page,
            gender: f.gender || undefined,
            age_min: f.age_min || undefined,
            age_max: f.age_max || undefined,
            previously_insured: f.previously_insured !== '' ? f.previously_insured : undefined,
            keyword: f.keyword || undefined,
        };
        document.getElementById('data-content').innerHTML = `
        <div class="card">
            <div class="card-header">客户列表</div>
            <div class="card-body">
                <div class="row g-2 mb-3">
                    <div class="col-md-2"><select class="form-select form-select-sm" id="f-gender" onchange="DataPage.applyFilters()">
                        <option value="">全部性别</option><option value="Male">Male</option><option value="Female">Female</option></select></div>
                    <div class="col-md-2"><input type="number" class="form-control form-control-sm" id="f-age-min" placeholder="年龄下限" onchange="DataPage.applyFilters()"></div>
                    <div class="col-md-2"><input type="number" class="form-control form-control-sm" id="f-age-max" placeholder="年龄上限" onchange="DataPage.applyFilters()"></div>
                    <div class="col-md-2"><select class="form-select form-select-sm" id="f-insured" onchange="DataPage.applyFilters()">
                        <option value="">全部投保状态</option><option value="0">未投保</option><option value="1">已投保</option></select></div>
                    <div class="col-md-2"><input type="text" class="form-control form-control-sm" id="f-keyword" placeholder="按ID搜索" onchange="DataPage.applyFilters()"></div>
                    <div class="col-md-2"><button class="btn btn-primary btn-sm w-100" onclick="DataPage.applyFilters()"><i class="bi bi-search"></i> 筛选</button></div>
                </div>
            </div>
            <div id="customers-table">${App.loading()}</div>
        </div>`;
        // 回填筛选值
        if (f.gender) document.getElementById('f-gender').value = f.gender;
        if (f.age_min) document.getElementById('f-age-min').value = f.age_min;
        if (f.age_max) document.getElementById('f-age-max').value = f.age_max;
        if (f.previously_insured !== '') document.getElementById('f-insured').value = f.previously_insured;
        if (f.keyword) document.getElementById('f-keyword').value = f.keyword;

        try {
            const data = await API.customers(params);
            const headers = ['ID', '性别', '年龄', '驾照', '区域', '已投保', '车龄', '车损', '年保费', '渠道', 'Vintage', 'Response', '预测概率'];
            const rows = (data.items || []).map(c => [
                c.id, c.gender, c.age, c.driving_license, c.region_code,
                c.previously_insured, c.vehicle_age, c.vehicle_damage,
                c.annual_premium, c.policy_sales_channel, c.vintage, c.response,
                App.gauge(c.predicted_prob)
            ]);
            const tableHtml = App.table(headers, rows) + App.pagination(data.total, data.page, data.per_page, 'DataPage.loadCustomers');
            document.getElementById('customers-table').innerHTML = tableHtml;
        } catch (err) {
            document.getElementById('customers-table').innerHTML = App.emptyState('bi-exclamation-circle', err.message);
            App.toast(err.message, 'error');
        }
    },

    applyFilters() {
        this.currentFilters.gender = document.getElementById('f-gender')?.value || '';
        this.currentFilters.age_min = document.getElementById('f-age-min')?.value || null;
        this.currentFilters.age_max = document.getElementById('f-age-max')?.value || null;
        this.currentFilters.previously_insured = document.getElementById('f-insured')?.value ?? '';
        this.currentFilters.keyword = document.getElementById('f-keyword')?.value || '';
        this.loadCustomers(1);
    },

    /* ===== Tab 3: Statistics ===== */
    async loadStatistics() {
        document.getElementById('data-content').innerHTML = App.loading();
        try {
            const s = await API.statistics();
            const total = s.total || 0;
            const male = s.gender_distribution?.Male || 0;
            const female = s.gender_distribution?.Female || 0;
            const resp0 = s.response_distribution?.['0'] || 0;
            const resp1 = s.response_distribution?.['1'] || 0;
            const resp1Pct = total > 0 ? (resp1 / total * 100).toFixed(1) : '0';
            document.getElementById('data-content').innerHTML = `
            <div class="row g-3 mb-3">
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">客户总数</div><div class="metric-value">${total.toLocaleString()}</div></div></div>
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">男性客户</div><div class="metric-value">${male.toLocaleString()}</div><div class="metric-sub">${total > 0 ? (male/total*100).toFixed(1) + '%' : ''}</div></div></div>
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">女性客户</div><div class="metric-value">${female.toLocaleString()}</div><div class="metric-sub">${total > 0 ? (female/total*100).toFixed(1) + '%' : ''}</div></div></div>
                <div class="col-md-3"><div class="metric-card accent"><div class="metric-label">正样本比例</div><div class="metric-value">${resp1Pct}%</div><div class="metric-sub">Response=1: ${resp1} / Response=0: ${resp0}</div></div></div>
            </div>
            <div class="card">
                <div class="card-header">年龄统计</div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4"><div class="metric-card"><div class="metric-label">最小年龄</div><div class="metric-value">${s.age_stats?.min ?? '--'}</div></div></div>
                        <div class="col-md-4"><div class="metric-card"><div class="metric-label">最大年龄</div><div class="metric-value">${s.age_stats?.max ?? '--'}</div></div></div>
                        <div class="col-md-4"><div class="metric-card"><div class="metric-label">平均年龄</div><div class="metric-value">${s.age_stats?.avg ?? '--'}</div></div></div>
                    </div>
                </div>
            </div>`;
        } catch (err) {
            document.getElementById('data-content').innerHTML = App.emptyState('bi-exclamation-circle', err.message);
            App.toast(err.message, 'error');
        }
    },

    /* ===== Tab 4: Quality ===== */
    async loadQuality() {
        document.getElementById('data-content').innerHTML = App.loading();
        try {
            const q = await API.quality();
            const missingRows = q.missing_values ? Object.entries(q.missing_values).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td><td>${q.total_rows > 0 ? (v/q.total_rows*100).toFixed(2) : 0}%</td></tr>`).join('') : '';
            const dtypeRows = q.dtypes ? Object.entries(q.dtypes).map(([k, v]) => `<tr><td>${k}</td><td><code>${v}</code></td></tr>`).join('') : '';
            document.getElementById('data-content').innerHTML = `
            <div class="row g-3 mb-3">
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">总行数</div><div class="metric-value">${q.total_rows || 0}</div></div></div>
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">总列数</div><div class="metric-value">${q.total_cols || 0}</div></div></div>
                <div class="col-md-3"><div class="metric-card accent"><div class="metric-label">重复行</div><div class="metric-value">${q.duplicates || 0}</div></div></div>
                <div class="col-md-3"><div class="metric-card"><div class="metric-label">缺失值总数</div><div class="metric-value">${Object.values(q.missing_values || {}).reduce((a, b) => a + b, 0)}</div></div></div>
            </div>
            <div class="row g-3">
                <div class="col-md-7">
                    <div class="card"><div class="card-header">缺失值详情</div>
                        <div class="table-container"><table class="table"><thead><tr><th>列名</th><th>缺失数</th><th>占比</th></tr></thead><tbody>${missingRows || '<tr><td colspan="3" class="text-center text-muted">无缺失</td></tr>'}</tbody></table></div>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="card"><div class="card-header">数据类型</div>
                        <div class="table-container"><table class="table"><thead><tr><th>列名</th><th>类型</th></tr></thead><tbody>${dtypeRows || '<tr><td colspan="2" class="text-center text-muted">无</td></tr>'}</tbody></table></div>
                    </div>
                </div>
            </div>`;
        } catch (err) {
            document.getElementById('data-content').innerHTML = App.emptyState('bi-exclamation-circle', err.message);
            App.toast(err.message, 'error');
        }
    },

    /* ===== Tab 5: Visualization ===== */
    renderVisualization() {
        const charts = [
            { type: 'response_distribution', label: '正负样本分布', icon: 'bi-bar-chart' },
            { type: 'gender_response', label: '性别-购买交叉', icon: 'bi-grid-3x3' },
            { type: 'age_distribution', label: '年龄分布', icon: 'bi-graph-up' },
            { type: 'premium_distribution', label: '保费分布', icon: 'bi-cash-stack' },
        ];
        document.getElementById('data-content').innerHTML = `
        <div class="card">
            <div class="card-header">EDA 探索性数据分析</div>
            <div class="card-body">
                <div class="d-flex gap-2 flex-wrap mb-3">
                    ${charts.map(c => `<button class="btn btn-outline-primary btn-sm" onclick="DataPage.loadChart('${c.type}')"><i class="bi ${c.icon}"></i> ${c.label}</button>`).join('')}
                </div>
                <div id="chart-display">${App.emptyState('bi-image', '请选择图表类型查看')}</div>
            </div>
        </div>`;
    },

    async loadChart(chartType) {
        const display = document.getElementById('chart-display');
        if (!display) return;
        display.innerHTML = App.loading();
        try {
            const data = await API.dataVisualization(chartType);
            display.innerHTML = `<div class="chart-container"><img src="data:image/png;base64,${data.image_base64}" alt="${chartType}"></div>`;
        } catch (err) {
            display.innerHTML = App.emptyState('bi-exclamation-circle', err.message);
            App.toast(err.message, 'error');
        }
    },
};
