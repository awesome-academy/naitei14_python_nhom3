from django.db import models
from django.conf import settings
from myapp.models import Product  # Product chuẩn bên myapp


class Comment(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5,
        help_text='Đánh giá từ 1 đến 5 sao'
    )
    content = models.TextField('Nội dung bình luận')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        unique_together = ('user', 'product')  # 1 user chỉ được comment 1 lần cho 1 product

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating}⭐)'
