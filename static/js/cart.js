// static/js/cart.js

function calcSelectedTotal() {
    let total = 0;

    // duyệt từng dòng sản phẩm
    document.querySelectorAll('tr.cart-row').forEach(function (row) {
        const checkbox = row.querySelector('.cart-item-checkbox');
        if (checkbox && checkbox.checked) {
            const raw = row.dataset.subtotal;   // ví dụ "159000.00"
            const value = parseFloat(raw);
            if (!isNaN(value)) {
                total += value;
            }
        }
    });

    const span = document.getElementById('cart-total-amount');
    if (span) {
        span.textContent = total.toLocaleString('vi-VN') + ' VNĐ';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const allCheckbox = document.getElementById('check-all');

    if (allCheckbox) {
        allCheckbox.addEventListener('change', function () {
            document.querySelectorAll('.cart-item-checkbox')
                .forEach(cb => cb.checked = allCheckbox.checked);
            calcSelectedTotal();
        });
    }

    document.querySelectorAll('.cart-item-checkbox').forEach(function (cb) {
        cb.addEventListener('change', calcSelectedTotal);
    });

    // lúc mới vào trang: chưa chọn gì => tổng = 0
    calcSelectedTotal();
});
