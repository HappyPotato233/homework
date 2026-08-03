/* 模型管理模块：训练、实验记录、预测、评估可视化、导入导出 */
const ModelPage = {

    /* ===== 状态 ===== */
    currentTab: 'train',
    experimentsPage: 1,
    experimentsFilter: '',
    trainResults: null,
    currentChart: null,

    /* ===== 常量 ===== */
    MODELS: [
        { name: 'logistic_regression', label: '逻辑回归' },
        { name: 'random_forest', label: '随机森林' },
        { name: 'xgboost', label: 'XGBoost' },
    ],
    CHARTS: [
        { name: 'roc_curve', label: 'ROC 曲线', needsModel: false },
        { name: 'metrics_comparison', label: '指标对比', needsModel: false },
        { name: 'confusion_matrix', label: '混淆矩阵', needsModel: true },
        { name: 'feature_importance', label: '特征重要度', needsModel: true },
    ],

    /* ===== 主渲染 ===== */
    async render() {
        const html = this.buildPage();
        setTimeout(() => this.afterTabSwitch(), 0);
        return html;
    },

    buildPage() {
        const tabs = [
            { name: 'train', label: '训练模型', icon: 'bi-cpu' },
            { name: 'experiments', label: '实验记录', icon: 'bi-clipboard-data' },
            { name: 'predict', label: '预测', icon: 'bi-lightning' },
            { name: 'visualization', label: '评估可视化', icon: 'bi-bar-chart' },
            { name: 'import-export', label: '导入/导出', icon: 'bi-box-arrow-in-down' },
        ];
        const tabsHtml = tabs.map(t => `
            <li class="nav-item">
                <a class="nav-link ${this.currentTab === t.name ? 'active' : ''}"
                   data-tab="${t.name}"
                   href="javascript:void(0)"
                   onclick="ModelPage.switchTab('${t.name}')">
                   <i class="bi ${t.icon}"></i> ${t.label}
                </a>
            </li>`).join('');

        return `
        <ul class="nav nav-tabs mb-3">${tabsHtml}</ul>
        <div id="model-content">${this.renderTab()}</div>`;
    },

    renderTab() {
        switch (this.currentTab) {
            case 'train': return this.renderTrain();
            case 'experiments': return this.renderExperiments();
            case 'predict': return this.renderPredict();
            case 'visualization': return this.renderVisualization();
            case 'import-export': return this.renderImportExport();
            default: return this.renderTrain();
        }
    },

    switchTab(tabName) {
        this.currentTab = tabName;
        document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.tab === tabName);
        });
        document.getElementById('model-content').innerHTML = this.renderTab();
        this.afterTabSwitch();
    },

    afterTabSwitch() {
        if (this.currentTab === 'experiments') {
            this.loadExperiments(this.experimentsPage);
        }
    },

    /* ===== 工具 ===== */
    modelLabel(name) {
        const m = this.MODELS.find(m => m.name === name);
        return m ? m.label : name;
    },

    fmtMetric(val) {
        return (val * 100).toFixed(2) + '%';
    },

    /* ===== Tab 1: 训练模型（仅 admin）===== */
    renderTrain() {
        const isAdmin = App.state.user?.role === 'admin';
        if (!isAdmin) {
            return App.emptyState('bi-shield-lock', '权限不足：仅管理员可训练模型');
        }

        const checkboxes = this.MODELS.map(m => `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="${m.name}" id="train-${m.name}" checked>
                <label class="form-check-label" for="train-${m.name}">${m.label}</label>
            </div>`).join('');

        return App.card('训练模型', `
            <div class="row g-3 align-items-end">
                <div class="col-md-6">
                    <label class="form-label">算法选择</label>
                    <div class="d-flex gap-3">${checkboxes}</div>
                </div>
                <div class="col-md-3">
                    <label class="form-label">测试集比例</label>
                    <input type="number" class="form-control" id="train-test-size" value="0.2" step="0.05" min="0.1" max="0.5">
                </div>
                <div class="col-md-3">
                    <label class="form-label">随机种子</label>
                    <input type="number" class="form-control" id="train-random-state" value="42">
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-accent" onclick="ModelPage.doTrain()">
                    <i class="bi bi-cpu"></i> 开始训练
                </button>
            </div>
            <div id="train-results" class="mt-3"></div>
        `);
    },

    async doTrain() {
        const models = this.MODELS
            .filter(m => document.getElementById(`train-${m.name}`).checked)
            .map(m => m.name);
        if (models.length === 0) {
            App.toast('请至少选择一个算法', 'error');
            return;
        }
        const test_size = parseFloat(document.getElementById('train-test-size').value);
        const random_state = parseInt(document.getElementById('train-random-state').value);

        document.getElementById('train-results').innerHTML = App.loading();
        try {
            const data = await API.train({ models, test_size, random_state });
            this.trainResults = data;
            this.renderTrainResults();
            App.toast(`训练完成，最佳模型：${this.modelLabel(data.best_model)}`, 'success');
        } catch (err) {
            document.getElementById('train-results').innerHTML = '';
            App.toast(err.message, 'error');
        }
    },

    renderTrainResults() {
        const data = this.trainResults;
        if (!data) return;

        const metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc'];
        const labels = ['准确率', '精确率', '召回率', 'F1', 'ROC-AUC'];

        let trs = '';
        for (const m of this.MODELS) {
            const r = data.results[m.name];
            if (!r) continue;
            const isBest = data.best_model === m.name;
            const style = isBest ? 'style="background: rgba(232,168,56,0.08)"' : '';
            const badge = isBest ? ' <span class="badge-custom badge-best">最佳</span>' : '';
            let tds = `<td><strong>${m.label}</strong>${badge}</td>`;
            for (const metric of metrics) {
                const formatted = metric === 'roc_auc'
                    ? r[metric].toFixed(4)
                    : this.fmtMetric(r[metric]);
                tds += `<td>${formatted}</td>`;
            }
            trs += `<tr ${style}>${tds}</tr>`;
        }

        const ths = ['模型', ...labels].map(h => `<th>${h}</th>`).join('');

        document.getElementById('train-results').innerHTML = `
            <h6 class="mb-2">训练结果</h6>
            <div class="table-container">
                <table class="table">
                    <thead><tr>${ths}</tr></thead>
                    <tbody>${trs}</tbody>
                </table>
            </div>`;
    },

    /* ===== Tab 2: 实验记录 ===== */
    renderExperiments() {
        const options = ['<option value="">全部模型</option>']
            .concat(this.MODELS.map(m =>
                `<option value="${m.name}" ${this.experimentsFilter === m.name ? 'selected' : ''}>${m.label}</option>`
            )).join('');

        return App.card('实验记录', `
            <div class="d-flex gap-2 align-items-center mb-3">
                <label class="form-label mb-0">模型筛选</label>
                <select class="form-select form-select-sm" style="width: auto;" id="exp-filter" onchange="ModelPage.filterExperiments()">
                    ${options}
                </select>
            </div>
            <div id="exp-table">${App.loading()}</div>
        `);
    },

    async loadExperiments(page) {
        this.experimentsPage = page;
        const container = document.getElementById('exp-table');
        if (!container) return;
        container.innerHTML = App.loading();
        try {
            const params = { page, per_page: 50 };
            if (this.experimentsFilter) params.model_name = this.experimentsFilter;
            const data = await API.experiments(params);

            const headers = ['ID', '模型', '准确率', '精确率', '召回率', 'F1', 'ROC-AUC', '最佳', '创建时间'];
            const rows = data.items.map(e => [
                e.id,
                this.modelLabel(e.model_name),
                this.fmtMetric(e.accuracy),
                this.fmtMetric(e.precision),
                this.fmtMetric(e.recall),
                this.fmtMetric(e.f1_score),
                e.roc_auc.toFixed(4),
                e.is_best ? '<span class="badge-custom badge-best">最佳</span>' : '<span class="text-muted">-</span>',
                App.fmtTime(e.created_at),
            ]);

            let html = App.table(headers, rows);
            html += App.pagination(data.total, data.page, data.per_page, 'ModelPage.loadExperiments');
            container.innerHTML = html;
        } catch (err) {
            container.innerHTML = App.emptyState('bi-exclamation-triangle', err.message);
            App.toast(err.message, 'error');
        }
    },

    filterExperiments() {
        this.experimentsFilter = document.getElementById('exp-filter').value;
        this.experimentsPage = 1;
        this.loadExperiments(1);
    },

    /* ===== Tab 3: 预测 ===== */
    renderPredict() {
        const modelOptions = '<option value="">默认（最佳模型）</option>' +
            this.MODELS.map(m => `<option value="${m.name}">${m.label}</option>`).join('');

        return `
        <div class="row g-3">
            <div class="col-md-6">
                ${App.card('全量预测', `
                    <p class="text-muted">使用已训练模型对数据库中所有客户进行预测，结果回写至客户记录。</p>
                    <button class="btn btn-accent" onclick="ModelPage.doPredict()">
                        <i class="bi bi-lightning"></i> 执行全量预测
                    </button>
                    <div id="predict-result" class="mt-3"></div>
                `)}
            </div>
            <div class="col-md-6">
                ${App.card('上传预测', `
                    <div class="mb-3">
                        <label class="form-label">选择模型（可选）</label>
                        <select class="form-select" id="upload-model">
                            ${modelOptions}
                        </select>
                    </div>
                    <div class="upload-zone" onclick="document.getElementById('predict-upload-input').click()">
                        <i class="bi bi-file-earmark-spreadsheet"></i>
                        <p>点击上传 Excel 文件（.xlsx / .xls）</p>
                        <input type="file" id="predict-upload-input" hidden accept=".xlsx,.xls" onchange="ModelPage.doPredictUpload()">
                    </div>
                    <div id="upload-predict-result" class="mt-3"></div>
                `)}
            </div>
        </div>`;
    },

    async doPredict() {
        const container = document.getElementById('predict-result');
        container.innerHTML = App.loading();
        try {
            const data = await API.predict();
            container.innerHTML = `
                <div class="metric-card">
                    <div class="metric-label">预测完成</div>
                    <div class="metric-value">${data.predicted_count}</div>
                    <div class="metric-sub">使用模型：${this.modelLabel(data.model_name)}</div>
                </div>`;
            App.toast(`全量预测完成，共 ${data.predicted_count} 条`, 'success');
        } catch (err) {
            container.innerHTML = '';
            App.toast(err.message, 'error');
        }
    },

    async doPredictUpload() {
        const input = document.getElementById('predict-upload-input');
        const file = input.files[0];
        if (!file) return;
        const model = document.getElementById('upload-model').value;
        const container = document.getElementById('upload-predict-result');
        container.innerHTML = App.loading();
        try {
            const data = await API.predictUpload(file, model);
            const s = data.statistics;

            let html = `
                <div class="row g-2 mb-3">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">总预测数</div>
                            <div class="metric-value">${data.total_count}</div>
                            <div class="metric-sub">${this.modelLabel(data.model_name)}</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card accent">
                            <div class="metric-label">正样本</div>
                            <div class="metric-value">${s.positive_count}</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">负样本</div>
                            <div class="metric-value">${s.negative_count}</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-label">平均概率</div>
                            <div class="metric-value">${(s.avg_prob * 100).toFixed(2)}%</div>
                        </div>
                    </div>
                </div>`;

            const headers = ['ID', '预测概率', '预测结果'];
            const rows = data.predictions.map(p => [
                p.id,
                App.gauge(p.predicted_prob),
                p.prediction === 1
                    ? '<span class="badge-custom badge-generated">响应</span>'
                    : '<span class="badge-custom badge-failed">未响应</span>',
            ]);
            html += App.table(headers, rows);
            container.innerHTML = html;
            App.toast(`上传预测完成，共 ${data.total_count} 条`, 'success');
        } catch (err) {
            container.innerHTML = '';
            App.toast(err.message, 'error');
        }
        input.value = '';
    },

    /* ===== Tab 4: 评估可视化 ===== */
    renderVisualization() {
        const buttons = this.CHARTS.map(c =>
            `<button class="btn btn-outline-primary btn-sm" onclick="ModelPage.loadChart('${c.name}')">${c.label}</button>`
        ).join('');
        const options = this.MODELS.map(m => `<option value="${m.name}">${m.label}</option>`).join('');

        return App.card('评估可视化', `
            <div class="d-flex gap-2 flex-wrap mb-3">${buttons}</div>
            <div class="mb-3" id="viz-model-selector" style="display:none;">
                <label class="form-label">选择模型</label>
                <select class="form-select" style="width:auto;" id="viz-model" onchange="ModelPage.onVizModelChange()">
                    ${options}
                </select>
            </div>
            <div id="viz-chart">${App.emptyState('bi-bar-chart', '请选择图表类型查看')}</div>
        `);
    },

    async loadChart(chartType) {
        const chart = this.CHARTS.find(c => c.name === chartType);
        this.currentChart = chartType;

        const selector = document.getElementById('viz-model-selector');
        if (selector) selector.style.display = chart.needsModel ? 'block' : 'none';

        let model = null;
        if (chart.needsModel) {
            const sel = document.getElementById('viz-model');
            model = sel ? sel.value : null;
        }

        const container = document.getElementById('viz-chart');
        container.innerHTML = App.loading();
        try {
            const data = await API.modelVisualization(chartType, model);
            container.innerHTML = `
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.image_base64}" alt="${chart.label}"/>
                </div>`;
        } catch (err) {
            container.innerHTML = App.emptyState('bi-exclamation-triangle', err.message);
            App.toast(err.message, 'error');
        }
    },

    onVizModelChange() {
        if (this.currentChart) {
            this.loadChart(this.currentChart);
        }
    },

    /* ===== Tab 5: 导入/导出（仅 admin）===== */
    renderImportExport() {
        const isAdmin = App.state.user?.role === 'admin';
        if (!isAdmin) {
            return App.emptyState('bi-shield-lock', '权限不足：仅管理员可导入导出模型');
        }

        const exportButtons = this.MODELS.map(m =>
            `<button class="btn btn-outline-primary btn-sm" onclick="ModelPage.doExport('${m.name}')">
                <i class="bi bi-download"></i> ${m.label}
            </button>`
        ).join('');

        return `
        <div class="row g-3">
            <div class="col-md-6">
                ${App.card('导出模型', `
                    <p class="text-muted">下载已训练的模型文件（.joblib）</p>
                    <div class="d-grid gap-2">${exportButtons}</div>
                `)}
            </div>
            <div class="col-md-6">
                ${App.card('导入模型', `
                    <div class="upload-zone" onclick="document.getElementById('import-input').click()">
                        <i class="bi bi-box-arrow-in-down"></i>
                        <p>点击上传模型文件（.joblib）</p>
                        <input type="file" id="import-input" hidden accept=".joblib" onchange="ModelPage.doImport()">
                    </div>
                `)}
            </div>
        </div>`;
    },

    async doExport(modelName) {
        try {
            App.toast('正在下载模型文件...', 'info');
            const blob = await API.exportModel(modelName);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = modelName + '.joblib';
            a.click();
            URL.revokeObjectURL(url);
            App.toast(`模型 ${this.modelLabel(modelName)} 导出成功`, 'success');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async doImport() {
        const input = document.getElementById('import-input');
        const file = input.files[0];
        if (!file) return;
        try {
            const data = await API.importModel(file);
            App.toast(`模型导入成功：${data.model_name}`, 'success');
        } catch (err) {
            App.toast(err.message, 'error');
        }
        input.value = '';
    },
};
