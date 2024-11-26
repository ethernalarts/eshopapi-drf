from django_filters import rest_framework as filters
from .models import Orders


class OrdersFilter(filters.FilterSet):
    class Meta:
        model = Orders
        fields = ["id", "order_status", "payment_status", "payment_mode"]