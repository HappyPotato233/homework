/* 认证模块：登录、注册、个人设置 */
const Auth = {

    /* ===== 登录页 ===== */
    renderLogin() {
        return `
        <div class="auth-page">
            <div class="auth-card">
                <div class="auth-card-header">
                    <div class="brand-icon"></div>
                    <h3>保险精准营销系统</h3>
                    <p>精准营销 · 数据驱动</p>
                </div>
                <div class="auth-card-body">
                    <div class="mb-3">
                        <label class="form-label">用户名</label>
                        <input type="text" class="form-control" id="login-username" placeholder="admin">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">密码</label>
                        <input type="password" class="form-control" id="login-password" placeholder="admin123">
                    </div>
                    <button class="btn btn-primary w-100" onclick="Auth.doLogin()">登录</button>
                    <div class="text-center mt-3">
                        <a href="/auth/register">没有账号？立即注册</a>
                    </div>
                    <div class="text-center mt-3 text-muted" style="font-size:12px;">
                        默认账号：admin / admin123
                    </div>
                </div>
            </div>
        </div>`;
    },

    async doLogin() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        if (!username || !password) {
            App.toast('请输入用户名和密码', 'error');
            return;
        }
        try {
            const data = await API.login(username, password);
            API.setToken(data.access_token);
            App.state.user = data.user;
            App.toast('登录成功', 'success');
            App.navigate('/dashboard');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    /* ===== 注册页 ===== */
    renderRegister() {
        return `
        <div class="auth-page">
            <div class="auth-card">
                <div class="auth-card-header">
                    <div class="brand-icon"></div>
                    <h3>注册账号</h3>
                    <p>精准营销 · 数据驱动</p>
                </div>
                <div class="auth-card-body">
                    <div class="mb-3">
                        <label class="form-label">用户名</label>
                        <input type="text" class="form-control" id="reg-username" placeholder="请输入用户名">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">密码</label>
                        <input type="password" class="form-control" id="reg-password" placeholder="至少6位">
                    </div>
                    <button class="btn btn-primary w-100" onclick="Auth.doRegister()">注册</button>
                    <div class="text-center mt-3">
                        <a href="/auth/login">已有账号？返回登录</a>
                    </div>
                </div>
            </div>
        </div>`;
    },

    async doRegister() {
        const username = document.getElementById('reg-username').value.trim();
        const password = document.getElementById('reg-password').value;
        if (!username) {
            App.toast('请输入用户名', 'error');
            return;
        }
        if (password.length < 6) {
            App.toast('密码至少6位', 'error');
            return;
        }
        try {
            const data = await API.register(username, password);
            API.setToken(data.access_token);
            App.state.user = data.user;
            App.toast('注册成功', 'success');
            App.navigate('/dashboard');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    /* ===== 个人设置页 ===== */
    async renderProfile() {
        const u = App.state.user;
        return `
        <div class="row g-3">
            <div class="col-md-6">
                ${App.card('修改用户名', `
                    <div class="mb-3">
                        <label class="form-label">当前用户名</label>
                        <input type="text" class="form-control" value="${u?.username || ''}" disabled>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">新用户名</label>
                        <input type="text" class="form-control" id="profile-username" placeholder="请输入新用户名">
                    </div>
                    <button class="btn btn-primary" onclick="Auth.doUpdateProfile()">保存修改</button>
                `)}
            </div>
            <div class="col-md-6">
                ${App.card('修改密码', `
                    <div class="mb-3">
                        <label class="form-label">原密码</label>
                        <input type="password" class="form-control" id="profile-old-password" placeholder="请输入原密码">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">新密码</label>
                        <input type="password" class="form-control" id="profile-new-password" placeholder="至少6位">
                    </div>
                    <button class="btn btn-primary" onclick="Auth.doUpdatePassword()">保存修改</button>
                `)}
            </div>
        </div>`;
    },

    async doUpdateProfile() {
        const newUsername = document.getElementById('profile-username').value.trim();
        if (!newUsername) {
            App.toast('请输入新用户名', 'error');
            return;
        }
        try {
            const data = await API.updateProfile(newUsername);
            API.setToken(data.access_token);
            App.state.user = data.user;
            App.toast('用户名修改成功', 'success');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async doUpdatePassword() {
        const oldPassword = document.getElementById('profile-old-password').value;
        const newPassword = document.getElementById('profile-new-password').value;
        if (!oldPassword) {
            App.toast('请输入原密码', 'error');
            return;
        }
        if (newPassword.length < 6) {
            App.toast('新密码至少6位', 'error');
            return;
        }
        try {
            const data = await API.updatePassword(oldPassword, newPassword);
            API.setToken(data.access_token);
            App.toast('密码修改成功', 'success');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },
};
