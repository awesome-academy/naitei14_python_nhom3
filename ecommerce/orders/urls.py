from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCheckoutView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='detail'),
    path('checkout/', OrderCheckoutView.as_view(), name='checkout'),
]
