const API_URL = "http://127.0.0.1:8000";

// 1. Kiểm tra đăng nhập
const token = localStorage.getItem("access_token");
if (!token) {
    window.location.href = "index.html"; 
}

// 2. Hàm đăng xuất
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "index.html";
}

// 3. Quản lý Modal (Cửa sổ thêm mới)
function openModal() {
    document.getElementById("addModal").style.display = "block";
}
function closeModal() {
    document.getElementById("addModal").style.display = "none";
}
// Click ra ngoài thì đóng modal
window.onclick = function(event) {
    if (event.target == document.getElementById("addModal")) {
        closeModal();
    }
}


let transactions = [
    { id: 1, type: 'expense', amount: 50000, category: 'Ăn sáng', date: '2023-10-25' },
    { id: 2, type: 'income', amount: 10000000, category: 'Lương tháng 10', date: '2023-10-20' },
    { id: 3, type: 'expense', amount: 200000, category: 'Đổ xăng', date: '2023-10-24' },
];

// Hàm hiển thị danh sách giao dịch
function renderTransactions() {
    const list = document.getElementById("transaction-list");
    list.innerHTML = ""; 
    
    let totalInc = 0;
    let totalExp = 0;

    transactions.forEach((t, index) => {
        // Tính tổng
        if(t.type === 'income') totalInc += Number(t.amount);
        else totalExp += Number(t.amount);

        // Tạo thẻ HTML
        const item = document.createElement("div");
        item.classList.add("transaction-item");
        
        // Định dạng tiền tệ
        const formattedAmount = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(t.amount);
        const sign = t.type === 'expense' ? '-' : '+';
        const colorClass = t.type; // 'income' hoặc 'expense'

        item.innerHTML = `
            <div class="t-info">
                <span class="t-cat">${t.category}</span>
                <span class="t-date">${t.date}</span>
            </div>
            <div class="t-amount ${colorClass}">${sign}${formattedAmount}</div>
            <button class="btn-del" onclick="deleteTransaction(${t.id})"><i class="fa-solid fa-trash"></i></button>
        `;
        list.appendChild(item);
    });

    // Cập nhật lên thẻ bài
    document.getElementById("total-income").innerText = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(totalInc);
    document.getElementById("total-expense").innerText = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(totalExp);
    document.getElementById("total-balance").innerText = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(totalInc - totalExp);
}

// Hàm thêm giao dịch (Giả lập)
document.getElementById("add-form").addEventListener("submit", function(e) {
    e.preventDefault();
    
    let type = document.getElementById("t-type").value;
    let amount = document.getElementById("t-amount").value;
    let category = document.getElementById("t-category").value;

    // Thêm vào mảng 
    transactions.push({
        id: Date.now(),
        type: type,
        amount: amount,
        category: category,
        date: new Date().toISOString().split('T')[0]
    });

    renderTransactions(); 
    closeModal(); 
    e.target.reset(); 
});

// Hàm xóa giao dịch 
function deleteTransaction(id) {
    if(confirm("Bạn có chắc muốn xóa không?")) {
        // Lọc bỏ phần tử có id tương ứng
        transactions = transactions.filter(t => t.id !== id);
        renderTransactions();
    }
}


renderTransactions();