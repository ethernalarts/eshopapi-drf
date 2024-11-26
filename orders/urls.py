from django.urls import path
from . import views


urlpatterns = [
    path('orders/new/', views.new_order, name="new_order"),
    path('orders/all/', views.get_all_orders, name="get_all_orders"),
    path('orders/<str:pk>/', views.get_order, name="get_order"),
    path('orders/<str:pk>/updatestatus/', views.process_order, name="process_order"),
    path('orders/<str:pk>/delete/', views.delete_order, name="delete_order"),
]