from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name="register"),
    path('user/', views.current_user, name="current_user"),
    path('user/update/', views.update_user, name="update_user"),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('reset_password/<str:token>', views.reset_password, name="reset_password"),
]
