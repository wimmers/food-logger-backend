from django.contrib.auth.models import User, Group
from api.models import Products, Product_To_Node
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ProductsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Products
        fields = ['id',
                  'url',
                  'code',
                  'product_name',
                  'generic_name',
                  'brands',
                  'categories',
                  'categories_tags',
                  'stores',
                  'allergens',
                  'nutriscore_score',
                  "image_url",
                  "image_small_url",
                  "image_front_url",
                  "image_front_small_url",
                  "image_ingredients_url",
                  "image_ingredients_small_url",
                  "image_nutrition_url",
                  "image_nutrition_small_url",
                  ]


class Product_To_NodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product_To_Node
        fields = ['code', 'node']