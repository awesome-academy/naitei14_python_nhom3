function calcSelectedTotal() {
    let total = 0;

    document.querySelectorAll('tr.cart-row').forEach(function (row) {
        const checkbox = row.querySelector('.cart-item-checkbox');
        if (checkbox && checkbox.checked) {
            const raw = row.dataset.subtotal;  
            const value = parseFloat(raw);
            if (!isNaN(value)) {
                total += value;
            }
        }
    });

    const span = document.getElementById('cart-total-amount');
    if (span) {
        try {
            span.textContent = total.toLocaleString('vi-VN', { minimumFractionDigits: 0 }) + ' VNĐ';
        } catch (e) {
            span.textContent = total.toFixed(0) + ' VNĐ';
        }
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