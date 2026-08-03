/* API 客户端：封装所有 fetch 调用 + token 管理 + 统一错误处理 */
const API = {
    BASE: '/api/v1',

    getToken() { return localStorage.getItem('token'); },
    setToken(token) { localStorage.setItem('token', token); },
    clearToken() { localStorage.removeItem('token'); },

    async request(method, path, options = {}) {
        const headers = { ...options.headers };
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }
        const config = { method, headers, ...options };
        if (options.body && !(options.body instanceof FormData)) {
            config.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
        }
        try {
            const resp = await fetch(this.BASE + path, config);
            const data = await resp.json();
            if (data.code === 0) return data.data;
            if (data.code === 1002) { this.clearToken(); history.pushState(null, '', '/auth/login'); }
            throw { code: data.code, message: data.message };
        } catch (err) {
            if (err.code) throw err;
            throw { code: 5000, message: '网络错误，请检查连接' };
        }
    },

    async upload(path, file, fieldName = 'file', extraFields = {}) {
        const formData = new FormData();
        formData.append(fieldName, file);
        for (const [k, v] of Object.entries(extraFields)) formData.append(k, v);
        return this.request('POST', path, { body: formData });
    },

    async download(path) {
        const headers = {};
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const resp = await fetch(this.BASE + path, { headers });
        if (!resp.ok) throw { code: resp.status, message: '下载失败' };
        return resp.blob();
    },

    /* ===== Auth ===== */
    login: (username, password) => API.request('POST', '/auth/login', { body: { username, password } }),
    register: (username, password) => API.request('POST', '/auth/register', { body: { username, password } }),
    me: () => API.request('GET', '/auth/me'),
    logout: () => API.request('POST', '/auth/logout'),
    users: () => API.request('GET', '/auth/users'),
    updateProfile: (new_username) => API.request('PUT', '/auth/profile', { body: { new_username } }),
    updatePassword: (old_password, new_password) => API.request('PUT', '/auth/password', { body: { old_password, new_password } }),

    /* ===== Data ===== */
    uploadData: (file) => API.upload('/data/upload', file),
    customers: (params = {}) => API.request('GET', '/data/customers' + API.toQuery(params)),
    statistics: () => API.request('GET', '/data/statistics'),
    quality: () => API.request('GET', '/data/quality'),
    dataVisualization: (chart_type) => API.request('GET', `/data/visualization/${chart_type}`),

    /* ===== Model ===== */
    train: (body = {}) => API.request('POST', '/model/train', { body }),
    experiments: (params = {}) => API.request('GET', '/model/experiments' + API.toQuery(params)),
    bestModel: () => API.request('GET', '/model/best'),
    predict: (model_name) => API.request('POST', '/model/predict', { body: model_name ? { model_name } : {} }),
    predictUpload: (file, model) => API.upload('/model/predict_upload', file, 'file', model ? { model } : {}),
    modelVisualization: (chart_type, model) => API.request('GET', `/model/visualization/${chart_type}` + API.toQuery(model ? { model } : {})),
    exportModel: (model_name) => API.download(`/model/export/${model_name}`),
    importModel: (file) => API.upload('/model/import', file),

    /* ===== Email ===== */
    targets: (params = {}) => API.request('GET', '/email/targets' + API.toQuery(params)),
    generateEmails: (body = {}) => API.request('POST', '/email/generate', { body }),
    getPrompt: () => API.request('GET', '/email/prompt'),
    updatePrompt: (content) => API.request('PUT', '/email/prompt', { body: { content } }),
    emailRecords: (params = {}) => API.request('GET', '/email/records' + API.toQuery(params)),
    emailRecord: (id) => API.request('GET', `/email/records/${id}`),
    updateEmailRecord: (id, body) => API.request('PUT', `/email/records/${id}`, { body }),
    markEmailRecord: (id, status) => API.request('PATCH', `/email/records/${id}`, { body: { status } }),
    deleteEmailRecord: (id) => API.request('DELETE', `/email/records/${id}`),
    bulkDeleteEmailRecords: (record_ids) => API.request('DELETE', '/email/records', { body: { record_ids } }),

    /* ===== Logs ===== */
    logs: (params = {}) => API.request('GET', '/logs' + API.toQuery(params)),

    /* ===== Utils ===== */
    toQuery(params) {
        const esc = encodeURIComponent;
        const query = Object.entries(params)
            .filter(([k, v]) => v !== null && v !== undefined && v !== '')
            .map(([k, v]) => `${esc(k)}=${esc(v)}`)
            .join('&');
        return query ? `?${query}` : '';
    }
};
