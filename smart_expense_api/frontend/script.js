const API_URL = "http://127.0.0.1:8000";

// --- TIỆN ÍCH ---
const formatVND = (num) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num);
const getToken = () => localStorage.getItem("access_token");

// Biến toàn cục theo dõi trạng thái Sửa
let editingTransactionId = null; 
let allExpenses = []; 

// --- 1. KHỞI TẠO & AUTH ---
document.addEventListener("DOMContentLoaded", () => {
    // Xử lý chuyển đổi Login/Register
    const btnToReg = document.getElementById("to-register");
    const btnToLogin = document.getElementById("to-login");
    const loginBox = document.getElementById("login-form-box");
    const regBox = document.getElementById("register-form-box");

    if (btnToReg && loginBox && regBox) {
        btnToReg.onclick = () => { loginBox.style.display = "none"; regBox.style.display = "block"; };
    }
    if (btnToLogin && loginBox && regBox) {
        btnToLogin.onclick = () => { regBox.style.display = "none"; loginBox.style.display = "block"; };
    }

    // Nếu đã có token thì vào thẳng Dashboard
    if (getToken()) {
        initDashboard();
    }
});

// Xử lý Đăng nhập
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = document.getElementById("login-user").value;
        const pass = document.getElementById("login-pass").value;
        const msgError = document.getElementById("msg-error");

        const formData = new URLSearchParams(); 
        formData.append("username", user); 
        formData.append("password", pass);

        try {
            const res = await fetch(`${API_URL}/users/login`, { 
                method: "POST", 
                headers: { "Content-Type": "application/x-www-form-urlencoded" }, 
                body: formData 
            });
            
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("username", user);
                location.reload(); 
            } else { 
                if(msgError) msgError.innerText = "❌ Sai tài khoản hoặc mật khẩu!"; 
            }
        } catch (err) { 
            console.error(err);
            alert("Lỗi kết nối Server! Đảm bảo Backend đang chạy."); 
        }
    });
}

// Xử lý Đăng ký
const regForm = document.getElementById("register-form");
if (regForm) {
    regForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = document.getElementById("reg-user").value;
        const email = document.getElementById("reg-email").value;
        const pass = document.getElementById("reg-pass").value;

        try {
            const res = await fetch(`${API_URL}/users/register`, { 
                method: "POST", 
                headers: { "Content-Type": "application/json" }, 
                body: JSON.stringify({ username: user, email: email, password: pass }) 
            });
            if (res.ok) { 
                alert("✅ Đăng ký thành công! Vui lòng đăng nhập."); 
                location.reload(); 
            } else { 
                const data = await res.json();
                alert("❌ Đăng ký thất bại: " + (data.detail || "Tên đăng nhập đã tồn tại")); 
            }
        } catch (err) { alert("Lỗi kết nối!"); }
    });
}

// Xử lý Đăng xuất
const btnLogout = document.getElementById("btn-logout");
if (btnLogout) {
    btnLogout.onclick = logoutSession;
}

function logoutSession() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    location.reload();
}

// --- 2. LOGIC DASHBOARD ---
async function initDashboard() {
    const authContainer = document.getElementById("auth-container");
    const dashSection = document.getElementById("dashboard-section");
    const displayName = document.getElementById("display-name");

    if (authContainer) authContainer.style.display = "none";
    if (dashSection) dashSection.style.display = "flex";
    if (displayName) displayName.innerText = localStorage.getItem("username") || "User";

    console.log("🚀 Đang khởi động Dashboard...");
    
    // Gọi hàm quan trọng: Tải danh mục và tự sửa nếu rỗng
    await loadCategoriesAndAutoFill();
    await loadDataAndStats();
}

// ===> HÀM QUAN TRỌNG: TẢI & TỰ TẠO DANH MỤC <===
async function loadCategoriesAndAutoFill() {
    try {
        const token = getToken();
        if (!token) return;

        const res = await fetch(`${API_URL}/categories/`, { 
            headers: { "Authorization": `Bearer ${token}` } 
        });
        
        if (res.status === 401) { logoutSession(); return; }

        let cats = await res.json();
        const select = document.getElementById("inp-category");
        if (!select) return;

        // 1. KIỂM TRA: Nếu danh sách rỗng (User mới) -> TỰ ĐỘNG TẠO
        if (cats.length === 0) {
            console.warn("⚠️ Danh sách trống! Đang tạo tự động...");
            const defaults = ["Lương", "Thưởng", "Tiền ăn", "Tiền nhà", "Tiền sinh hoạt", "Tiền đi lại", "Tiền học", "Đi chơi", "Mua sắm"];
            const promises = defaults.map(name => 
                fetch(`${API_URL}/categories/`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json", 
                        "Authorization": `Bearer ${token}` 
                    },
                    body: JSON.stringify({ name: name })
                })
            );
            await Promise.all(promises);
            await loadCategoriesAndAutoFill(); // Gọi lại chính nó
            return;
        }

        // 2. HIỂN THỊ VÀO SELECT BOX
        select.innerHTML = '<option value="" disabled selected>-- Chọn danh mục --</option>';
        cats.forEach(c => {
            const op = document.createElement("option");
            op.value = c.id; 
            op.textContent = c.name;
            select.appendChild(op);
        });

    } catch (error) { console.error("❌ Lỗi khi tải danh mục:", error); }
}

// --- 3. TẢI DỮ LIỆU & RENDER LIST ---
// Bộ từ điển Icon (Dùng chung)
const iconMap = {
    "ăn": "fa-utensils", "uống": "fa-coffee", "nhà": "fa-home",
    "điện": "fa-bolt", "nước": "fa-tint", "mạng": "fa-wifi",
    "xe": "fa-motorcycle", "xăng": "fa-gas-pump", "bus": "fa-bus",
    "lương": "fa-money-bill-wave", "thưởng": "fa-gift",
    "chơi": "fa-gamepad", "giải trí": "fa-film", "sắm": "fa-shopping-cart",
    "áo": "fa-tshirt", "học": "fa-graduation-cap", "thuốc": "fa-pills",
    "bệnh": "fa-briefcase-medical", "lại": "fa-car"
};

function getIcon(text) {
    text = (text || "").toLowerCase();
    for (let key in iconMap) {
        if (text.includes(key)) return iconMap[key];
    }
    return "fa-tag"; // Icon mặc định
}

async function loadDataAndStats() {
    try {
        const res = await fetch(`${API_URL}/expenses/?skip=0&limit=100`, { 
            headers: { "Authorization": `Bearer ${getToken()}` } 
        });

        if (res.status === 401) { logoutSession(); return; }
        
        allExpenses = await res.json();
        
        // Render List (Mới nhất lên đầu)
        renderTransactionList([...allExpenses].reverse().slice(0, 10));
        // Tính toán thống kê
        calculateStats(allExpenses); // Lưu ý: Cần hàm calculateStats (đã có ở code gốc của bạn hoặc dùng logic bên dưới)
        
        // Nếu đang ở tab thống kê thì vẽ lại luôn
        if(document.getElementById("view-stats") && document.getElementById("view-stats").style.display === 'flex') {
             renderPieChart();
             renderHistoryChart(allExpenses);
             renderCategoryBudgets(allExpenses);
        }

    } catch (e) { console.log("Lỗi tải giao dịch:", e); }
}

// Hàm tính toán thống kê cơ bản cho biểu đồ tròn
function calculateStats(data) {
    const stats = {};
    data.forEach(item => {
        const catName = item.category ? item.category.name : "Khác";
        const isIncome = ["Lương", "Thưởng", "Thu nhập"].includes(catName);
        if(!isIncome) {
            stats[catName] = (stats[catName] || 0) + item.amount;
        }
    });
    window.chartData = stats;
}


// ==========================================================
// HÀM VẼ DANH SÁCH (SỬ DỤNG ADDEVENTLISTENER - CHUẨN NHẤT)
// ==========================================================
function renderTransactionList(data) {
    const container = document.getElementById("transaction-list");
    if (!container) return;
    container.innerHTML = "";

    if (data.length === 0) {
        container.innerHTML = "<div style='text-align:center; color:#777; padding:20px;'>Chưa có giao dịch nào</div>";
        return;
    }

    data.forEach(item => {
        // Lấy thông tin
        const catName = item.category ? item.category.name : "Khác";
        const catId = item.category ? item.category.id : "";
        const desc = item.description || "";
        const isIncome = ["Lương", "Thưởng", "Thu nhập"].includes(catName);
        
        // Tạo dòng chứa
        const rowDiv = document.createElement("div");
        rowDiv.className = "transaction-item";
        rowDiv.style.display = "flex";
        rowDiv.style.justifyContent = "space-between";
        rowDiv.style.alignItems = "center";
        rowDiv.style.padding = "10px";
        rowDiv.style.borderBottom = "1px solid #444";
        rowDiv.style.marginTop = "5px";

        // Phần Trái: Text
        const leftDiv = document.createElement("div");
        leftDiv.innerHTML = `
            <div style="font-weight:bold; color:white;">${desc || catName}</div>
            <div style="font-size:12px; color:#aaa;">${catName}</div>
        `;

        // Phần Phải: Tiền + Nút
        const rightDiv = document.createElement("div");
        rightDiv.style.display = "flex";
        rightDiv.style.alignItems = "center";
        rightDiv.style.gap = "8px";

        // 1. Tiền
        const amountDiv = document.createElement("span");
        amountDiv.innerText = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(item.amount);
        amountDiv.style.color = isIncome ? "#00b894" : "#ff7675";
        amountDiv.style.fontWeight = "bold";
        amountDiv.style.marginRight = "5px";

        // 2. Nút SỬA (Tạo bằng code DOM)
        const btnEdit = document.createElement("button");
        btnEdit.innerText = "SỬA";
        // Style cho nút
        btnEdit.style.background = "#f1c40f"; // Vàng
        btnEdit.style.color = "#000";
        btnEdit.style.border = "none";
        btnEdit.style.padding = "5px 10px";
        btnEdit.style.cursor = "pointer";
        btnEdit.style.borderRadius = "4px";
        btnEdit.style.fontWeight = "bold";
        
        // --- QUAN TRỌNG: GẮN SỰ KIỆN CLICK ---
        btnEdit.addEventListener("click", function() {
            window.startEdit(item.id, desc, item.amount, catId);
        });

        // 3. Nút XÓA (Tạo bằng code DOM)
        const btnDelete = document.createElement("button");
        btnDelete.innerText = "XÓA";
        // Style cho nút
        btnDelete.style.background = "#e74c3c"; // Đỏ
        btnDelete.style.color = "#fff";
        btnDelete.style.border = "none";
        btnDelete.style.padding = "5px 10px";
        btnDelete.style.cursor = "pointer";
        btnDelete.style.borderRadius = "4px";
        btnDelete.style.fontWeight = "bold";

        // --- QUAN TRỌNG: GẮN SỰ KIỆN CLICK ---
        btnDelete.addEventListener("click", function() {
            window.deleteTransaction(item.id);
        });

        // Ghép lại
        rightDiv.appendChild(amountDiv);
        rightDiv.appendChild(btnEdit);
        rightDiv.appendChild(btnDelete);

        rowDiv.appendChild(leftDiv);
        rowDiv.appendChild(rightDiv);

        container.appendChild(rowDiv);
    });
}

// --- 4. XỬ LÝ BIỂU ĐỒ & HẠN MỨC (STATS VIEW) ---
const viewHome = document.getElementById("view-home");
const viewStats = document.getElementById("view-stats");
const tabHome = document.getElementById("tab-home");
const tabStats = document.getElementById("tab-stats");
let pieChart = null;
let historyChart = null;

if(tabHome && tabStats && viewHome && viewStats) {
    tabHome.onclick = () => { 
        viewHome.style.display="block"; viewStats.style.display="none"; 
        tabHome.classList.add("active"); tabStats.classList.remove("active"); 
    };
    
    tabStats.onclick = () => {
        viewHome.style.display="none"; viewStats.style.display="flex"; 
        tabStats.classList.add("active"); tabHome.classList.remove("active");
        
        renderPieChart();
        if(allExpenses.length > 0) {
            renderHistoryChart(allExpenses);
            renderCategoryBudgets(allExpenses);
        }
    };
}

// 4.1. Biểu đồ tròn
function renderPieChart() {
    const ctx = document.getElementById('myChart');
    if (!ctx || !window.chartData) return;

    if (pieChart) pieChart.destroy();

    const labels = Object.keys(window.chartData);
    const data = Object.values(window.chartData);
    
    if (labels.length === 0) return;

    pieChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ 
                data: data, 
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#03e9f4'], 
                borderWidth: 0 
            }]
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            plugins: { 
                legend: { position: 'right', labels: { color: 'white' } },
            } 
        }
    });
}

// 4.2. Hạn Mức TỔNG
function getUserLimit() {
    const saved = localStorage.getItem("user_monthly_limit");
    return saved ? parseInt(saved) : 5000000;
}

const btnSaveBudget = document.getElementById("btn-save-budget");
const inpBudget = document.getElementById("inp-budget");

if (btnSaveBudget && inpBudget) {
    inpBudget.value = getUserLimit(); 
    btnSaveBudget.onclick = () => {
        const val = parseInt(inpBudget.value);
        if (val > 0) {
            localStorage.setItem("user_monthly_limit", val);
            alert(`✅ Đã cập nhật hạn mức tổng: ${formatVND(val)}`);
            renderHistoryChart(allExpenses); 
        }
    };
}

function renderHistoryChart(transactions) {
    const ctx = document.getElementById('historyChart');
    if (!ctx) return;

    const currentLimit = getUserLimit();
    const monthlyStats = {};
    
    transactions.forEach(item => {
        const catName = item.category ? item.category.name : "Khác";
        const isIncome = ["Lương", "Thưởng", "Thu nhập", "Lãi suất"].includes(catName);

        if (!isIncome) {
            const dateObj = new Date(item.date);
            const monthKey = `${dateObj.getMonth() + 1}/${dateObj.getFullYear()}`; 
            if (!monthlyStats[monthKey]) monthlyStats[monthKey] = 0;
            monthlyStats[monthKey] += item.amount;
        }
    });

    const labels = Object.keys(monthlyStats).reverse(); 
    const dataValues = labels.map(label => monthlyStats[label]);

    const backgroundColors = dataValues.map(amount => 
        amount > currentLimit ? '#FF4d4d' : '#00ff88'
    );

    if (historyChart) historyChart.destroy();

    historyChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Thực chi',
                data: dataValues,
                backgroundColor: backgroundColors,
                borderRadius: 5,
            },
            {
                type: 'line',
                label: 'Hạn mức tổng',
                data: Array(labels.length).fill(currentLimit),
                borderColor: '#FFCE56',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: true, text: `Hạn mức tổng: ${formatVND(currentLimit)}`, color: '#aaa'}
            },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#aaa' }, grid: { color: '#444' } },
                x: { ticks: { color: 'white' } }
            }
        }
    });
}

// 4.3. Ngân sách từng danh mục
function getCategoryLimitMap() {
    const raw = localStorage.getItem("category_limits_map");
    return raw ? JSON.parse(raw) : {};
}
function saveCategoryLimit(categoryName, amount) {
    const map = getCategoryLimitMap();
    map[categoryName] = amount;
    localStorage.setItem("category_limits_map", JSON.stringify(map));
}

function renderCategoryBudgets(transactions) {
    const container = document.getElementById("category-budget-list");
    if (!container) return; 
    
    container.innerHTML = "";

    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    const spendingMap = {};

    transactions.forEach(t => {
        const tDate = new Date(t.date);
        const catName = t.category ? t.category.name : "Khác";
        const isIncome = ["Lương", "Thưởng", "Thu nhập"].includes(catName);

        if (!isIncome && tDate.getMonth() === currentMonth && tDate.getFullYear() === currentYear) {
            spendingMap[catName] = (spendingMap[catName] || 0) + t.amount;
        }
    });

    const categories = Object.keys(spendingMap);
    const limitsMap = getCategoryLimitMap();
    const defaultLimit = 2000000; 

    if (categories.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#777;">Tháng này chưa có chi tiêu.</p>';
        return;
    }

    categories.forEach(catName => {
        const spent = spendingMap[catName];
        const limit = limitsMap[catName] || defaultLimit;
        
        let percent = (spent / limit) * 100;
        let displayPercent = percent > 100 ? 100 : percent;

        let statusClass = 'safe'; 
        if (percent >= 100) statusClass = 'danger'; 
        else if (percent >= 75) statusClass = 'warning'; 

        const iconClass = getIcon(catName);

        const div = document.createElement('div');
        div.className = 'budget-item';
        div.innerHTML = `
            <div class="budget-info">
                <div class="b-cat-name" style="cursor:pointer;" title="Bấm để sửa hạn mức">
                    <div class="b-cat-icon"><i class="fas ${iconClass}"></i></div>
                    ${catName} <i class="fas fa-edit" style="font-size:10px; margin-left:5px; color:#555;"></i>
                </div>
                <div class="b-amount-text">
                    <span>${new Intl.NumberFormat('vi-VN').format(spent)}</span> / ${new Intl.NumberFormat('vi-VN').format(limit)}
                </div>
            </div>
            <div class="progress-track">
                <div class="progress-fill ${statusClass}" style="width: ${displayPercent}%"></div>
            </div>
            ${percent >= 100 ? `<div style="font-size: 11px; color: #ff3333; margin-top: 3px; text-align: right;"><i class="fas fa-exclamation-circle"></i> Vượt hạn mức!</div>` : ''}
        `;

        div.querySelector('.b-cat-name').onclick = () => {
            const newLimit = prompt(`Đặt hạn mức tháng cho "${catName}" (VNĐ):`, limit);
            if (newLimit && !isNaN(newLimit) && Number(newLimit) > 0) {
                saveCategoryLimit(catName, Number(newLimit));
                renderCategoryBudgets(transactions); 
            }
        };

        container.appendChild(div);
    });
}

// --- 5. MODAL & LOGIC THÊM/SỬA GIAO DỊCH (ĐÃ FIX LỖI) ---
const modal = document.getElementById("modal-overlay");
const btnOpen = document.getElementById("btn-open-modal");
const btnClose = document.getElementById("btn-close-modal");
const menuBtnAdd = document.getElementById("menu-btn-add");

const openModal = () => { if(modal) modal.style.display="flex"; };

// Hàm Reset Form trạng thái
const resetFormState = () => {
    editingTransactionId = null; // Quên ID đang sửa đi
    
    // Reset ô nhập
    document.getElementById("add-expense-form").reset();
    
    // Đóng Modal
    const modal = document.getElementById("modal-overlay");
    if(modal) modal.style.display = "none";

    // Đổi nút bấm về "Thêm mới" (Màu xanh/đen)
    const btnSubmit = document.querySelector("#add-expense-form button[type='submit']");
    if(btnSubmit) {
        btnSubmit.innerText = "+ Thêm mới";
        btnSubmit.style.backgroundColor = ""; 
    }
    
    // Đổi lại tiêu đề Modal
    const modalTitle = document.querySelector("#modal-overlay h2");
    if(modalTitle) modalTitle.innerText = "Thêm Giao Dịch";
}

if(btnOpen) btnOpen.onclick = openModal;
if(menuBtnAdd) menuBtnAdd.onclick = openModal;
if(btnClose) btnClose.onclick = resetFormState;
if(modal) modal.onclick = (e) => { if (e.target === modal) resetFormState(); }


// ==========================================================
// XỬ LÝ FORM: CHÍNH XÁC CHO CẢ "THÊM" VÀ "SỬA"
// ==========================================================
const expenseForm = document.getElementById("add-expense-form");

if (expenseForm) {
    // Dùng .onsubmit để GHI ĐÈ lên tất cả các code cũ, tránh trùng lặp
    expenseForm.onsubmit = async function(event) {
        event.preventDefault(); // Chặn load lại trang

        // 1. Lấy dữ liệu từ ô nhập
        const amount = document.getElementById("inp-amount").value;
        const desc = document.getElementById("inp-desc").value;
        const catId = document.getElementById("inp-category").value;
        const token = localStorage.getItem("access_token");

        // Kiểm tra dữ liệu
        if (!amount || !desc || !catId) {
            alert("Vui lòng nhập đầy đủ thông tin!");
            return;
        }

        // Body chuẩn gửi lên Server
        const bodyData = {
            amount: parseInt(amount),
            description: desc,
            category_id: parseInt(catId),
            date: new Date().toISOString().split('T')[0]
        };
console.log("📦 Dữ liệu gửi đi (Payload):", JSON.stringify(bodyData));
        // 2. Kiểm tra xem đang "SỬA" hay "THÊM MỚI"
        if (editingTransactionId) {
            // === TRƯỜNG HỢP: ĐANG SỬA (UPDATE) ===
            console.log("🔄 Đang thực hiện CẬP NHẬT cho ID:", editingTransactionId);
            
            try {
                const response = await fetch(`${API_URL}/expenses/${editingTransactionId}`, {
                    method: "PUT", // Dùng PUT để cập nhật
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(bodyData)
                });

                if (response.ok) {
                    alert("✅ Cập nhật thành công!");
                    resetFormState(); // Reset form
                    loadDataAndStats(); // Tải lại danh sách
                } else {
                    const text = await response.text();
                    alert("❌ Lỗi Server: " + text);
                }
            } catch (err) {
                console.error(err);
                alert("❌ Lỗi kết nối tới Server (Kiểm tra lại backend)!");
            }

        } else {
            // === TRƯỜNG HỢP: ĐANG THÊM MỚI (ADD) ===
            console.log("➕ Đang thực hiện THÊM MỚI");
            
            try {
                const response = await fetch(`${API_URL}/expenses/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(bodyData)
                });

                if (response.ok) {
                    alert("✅ Thêm mới thành công!");
                    resetFormState();
                    loadDataAndStats();
                } else {
                    alert("❌ Thêm thất bại!");
                }
            } catch (err) {
                alert("❌ Lỗi kết nối!");
            }
        }
    };
}


// ==========================================================
// CÁC HÀM GỌI TỪ NÚT BẤM (Global Scope)
// ==========================================================

// 1. Hàm Xử lý khi bấm nút SỬA
window.startEdit = function(id, desc, amount, catId) {
    console.log("✏️ Đang sửa ID:", id); 
    
    editingTransactionId = id; 

    // Điền dữ liệu cũ vào ô nhập
    const inpAmount = document.getElementById("inp-amount");
    const inpDesc = document.getElementById("inp-desc");
    const inpCat = document.getElementById("inp-category");

    if(inpAmount) inpAmount.value = amount;
    if(inpDesc) inpDesc.value = desc;
    if(inpCat) inpCat.value = catId;

    // Mở Modal
    const modal = document.getElementById("modal-overlay");
    if(modal) modal.style.display = "flex";

    // Đổi nút "Thêm" thành "Lưu"
    const btnSubmit = document.querySelector("#add-expense-form button[type='submit']");
    if(btnSubmit) {
        btnSubmit.innerText = "💾 CẬP NHẬT";
        btnSubmit.style.backgroundColor = "#e67e22"; 
    }
    
    // Đổi tiêu đề Modal
    const modalTitle = document.querySelector("#modal-overlay h2");
    if(modalTitle) modalTitle.innerText = "Sửa Giao Dịch";
};

// 2. Hàm Xử lý khi bấm nút XÓA
window.deleteTransaction = async function(id) {
    console.log("🗑️ Đang xóa ID:", id); 

    if(!confirm("⚠️ Bạn có chắc chắn muốn XÓA khoản này không?")) return;

    try {
        const token = localStorage.getItem("access_token");
        const res = await fetch(`${API_URL}/expenses/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if(res.ok) {
            alert("✅ Đã xóa thành công!");
            loadDataAndStats();
        } else {
            alert("❌ Lỗi Server: Không xóa được!");
        }
    } catch(e) {
        console.error(e);
        alert("❌ Lỗi kết nối!");
    }
};
// ==========================================================
// HÀM CÒN THIẾU: CẬP NHẬT TỔNG THU - CHI - SỐ DƯ
// ==========================================================
function updateDashboardTotals(data) {
    console.log("--- Đang tính toán tổng số tiền... ---");
    
    let totalIncome = 0;
    let totalExpense = 0;

    data.forEach(item => {
        const amount = item.amount || 0;
        const catName = item.category ? item.category.name : "Khác";
        
        // Danh sách các từ khóa được coi là Thu Nhập
        // (Khớp với logic bạn đang dùng ở các hàm khác)
        const incomeKeywords = ["Lương", "Thưởng", "Thu nhập", "Lãi suất"];
        const isIncome = incomeKeywords.some(keyword => catName.includes(keyword));

        if (isIncome) {
            totalIncome += amount;
        } else {
            totalExpense += amount;
        }
    });

    // Tính số dư
    const balance = totalIncome - totalExpense;

    // Cập nhật lên giao diện (DOM)
    // Lưu ý: ID ở đây phải khớp với file HTML bạn đã sửa ở bước trước
    const elIn = document.getElementById("total-income-display");
    const elEx = document.getElementById("total-expense-display");
    const elBal = document.getElementById("total-balance-display");

    if (elIn) elIn.innerText = formatVND(totalIncome);
    if (elEx) elEx.innerText = formatVND(totalExpense);
    
    if (elBal) {
        elBal.innerText = formatVND(balance);
        // Nếu dương màu trắng, âm màu vàng để cảnh báo
        elBal.style.color = balance >= 0 ? "#ffffff" : "#f1c40f"; 
    }

    console.log(`=> Đã cập nhật: Thu ${totalIncome} - Chi ${totalExpense} = Dư ${balance}`);
}
async function loadDataAndStats() {
    try {
        const res = await fetch(`${API_URL}/expenses/?skip=0&limit=100`, { 
            headers: { "Authorization": `Bearer ${getToken()}` } 
        });

        if (res.status === 401) { logoutSession(); return; }
        
        allExpenses = await res.json();
        
        // 1. Render List (Mới nhất lên đầu)
        renderTransactionList([...allExpenses].reverse().slice(0, 10));

        // 2. Tính toán thống kê biểu đồ tròn (Đã có)
        calculateStats(allExpenses); 
        
        // ===> 3. THÊM DÒNG NÀY ĐỂ HIỆN SỐ TIỀN LÊN 3 Ô <===
        updateDashboardTotals(allExpenses); 

        // 4. Nếu đang ở tab thống kê thì vẽ lại biểu đồ
        if(document.getElementById("view-stats") && document.getElementById("view-stats").style.display === 'flex') {
             renderPieChart();
             renderHistoryChart(allExpenses);
             renderCategoryBudgets(allExpenses);
        }

    } catch (e) { console.log("Lỗi tải giao dịch:", e); }
}