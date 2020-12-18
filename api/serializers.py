from django.contrib.auth.models import User, Group
from api.models import Products, ProductToNode, SpottedOn, NotSpottedOn
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
                  'nutriscore_grade',
                  "image_url",
                  "image_small_url",
                  "image_front_url",
                  "image_front_small_url",
                  "image_ingredients_url",
                  "image_ingredients_small_url",
                  "image_nutrition_url",
                  "image_nutrition_small_url",
                  ]


class SpottedOnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpottedOn
        fields = ['day', 'product_node_link']


class NotSpottedOnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NotSpottedOn
        fields = ['day', 'product_node_link']


class ProductToNodeSerializer(serializers.HyperlinkedModelSerializer):
    spotted_on = serializers.SlugRelatedField(many=True, read_only=True, slug_field='day')
    not_spotted_on = serializers.SlugRelatedField(many=True, read_only=True, slug_field='day')

    class Meta:
        model = ProductToNode
        fields = ['code', 'node', 'created', 'spotted_on', 'not_spotted_on']
