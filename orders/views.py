import os

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .filters import OrdersFilter
from products.models import Product
from .models import Orders, OrderItems
from .serializers import OrdersSerializer
from utils.helpers import get_current_host

import stripe


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


stripe.api_key = os.environ.get("STRIPE_PRIVATE_KEY")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    YOUR_DOMAIN = get_current_host(request)
    user = request.user
    data = request.data

    order_items = data["order_items"]

    shipping_details = {
        "address": data["address"],
        "city": data["city"],
        "state": data["state"],
        "zipcode": data["zipcode"],
        "country": data["country"],
        "phone_number": data["phone_number"],
        "user": user.id,
    }

    checkout_order_items = []

    for item in order_items:
        checkout_order_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item["name"],
                    "images": [item["image"]],
                    "metadata": { "product_id": item["product"] }
                },
                "unit_amount": int(item["price"] * 100),
            },
            "quantity": item["quantity"]
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        metadata = shipping_details,
        line_items = checkout_order_items,
        customer_email = user.email,
        mode = "payment",
        success_url = YOUR_DOMAIN,
        cancel_url = YOUR_DOMAIN
    )

    return Response({
        "session": session
    })


@api_view(["POST"])
def stripe_webhook(request):
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return Response(
            {"error": "Invalid Payload"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.SignatureVerificationError as e:
        return Response(
            {"error": "Invalid Signature"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        line_items = stripe.checkout.Session.list_line_items(session["id"])
        price = int(session["amount_total"] / 100)

        order = Orders.objects.create(
            user = User(session.metadata.user),
            address = session.metadata.address,
            city = session.metadata.city,
            state = session.metadata.state,
            zipcode = session.metadata.zipcode,
            country = session.metadata.country,
            phone_number = session.metadata.phone_number,
            total_amount = price,
            payment_mode = "CARD",
            payment_status = "PAID"
        )

        for item in line_items["data"]:
            print("item", item)

            line_product = stripe.Product.retrieve(item.price.product)
            product_id = line_product.metadata.product_id
            product = Product.objects.get(id=product_id)

            item = OrderItems.objects.create(
                product = product,
                order = order,
                name = product.name,
                quantity = item.quantity,
                price = item.price.unit_amount,
                image = line_product.images[0]
            )

            product.stock -= item.quantity
            product.save()

        return Response({"Payment Successful"}, status=status.HTTP_200_OK)