// Custom JavaScript for Naitei14 Python Nhom3 Project

document.addEventListener('DOMContentLoaded', function() {
    console.log('Naitei14 Python Nhom3 - Ready!');
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
