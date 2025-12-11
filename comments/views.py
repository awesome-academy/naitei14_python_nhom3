from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from myapp.models import Product, OrderItem
from .models import Comment


@login_required
def review_order_item(request, order_item_id):
    """
    Đánh giá / chỉnh sửa đánh giá cho 1 sản phẩm trong đơn hàng.
    Chỉ cho phép nếu:
      - order thuộc về user
      - order.status = 'completed'
      - updated_at không quá 7 ngày
    Mỗi user chỉ có 1 comment / product (update nếu đã tồn tại).
    """
    order_item = get_object_or_404(
        OrderItem.objects.select_related("order", "product"),
        pk=order_item_id,
        order__user=request.user,
    )
    order = order_item.order
    product = order_item.product

    # Kiểm tra quyền và thời gian
    if not order_item.can_review:
        messages.error(
            request,
            "Bạn chỉ có thể đánh giá trong vòng 7 ngày sau khi đơn hàng được giao thành công."
        )
        return redirect("orders:detail", pk=order.pk)

    if request.method == "POST":
        rating = request.POST.get("rating")
        content = request.POST.get("content", "").strip()

        # validate rating
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = None

        if not rating or rating < 1 or rating > 5:
            messages.error(request, "Vui lòng chọn số sao từ 1 đến 5.")
            return redirect("orders:detail", pk=order.pk)

        if not content:
            messages.error(request, "Nội dung đánh giá không được để trống.")
            return redirect("orders:detail", pk=order.pk)

        # 1 user – 1 comment / product: nếu có rồi thì cập nhật
        comment, created = Comment.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={"rating": rating, "content": content},
        )
        if not created:
            comment.rating = rating
            comment.content = content
            comment.save()

        messages.success(request, "Đã lưu đánh giá của bạn.")
        return redirect("orders:detail", pk=order.pk)

    # nếu không phải POST -> quay lại
    return redirect("orders:detail", pk=order.pk)


@login_required
def delete_comment(request, pk):
    """
    User xóa bình luận của chính mình.
    Sau khi xóa, quay lại 1 đơn hàng gần nhất có sản phẩm đó (nếu có).
    """
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    product = comment.product

    # tìm 1 order_item gần nhất của user với product này
    order_item = (
        OrderItem.objects
        .filter(order__user=request.user, product=product)
        .select_related("order")
        .order_by("-order__order_date")
        .first()
    )

    if request.method != "POST":
        if order_item:
            return redirect("orders:detail", pk=order_item.order.pk)
        # fallback
        return redirect("products:detail", pk=product.pk)

    comment.delete()
    messages.success(request, "Đã xóa bình luận.")

    if order_item:
        return redirect("orders:detail", pk=order_item.order.pk)
    # fallback
    return redirect("products:detail", pk=product.pk)
