// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : '';  // Same origin in production

// State Management
let currentUser = null;
let authToken = null;

// Utility Functions
function showLoading() {
    document.getElementById('loadingSpinner').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.remove('active');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatCurrency(amount) {
    return parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Tab Switching
function switchTab(tab, evt) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(btn => btn.classList.remove('active'));
    if (evt && evt.target) {
        evt.target.classList.add('active');
    } else {
        // Fallback: highlight the correct tab button
        tabButtons.forEach(btn => {
            if (btn.textContent.toLowerCase().includes(tab)) btn.classList.add('active');
        });
    }

    if (tab === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

function switchDashboardTab(tab, evt) {
    const tabs = document.querySelectorAll('.tab-content');
    const navTabs = document.querySelectorAll('.nav-tab');

    tabs.forEach(t => t.classList.remove('active'));
    navTabs.forEach(t => t.classList.remove('active'));

    if (evt && evt.target) {
        evt.target.classList.add('active');
    } else {
        // Fallback: highlight correct nav tab
        navTabs.forEach(t => {
            if (t.textContent.toLowerCase().includes(tab === 'apply' ? 'apply' : tab)) t.classList.add('active');
        });
    }

    if (tab === 'loans') {
        document.getElementById('loansTab').classList.add('active');
        loadMyLoans();
    } else if (tab === 'apply') {
        document.getElementById('applyTab').classList.add('active');
        calculateEMI();
    } else if (tab === 'transactions') {
        document.getElementById('transactionsTab').classList.add('active');
        loadTransactions();
    } else if (tab === 'admin') {
        document.getElementById('adminTab-content').classList.add('active');
        loadPendingLoans();
    }
}

// Authentication
async function handleLogin(event) {
    event.preventDefault();
    showLoading();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 uses 'username' field
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const data = await response.json();
        authToken = data.access_token;
        currentUser = data.user;

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showDashboard();
        showToast('Login successful!', 'success');
    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading();

    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                password,
                role: 'USER'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        authToken = data.access_token;
        currentUser = data.user;

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showDashboard();
        showToast('Account created successfully!', 'success');
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
    } finally {
        hideLoading();
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');

    document.getElementById('authSection').style.display = 'block';
    document.getElementById('dashboardSection').style.display = 'none';

    showToast('Logged out successfully', 'success');
}

function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';

    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('userRole').textContent = currentUser.role;

    // Show admin tab if user is admin
    if (currentUser.role === 'ADMIN') {
        document.getElementById('adminTab').style.display = 'block';
    }

    refreshBalance();
    loadMyLoans();
}

// Wallet Functions
async function refreshBalance() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/wallet/balance`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to fetch balance');

        const data = await response.json();
        document.getElementById('walletBalance').textContent = formatCurrency(data.balance);
    } catch (error) {
        showToast('Failed to load balance', 'error');
    }
}

// Loan Functions
async function loadMyLoans() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/my-loans`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to fetch loans');

        const loans = await response.json();
        displayLoans(loans);
    } catch (error) {
        showToast('Failed to load loans', 'error');
    } finally {
        hideLoading();
    }
}

function displayLoans(loans) {
    const loansList = document.getElementById('loansList');

    if (loans.length === 0) {
        loansList.innerHTML = '<p class="empty-state">No loans found. Apply for a loan to get started!</p>';
        return;
    }

    loansList.innerHTML = loans.map(loan => `
        <div class="loan-card">
            <div class="loan-header">
                <span class="loan-id">Loan #${loan.id}</span>
                <span class="loan-status status-${loan.status.toLowerCase()}">${loan.status}</span>
            </div>
            <div class="loan-details">
                <div class="detail-item">
                    <span class="detail-label">Principal Amount</span>
                    <span class="detail-value">₹${formatCurrency(loan.principal_amount)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Outstanding</span>
                    <span class="detail-value">₹${formatCurrency(loan.outstanding_amount)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tenure</span>
                    <span class="detail-value">${loan.tenure_months} months</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Interest Rate</span>
                    <span class="detail-value">${loan.interest_rate}% p.a.</span>
                </div>
            </div>
            ${loan.status === 'ACTIVE' ? `
                <div class="loan-actions">
                    <button onclick="openRepaymentModal(${loan.id}, ${loan.outstanding_amount})" 
                            class="btn btn-primary">Make Payment</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

// EMI Calculation
async function calculateEMI() {
    const amount = parseFloat(document.getElementById('loanAmount').value) || 0;
    const tenure = parseInt(document.getElementById('loanTenure').value) || 0;
    const interest = parseFloat(document.getElementById('loanInterest').value) || 12.0;

    if (amount <= 0 || tenure <= 0) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/calculate-emi`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                principal_amount: amount,
                tenure_months: tenure,
                interest_rate: interest
            })
        });

        if (!response.ok) throw new Error('Failed to calculate EMI');

        const data = await response.json();
        document.getElementById('emiAmount').textContent = formatCurrency(data.emi_amount);
        document.getElementById('totalInterest').textContent = formatCurrency(data.total_interest);
        document.getElementById('totalAmount').textContent = formatCurrency(data.total_amount);
    } catch (error) {
        console.error('EMI calculation failed:', error);
    }
}

async function handleLoanApplication(event) {
    event.preventDefault();
    showLoading();

    const amount = parseFloat(document.getElementById('loanAmount').value);
    const tenure = parseInt(document.getElementById('loanTenure').value);
    const interest = parseFloat(document.getElementById('loanInterest').value) || null;

    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/apply`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                principal_amount: amount,
                tenure_months: tenure,
                interest_rate: interest
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Application failed');
        }

        showToast('Loan application submitted successfully!', 'success');
        switchDashboardTab('loans', null);
        event.target.reset();
    } catch (error) {
        showToast(error.message || 'Application failed', 'error');
    } finally {
        hideLoading();
    }
}

// Repayment Functions
function openRepaymentModal(loanId, outstanding) {
    document.getElementById('repaymentLoanId').value = loanId;
    document.getElementById('outstandingAmount').textContent = formatCurrency(outstanding);
    document.getElementById('repaymentAmount').value = '';
    document.getElementById('repaymentAmount').max = outstanding;
    document.getElementById('repaymentModal').classList.add('active');
}

function closeRepaymentModal() {
    document.getElementById('repaymentModal').classList.remove('active');
}

async function handleRepayment(event) {
    event.preventDefault();
    showLoading();

    const loanId = parseInt(document.getElementById('repaymentLoanId').value);
    const amount = parseFloat(document.getElementById('repaymentAmount').value);
    const idempotencyKey = `payment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/repayments/make-payment`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loan_id: loanId,
                amount: amount,
                idempotency_key: idempotencyKey
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Payment failed');
        }

        const data = await response.json();
        closeRepaymentModal();
        showToast(`Payment successful! ${data.loan_closed ? 'Loan closed!' : ''}`, 'success');
        refreshBalance();
        loadMyLoans();
        loadTransactions();
    } catch (error) {
        showToast(error.message || 'Payment failed', 'error');
    } finally {
        hideLoading();
    }
}

// Transaction Functions
async function loadTransactions() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/wallet/transactions?limit=50`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to fetch transactions');

        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        showToast('Failed to load transactions', 'error');
    } finally {
        hideLoading();
    }
}

function displayTransactions(transactions) {
    const transactionsList = document.getElementById('transactionsList');

    if (transactions.length === 0) {
        transactionsList.innerHTML = '<p class="empty-state">No transactions yet.</p>';
        return;
    }

    transactionsList.innerHTML = transactions.map(txn => `
        <div class="transaction-item">
            <div class="transaction-info">
                <h4>${txn.source.replace(/_/g, ' ')}</h4>
                <p>${formatDate(txn.created_at)}</p>
                <p style="font-size: 0.75rem; color: var(--text-secondary);">${txn.description}</p>
            </div>
            <div class="transaction-amount ${txn.type === 'CREDIT' ? 'amount-credit' : 'amount-debit'}">
                ${txn.type === 'CREDIT' ? '+' : '-'}₹${formatCurrency(txn.amount)}
            </div>
        </div>
    `).join('');
}

// Admin Functions
async function loadPendingLoans() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/admin/pending`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to fetch pending loans');

        const loans = await response.json();
        displayPendingLoans(loans);
    } catch (error) {
        showToast('Failed to load pending loans', 'error');
    } finally {
        hideLoading();
    }
}

function displayPendingLoans(loans) {
    const pendingList = document.getElementById('pendingLoansList');

    if (loans.length === 0) {
        pendingList.innerHTML = '<p class="empty-state">No pending loan applications.</p>';
        return;
    }

    pendingList.innerHTML = loans.map(loan => `
        <div class="loan-card">
            <div class="loan-header">
                <span class="loan-id">Loan #${loan.id} - User #${loan.user_id}</span>
                <span class="loan-status status-${loan.status.toLowerCase()}">${loan.status}</span>
            </div>
            <div class="loan-details">
                <div class="detail-item">
                    <span class="detail-label">Amount</span>
                    <span class="detail-value">₹${formatCurrency(loan.principal_amount)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tenure</span>
                    <span class="detail-value">${loan.tenure_months} months</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Interest Rate</span>
                    <span class="detail-value">${loan.interest_rate}% p.a.</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Applied On</span>
                    <span class="detail-value">${formatDate(loan.created_at)}</span>
                </div>
            </div>
            <div class="loan-actions">
                <button onclick="approveLoan(${loan.id})" class="btn btn-success">Approve</button>
                <button onclick="rejectLoan(${loan.id})" class="btn btn-danger">Reject</button>
            </div>
        </div>
    `).join('');
}

async function approveLoan(loanId) {
    if (!confirm('Are you sure you want to approve this loan?')) return;

    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/admin/approve`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loan_id: loanId,
                approved: true
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Approval failed');
        }

        showToast('Loan approved and disbursed successfully!', 'success');
        loadPendingLoans();
    } catch (error) {
        showToast(error.message || 'Approval failed', 'error');
    } finally {
        hideLoading();
    }
}

async function rejectLoan(loanId) {
    if (!confirm('Are you sure you want to reject this loan?')) return;

    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/admin/approve`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loan_id: loanId,
                approved: false,
                rejection_reason: 'Does not meet criteria'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Rejection failed');
        }

        showToast('Loan rejected', 'success');
        loadPendingLoans();
    } catch (error) {
        showToast(error.message || 'Rejection failed', 'error');
    } finally {
        hideLoading();
    }
}

// Initialize app
window.addEventListener('DOMContentLoaded', () => {
    // Check for saved session
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');

    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        
        // Validate token is still valid by calling /api/auth/me
        fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        }).then(response => {
            if (response.ok) {
                showDashboard();
            } else {
                // Token expired or invalid — clear and show login
                handleLogout();
            }
        }).catch(() => {
            // Network error — show login
            handleLogout();
        });
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('repaymentModal');
    if (event.target === modal) {
        closeRepaymentModal();
    }
}
