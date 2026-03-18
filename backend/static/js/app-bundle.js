/* ============================================================
   AgentDoc App Bundle - Auth + Dashboard + Documents + Reviews
   All API calls target /api/* endpoints on the same Django host
   ============================================================ */

// ============================================================
// API CLIENT
// ============================================================
const API = {
    _accessToken: null,
    _refreshToken: null,

    _headers(extra = {}) {
        const h = { 'Content-Type': 'application/json', ...extra };
        if (this._accessToken) h['Authorization'] = `Bearer ${this._accessToken}`;
        return h;
    },

    async _fetch(url, opts = {}) {
        let res = await fetch(url, { ...opts, headers: this._headers(opts.headers) });
        if (res.status === 401 && this._refreshToken) {
            const refreshed = await this._doRefresh();
            if (refreshed) {
                res = await fetch(url, { ...opts, headers: this._headers(opts.headers) });
            }
        }
        return res;
    },

    async _doRefresh() {
        try {
            const res = await fetch('/api/auth/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this._refreshToken }),
            });
            if (!res.ok) { this.clearTokens(); return false; }
            const data = await res.json();
            this._accessToken = data.access;
            localStorage.setItem('access_token', data.access);
            return true;
        } catch { this.clearTokens(); return false; }
    },

    setTokens(access, refresh) {
        this._accessToken = access;
        this._refreshToken = refresh;
        if (access) localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },

    loadTokens() {
        this._accessToken = localStorage.getItem('access_token');
        this._refreshToken = localStorage.getItem('refresh_token');
    },

    clearTokens() {
        this._accessToken = null;
        this._refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    async get(path) {
        return this._fetch(`/api${path}`);
    },

    async post(path, body) {
        return this._fetch(`/api${path}`, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    },

    async postForm(path, formData) {
        // No Content-Type header — browser sets multipart boundary
        const headers = {};
        if (this._accessToken) headers['Authorization'] = `Bearer ${this._accessToken}`;
        return fetch(`/api${path}`, { method: 'POST', headers, body: formData });
    },

    async del(path) {
        return this._fetch(`/api${path}`, { method: 'DELETE' });
    },
};

// ============================================================
// AUTH MODULE
// ============================================================
const Auth = {
    _user: null,

    async init() {
        API.loadTokens();
        if (API._accessToken) {
            try {
                const res = await API.get('/auth/me/');
                if (res.ok) {
                    const data = await res.json();
                    if (data.authenticated) {
                        this._user = data.user;
                        this._updateNav();
                        return;
                    }
                }
            } catch { /* fall through */ }
            API.clearTokens();
        }
        this._user = null;
    },

    isAuthenticated() { return !!this._user; },
    getUser() { return this._user; },

    async login(username, password) {
        const res = await API.post('/auth/login/', { username, password });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        API.setTokens(data.access, data.refresh);
        this._user = data.user;
        this._updateNav();
        return data;
    },

    async signup(payload) {
        const res = await API.post('/auth/signup/', payload);
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Signup failed');
        API.setTokens(data.access, data.refresh);
        this._user = data.user;
        this._updateNav();
        return data;
    },

    async logout() {
        try { await API.post('/auth/logout/', { refresh: API._refreshToken }); } catch { /* ignore */ }
        API.clearTokens();
        this._user = null;
        this._updateNav();
        window.location.hash = '#login';
    },

    _updateNav() {
        const navMenu = document.getElementById('navMenu');
        const userInfo = document.getElementById('userInfo');
        const reviewsLink = document.getElementById('reviewsLink');
        if (!navMenu) return;
        if (this._user) {
            navMenu.style.display = 'flex';
            if (userInfo) userInfo.textContent = this._user.display_name || this._user.username;
            if (reviewsLink) {
                reviewsLink.style.display =
                    (this._user.role === 'reviewer' || this._user.role === 'admin') ? 'block' : 'none';
            }
        } else {
            navMenu.style.display = 'none';
            if (userInfo) userInfo.textContent = '';
        }
    },
};

// ============================================================
// DASHBOARD MODULE
// ============================================================
const Dashboard = {
    async init() {
        const res = await API.get('/dashboard/');
        if (!res.ok) { console.error('Dashboard fetch failed'); return; }
        const data = await res.json();

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        set('totalDocs', data.documents_total ?? 0);
        set('processingDocs', data.status_breakdown?.processing ?? 0);
        set('completedDocs', data.status_breakdown?.completed ?? 0);
        set('reviewDocs', data.reviews_open ?? 0);

        const list = document.getElementById('recentDocsList');
        if (list) {
            if (!data.recent_documents?.length) {
                list.innerHTML = '<div class="empty-state">No documents yet. Upload your first document.</div>';
            } else {
                list.innerHTML = data.recent_documents.map(doc => renderDocItem(doc, false)).join('');
            }
        }
    },
};

// ============================================================
// DOCUMENTS MODULE
// ============================================================
const Documents = {
    async init() {
        this._setupUpload();
        await this._loadList();
    },

    _setupUpload() {
        const form = document.getElementById('uploadForm');
        if (!form || form._bound) return;
        form._bound = true;

        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        if (fileInput && fileName) {
            fileInput.addEventListener('change', () => {
                fileName.textContent = fileInput.files[0]?.name || 'Choose a file...';
            });
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = fileInput?.files[0];
            if (!file) return;

            const statusEl = document.getElementById('uploadStatus');
            const progressBar = document.getElementById('uploadProgress');
            const progressFill = document.getElementById('progressFill');

            const showStatus = (msg, type) => {
                if (!statusEl) return;
                statusEl.textContent = msg;
                statusEl.className = `status-message show ${type}`;
            };

            if (progressBar) progressBar.style.display = 'block';
            if (progressFill) progressFill.style.width = '30%';
            showStatus('Uploading...', '');

            try {
                const fd = new FormData();
                fd.append('file', file);
                fd.append('source_channel', 'web');

                if (progressFill) progressFill.style.width = '60%';
                const res = await API.postForm('/documents/', fd);
                const data = await res.json();

                if (!res.ok) throw new Error(data.detail || 'Upload failed');

                if (progressFill) progressFill.style.width = '100%';
                showStatus(`Document uploaded and processing started (ID: ${data.document?.document_id})`, 'success');
                form.reset();
                if (fileName) fileName.textContent = 'Choose a file...';
                await this._loadList();
            } catch (err) {
                showStatus(err.message, 'error');
            } finally {
                setTimeout(() => { if (progressBar) progressBar.style.display = 'none'; }, 1500);
            }
        });
    },

    async _loadList() {
        const list = document.getElementById('documentsList');
        if (!list) return;
        list.innerHTML = '<div class="empty-state">Loading...</div>';
        try {
            const res = await API.get('/documents/');
            if (!res.ok) throw new Error('Failed to load documents');
            const docs = await res.json();
            if (!docs.length) {
                list.innerHTML = '<div class="empty-state">No documents found. Upload your first document above.</div>';
            } else {
                list.innerHTML = docs.map(doc => renderDocItem(doc, true)).join('');
                list.querySelectorAll('.btn-delete').forEach(btn => {
                    btn.addEventListener('click', () => this._delete(btn.dataset.id));
                });
            }
        } catch (err) {
            list.innerHTML = `<div class="empty-state">${err.message}</div>`;
        }
    },

    async _delete(docId) {
        if (!confirm('Delete this document?')) return;
        const res = await API.del(`/documents/${docId}/`);
        if (res.ok) await this._loadList();
        else alert('Delete failed');
    },
};

// ============================================================
// REVIEWS MODULE
// ============================================================
const Reviews = {
    async init() {
        const list = document.getElementById('reviewsList');
        if (!list) return;
        list.innerHTML = '<div class="empty-state">Loading reviews...</div>';
        try {
            const res = await API.get('/reviews/');
            if (!res.ok) throw new Error('Failed to load reviews');
            const reviews = await res.json();
            if (!reviews.length) {
                list.innerHTML = '<div class="empty-state">No reviews in queue.</div>';
            } else {
                list.innerHTML = reviews.map(r => renderReviewItem(r)).join('');
                list.querySelectorAll('.btn-approve').forEach(btn => {
                    btn.addEventListener('click', () => this._action(btn.dataset.id, 'approve'));
                });
                list.querySelectorAll('.btn-reject').forEach(btn => {
                    btn.addEventListener('click', () => this._action(btn.dataset.id, 'reject'));
                });
            }
        } catch (err) {
            list.innerHTML = `<div class="empty-state">${err.message}</div>`;
        }
    },

    async _action(docId, decision) {
        const res = await API.post(`/reviews/${docId}/action/`, { decision });
        if (res.ok) await this.init();
        else alert(`Action failed: ${decision}`);
    },
};

// ============================================================
// RENDER HELPERS
// ============================================================
function statusClass(status) {
    const map = {
        completed: 'status-completed',
        processing: 'status-processing',
        pending_review: 'status-pending-review',
        failed: 'status-failed',
    };
    return map[status] || 'status-processing';
}

function renderDocItem(doc, showDelete) {
    const deleteBtn = showDelete
        ? `<button class="btn btn-small btn-secondary btn-delete" data-id="${doc.document_id}">Delete</button>`
        : '';
    return `
    <div class="document-item">
        <div class="document-header">
            <span class="document-title">${escHtml(doc.title || doc.file_name || doc.document_id)}</span>
            <span class="document-status ${statusClass(doc.status)}">${escHtml(doc.status || 'unknown')}</span>
        </div>
        <div class="document-meta">
            <span>ID: ${escHtml(doc.document_id)}</span>
            <span>Type: ${escHtml(doc.document_type || doc.document_type_hint || '—')}</span>
            <span>Pages: ${doc.page_count ?? '—'}</span>
        </div>
        <div class="document-actions">${deleteBtn}</div>
    </div>`;
}

function renderReviewItem(r) {
    return `
    <div class="review-item">
        <div class="review-header">
            <div class="review-title">Document: ${escHtml(r.document_id)}</div>
            <div class="review-meta">Status: ${escHtml(r.review_status || '—')} | Action: ${escHtml(r.next_action || '—')}</div>
        </div>
        <div class="review-actions">
            <button class="btn-approve btn-small" data-id="${r.document_id}">Approve</button>
            <button class="btn-reject btn-small" data-id="${r.document_id}">Reject</button>
        </div>
    </div>`;
}

function escHtml(str) {
    return String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ============================================================
// MAIN APP CONTROLLER
// ============================================================
const App = {
    async init() {
        await Auth.init();
        this._setupRouting();
        await this._handleRoute();
    },

    _setupRouting() {
        window.addEventListener('hashchange', () => this._handleRoute());

        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.hash = `#${e.currentTarget.dataset.page}`;
            });
        });

        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const errEl = document.getElementById('loginError');
                try {
                    await Auth.login(
                        document.getElementById('username').value,
                        document.getElementById('password').value
                    );
                    window.location.hash = '#dashboard';
                } catch (err) {
                    if (errEl) { errEl.textContent = err.message; errEl.classList.add('show'); }
                }
            });
        }

        // Signup form
        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const errEl = document.getElementById('signupError');
                const pw = document.getElementById('signupPassword').value;
                const cpw = document.getElementById('signupConfirmPassword').value;
                if (pw !== cpw) {
                    if (errEl) { errEl.textContent = 'Passwords do not match'; errEl.classList.add('show'); }
                    return;
                }
                try {
                    await Auth.signup({
                        username: document.getElementById('signupUsername').value,
                        email: document.getElementById('signupEmail').value,
                        display_name: document.getElementById('signupDisplayName').value,
                        password: pw,
                    });
                    window.location.hash = '#dashboard';
                } catch (err) {
                    if (errEl) { errEl.textContent = err.message; errEl.classList.add('show'); }
                }
            });
        }

        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) logoutBtn.addEventListener('click', (e) => { e.preventDefault(); Auth.logout(); });

        // Auth toggles
        document.querySelectorAll('.show-signup').forEach(el =>
            el.addEventListener('click', (e) => { e.preventDefault(); window.location.hash = '#signup'; }));
        document.querySelectorAll('.show-login').forEach(el =>
            el.addEventListener('click', (e) => { e.preventDefault(); window.location.hash = '#login'; }));
    },

    async _handleRoute() {
        const hash = window.location.hash.slice(1) || 'login';

        if (hash !== 'login' && hash !== 'signup' && !Auth.isAuthenticated()) {
            window.location.hash = '#login';
            return;
        }

        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const page = document.getElementById(`${hash}Page`);
        if (page) {
            page.classList.add('active');
            await this._initPage(hash);
        } else {
            window.location.hash = '#login';
        }
    },

    async _initPage(name) {
        switch (name) {
            case 'dashboard': await Dashboard.init(); break;
            case 'documents': await Documents.init(); break;
            case 'reviews': {
                const user = Auth.getUser();
                if (user && (user.role === 'reviewer' || user.role === 'admin')) {
                    await Reviews.init();
                } else {
                    alert('You do not have permission to access reviews');
                    window.location.hash = '#dashboard';
                }
                break;
            }
        }
    },
};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await App.init();
    } catch (err) {
        console.error('App init failed:', err);
        document.body.innerHTML = `
            <div style="padding:2rem;text-align:center;font-family:sans-serif;">
                <h1>Application Error</h1>
                <p>Failed to initialize. Please refresh the page.</p>
                <p style="color:red;font-size:.9rem;">${err.message}</p>
            </div>`;
    }
});
