from rest_framework import serializers
from .models import *


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImagesSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField(method_name="get_reviews", read_only=True)

    class Meta:
        model = Product
        model_fields = [f.name for f in Product._meta.fields]
        extra_fields = ["images", "reviews"]
        fields = model_fields + extra_fields
        extra_kwargs = {
            "name": {"required": True, "allow_blank": False},
            "description": {"required": True, "allow_blank": False},
            "brand": {"required": True, "allow_blank": False},
            "category": {"required": True, "allow_blank": False}
        }

    def get_reviews(self, object):
        reviews = object.reviews.all()
        serializer = ReviewsSerializer(reviews, many=True)
        return serializer.data