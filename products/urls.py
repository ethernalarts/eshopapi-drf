from django.urls import path
from . import views


urlpatterns = [
    path('products/all/', views.get_products, name="all_products"),
    path('products/new/', views.create_new_product, name="create_new_product"),
    path('products/upload_image/', views.upload_product_image, name="upload_product_image"),
    path('products/<str:pk>/', views.get_product, name="get_product_details"),
    path('products/<str:pk>/update/', views.update_product, name="update_product"),
    path('products/<str:pk>/delete/', views.delete_product, name="delete_product"),

    path('<str:pk>/reviews/', views.create_update_review, name="create_update_product"),
    path('<str:pk>/reviews/delete/', views.delete_review, name="delete_review"),
]
