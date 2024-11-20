from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name="register"),
    path('user/', views.current_user, name="current_user"),
    path('user/update/', views.update_user, name="update_user"),
]
