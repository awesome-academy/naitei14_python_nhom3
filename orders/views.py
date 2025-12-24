from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from cart.cart import Cart
from myapp.enums import (
    ORDER_STATUS_CHOICES,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_CANCELLED,
)
from myapp.models import CartItem, Order, OrderItem
from comments.models import Comment
from django.utils.translation import gettext as _

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user).order_by('-order_date').prefetch_related('items__product')
        status = self.request.GET.get('status')

        valid_status = dict(ORDER_STATUS_CHOICES).keys()
        if status in valid_status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = ORDER_STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        return ctx


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.object

        order_items = list(order.items.all())         

        product_ids = [it.product_id for it in order_items]

        user_comments = Comment.objects.filter(
            user=self.request.user,
            product_id__in=product_ids,
        )

        comment_map = {c.product_id: c for c in user_comments}

        for it in order_items:
            it.user_comment = comment_map.get(it.product_id)

        ctx["items"] = order_items
        return ctx

class OrderCancelView(LoginRequiredMixin, View):
    """
    Cho phép user hủy đơn nếu đang ở trạng thái 'pending'
    và đổi sang 'cancelled' (khớp với ORDER_STATUS_CHOICES).
    """

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        # chỉ cho hủy khi status = 'pending'
        if order.status != ORDER_STATUS_PENDING:
            messages.error(request, _('Đơn hàng này không thể hủy nữa.'))
            return redirect('orders:detail', pk=order.pk)

        order.status = ORDER_STATUS_CANCELLED
        order.rejection_reason = _('Người dùng tự hủy đơn.')
        order.save(update_fields=['status', 'rejection_reason', 'updated_at'])

        messages.success(request, _('Đơn hàng đã được hủy thành công.'))
        return redirect('orders:detail', pk=order.pk)

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('cart:detail')
        
        selected_ids_str = request.GET.get('ids', '')
        
        if not selected_ids_str:
            messages.warning(request, _("Vui lòng chọn sản phẩm để thanh toán."))
            return redirect('cart:detail')

        ids_list = selected_ids_str.split(',')

        cart_items = []
        total_price = 0
        
        for item in cart:
            if str(item['product'].id) in ids_list:
                cart_items.append(item)
                total_price += item['total_price']
        
        context = {
            'cart_items': cart_items,    
            'total_price': total_price, 
            'selected_ids': selected_ids_str
        }
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = Cart(request)
        
        selected_ids_str = request.POST.get('selected_ids', '')
        ids_list = selected_ids_str.split(',')
        
        items_to_buy = []
        final_total = 0
        
        for item in cart:
            if str(item['product'].id) in ids_list:
                items_to_buy.append(item)
                final_total += item['total_price']

        if not items_to_buy:
            messages.warning(request, _("Danh sách sản phẩm không hợp lệ."))
            return redirect('cart:detail')

        shipping_address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            payment_method='COD',
            total_amount=final_total, 
            status='pending'
        )

        for item in items_to_buy:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price_at_purchase=item['price'],
                quantity=item['quantity']
            )
            cart.remove(item['product']) 
        
        messages.success(
            request,
            _("Đặt hàng thành công! Mã đơn: #%(order_id)s")
            % {"order_id": order.id},
        )
        return redirect('orders:detail', pk=order.id)