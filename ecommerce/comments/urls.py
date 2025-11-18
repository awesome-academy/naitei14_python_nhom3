from django.urls import path
from .views import CommentCreateView, CommentDeleteView

app_name = 'comments'

urlpatterns = [
    path('add/<int:product_id>/<slug:slug>/', CommentCreateView.as_view(), name='add'),
    path('delete/<int:pk>/', CommentDeleteView.as_view(), name='delete'),
]
