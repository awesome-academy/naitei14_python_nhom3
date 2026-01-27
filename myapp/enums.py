"""Common enums/constants for the myapp app."""

from django.utils.translation import gettext_lazy as _

ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_CONFIRMED = 'confirmed'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_COMPLETED = 'completed'
ORDER_STATUS_CANCELLED = 'cancelled'
ORDER_STATUS_REJECTED = 'rejected'

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, _('Chờ xác nhận')),
    (ORDER_STATUS_CONFIRMED, _('Đã xác nhận')),
    (ORDER_STATUS_SHIPPED, _('Đang giao')),
    (ORDER_STATUS_COMPLETED, _('Đã giao thành công')),
    (ORDER_STATUS_CANCELLED, _('Hủy bởi người dùng')),
    (ORDER_STATUS_REJECTED, _('Bị từ chối bởi admin')),
]
