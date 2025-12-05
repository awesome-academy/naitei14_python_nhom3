# myapp/enums.py

ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_CONFIRMED = 'confirmed'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_COMPLETED = 'completed'
ORDER_STATUS_CANCELLED = 'cancelled'
ORDER_STATUS_REJECTED = 'rejected'

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, 'Chờ xác nhận'),
    (ORDER_STATUS_CONFIRMED, 'Đã xác nhận'),
    (ORDER_STATUS_SHIPPED, 'Đang giao'),
    (ORDER_STATUS_COMPLETED, 'Đã giao thành công'),
    (ORDER_STATUS_CANCELLED, 'Hủy bởi người dùng'),
    (ORDER_STATUS_REJECTED, 'Bị từ chối bởi admin'),
]
