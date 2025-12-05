from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("review/order-item/<int:order_item_id>/", views.review_order_item,
         name="review_order_item"),
    path("delete/<int:pk>/", views.delete_comment, name="delete"),
]