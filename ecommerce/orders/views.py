from django.views import View
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from cart.cart import Cart
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

class OrderCheckoutView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('cart:detail')

        total = cart.get_total_price()
        order = Order.objects.create(user=request.user, total_price=total)

        for item in cart:
            product = item['product']
            qty = item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=item['price']
            )
            if product.stock >= qty:
                product.stock -= qty
                product.save()
            else:
                raise ValueError(f"Not enough stock for {product.name}")

        cart.clear()
        return redirect('orders:detail', order_id=order.id)
