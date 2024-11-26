from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .filters import OrdersFilter
from products.models import Product
from .models import Orders, OrderItems
from .serializers import OrdersSerializer


# Create your views here.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data
    order_items = data["order_items"]

    if len(order_items) == 0:
        return Response(
            "Shopping Cart is empty",
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        # create order
        order = Orders.objects.create(
            address = data["address"],
            city = data["city"],
            state = data["state"],
            zipcode = data["zipcode"],
            country = data["country"],
            phone_number = data["phone_number"],
            email = user.email,
            total_amount = sum(
                item["price"] * item["quantity"] for item in order_items
            )

        )

        # create order items
        for i in order_items:
            product = Product.objects.get(id=i["product"])

            item = OrderItems.objects.create(
                product = product,
                order = order,
                name = product.name,
                quantity = i["quantity"],
                price = i["price"]
            )

            product.stock -= item.quantity
            product.save()

        serializer = OrdersSerializer(order, many=False)
        return Response(serializer.data)



# Get all orders
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    filterset = OrdersFilter(request.GET, queryset=Orders.objects.all().order_by("id"))
    count = filterset.qs.count()

    # Pagination
    resultsPerPage = 1
    paginator = PageNumberPagination()
    paginator.page_size = resultsPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = OrdersSerializer(queryset, many=True)
    return Response({
        "count": count,
        "resultsPerPage": resultsPerPage,
        "All orders": serializer.data
    })



# Get all orders
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order(request, pk):
    order = get_object_or_404(Orders, id=pk)
    serializer = OrdersSerializer(order, many=False)
    return Response({
        "Order": serializer.data
    })


# Delete an order
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request, pk):
    order = get_object_or_404(Orders, id=pk)
    order.order_status = request.data["order_status"]
    order.save()
    return Response(
        "Order status has been updated",
        status=status.HTTP_200_OK
    )


# Delete an order
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_order(request, pk):
    order = get_object_or_404(Orders, id=pk)

    order.delete()
    return Response(
        "Order has been deleted",
        status=status.HTTP_200_OK
    )