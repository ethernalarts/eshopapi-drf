from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ProductSerializer, ProductImagesSerializer
from .filters import ProductsFilter
from .models import Product, ProductImages, Reviews


# Create your views here.


# Get All Products
@api_view(["GET"])
def get_products(request):
    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))
    count = filterset.qs.count()

    # Pagination
    resPerPage = 3

    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = ProductSerializer(queryset, many=True)
    return Response({
        "count": count,
        "resPerPage": resPerPage,
        "products": serializer.data
    })


# Get Product Details
@api_view(["GET"])
def get_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


# Create new Product
@api_view(["POST"])
@permission_classes(IsAuthenticated)
def create_new_product(request):
    data = request.data
    serializer = ProductSerializer(data=data)

    if not serializer.is_valid():
        return Response(serializer.errors)

    product = Product.objects.create(**data, user=request.user)
    res = ProductSerializer(product, many=False)
    return Response({"product": res.data})


# Update a Product
@api_view(["PUT"])
@permission_classes(IsAuthenticated)
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    if product.user != request.user:
        return Response(
            "You aren't authorized to update this product",
            status=status.HTTP_403_FORBIDDEN
        )

    product.name = request.data['name']
    product.description = request.data['description']
    product.price = request.data['price']
    product.brand = request.data['brand']
    product.category = request.data['category']
    product.ratings = request.data['ratings']
    product.stock = request.data['stock']

    product.save()
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


# Delete a Product
@api_view(["DELETE"])
@permission_classes(IsAuthenticated)
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    if product.user != request.user:
        return Response(
            "You aren't authorized to delete this product",
            status=status.HTTP_403_FORBIDDEN
        )

    args = {"product": pk}
    images = ProductImages.objects.filter(**args)
    for image in images:
        image.delete()

    product.delete()
    return Response({"details": "Product deleted"}, status=status.HTTP_200_OK)


# Upload a Product Image
@api_view(["POST"])
def upload_product_image(request):
    data = request.data
    files = request.FILES.getlist("images")

    images = []
    for f in files:
        image = ProductImages.objects.create(product=Product(data['product']), image=f)
        images.append(image)

    serializer = ProductImagesSerializer(images, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, ])
def create_update_review(request, pk):
    user = request.user
    data = request.data
    product = get_object_or_404(Product, id=pk)
    review = product.reviews.filter(user=user)

    if data['rating'] <= 0 or data['rating'] > 5:
        return Response(
            'Please select a rating between 1-5',
            status=status.HTTP_400_BAD_REQUEST
        )

    elif review.exists():
        new_review = {"rating": data['rating'], "comment": data['comment']}
        review.update(**new_review)
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()
        return Response('Your review has been updated', status=status.HTTP_200_OK)

    else:
        Reviews.objects.create(
            user=user,
            product=product,
            rating=data['rating'],
            comment=data['comment'],
        )

        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()

        return Response('Your review has been posted', status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)
    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

        if rating['avg_ratings'] is None:
            rating['average_ratings'] = 0

        product.ratings = rating['avg_ratings']
        product.save()
        return Response('Review has been deleted', status=status.HTTP_200_OK)

    else:
        return Response('Review not found', status=status.HTTP_404_NOT_FOUND)