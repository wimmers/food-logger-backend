# from api.models import Products
from django.core.exceptions import ValidationError
from api.models import Products, ProductToNode, SpottedOn, NotSpottedOn
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from api.serializers import UserSerializer, GroupSerializer,\
    ProductsSerializer, ProductToNodeSerializer, SpottedOnSerializer, NotSpottedOnSerializer
import requests
import json


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductToNodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows mappings from products to OSM nodes
    to be viewed or edited.
    """
    queryset = ProductToNode.objects.all()
    serializer_class = ProductToNodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SpottedOnViewSet(viewsets.ModelViewSet):
    queryset = SpottedOn.objects.all()
    serializer_class = SpottedOnSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotSpottedOnViewSet(viewsets.ModelViewSet):
    queryset = NotSpottedOn.objects.all()
    serializer_class = NotSpottedOnSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["GET"])
def get_categories(request):
    """
    API endpoint that returns the existing categories
    in the Open Food Facts db.
    Only for internal use.
    """
    queryset = Products.objects.all()
    categories = set()
    for product in queryset:
        new_categories = product.categories.split(',')
        new_categories = (x.strip() for x in new_categories)
        categories.update(new_categories)
    return JsonResponse({"categories": list(categories)})


def sort_by_field_string(entries, accessor):
    categories_to_entries = {}
    for entry in entries:
        categories = [s.strip() for s in accessor(entry).split(',')]
        for category in categories:
            categories_to_entries.setdefault(category, set()).add(entry.id)
    return [{'name': category, 'products': list(results)}
            for category, results in categories_to_entries.items()]


@api_view(["GET"])
def get_products(request):
    """
    Result: A JSON consisting of
    - a JSON of all products in our catalog
    - a list of categories
    """
    products = Products.objects.all()
    products_serialized = ProductsSerializer(products, many=True).data
    category_results = sort_by_field_string(products, lambda x: x.categories)
    brand_results = sort_by_field_string(products, lambda x: x.brands)

    return JsonResponse({
        "products": products_serialized,
        "categories": category_results,
        "brands": brand_results
    })


@api_view(["GET"])
def filter_shops(request):
    """
    Arguments:
    - product: product id
    - shops: a list of shop ids

    Result: a sublist of `shops` that have `product`
    """
    product_id = request.GET.get('product')
    node_ids = request.GET.get('nodes').split(',')
    entries = ProductToNode.objects.all().\
        filter(product=product_id).\
        filter(node__in=node_ids)
    result = [entry.node for entry in entries]
    return JsonResponse({
        'nodes': result
    })


@api_view(["GET"])
def filter_products(request):
    """
    Arguments:
    - products: a list of product ids
    - shops: a list of shop ids

    Result: a sublist of `products` that are available at at least one of `shops`
    """
    node_ids = request.GET.get('nodes').split(',')
    entries = ProductToNode.objects.all().\
        filter(node__in=node_ids).\
        distinct()
    return JsonResponse({
        'products': [entry.product.id for entry in entries]
    })


@api_view(["POST"])
def post_single_product(request):
    """
    expects a json body with "barcode" as single field
    """
    barcode = json.loads(request.body.decode("utf-8")).get('barcode', '')
    request = requests.get(
        'https://world.openfoodfacts.org/api/v0/product/' + str(barcode) + '.json')
    if request.json()['status_verbose'] == 'product not found':
        return HttpResponse('Product does not exist in Open Food Facts', status=404)

    product = request.json()['product']

    # for test purposes
    # Products.objects.filter(code=barcode).delete()

    if not Products.objects.filter(code=barcode).exists():

        list_of_fields = [field.get_attname_column()[1]
                          for field in Products._meta.fields]
        # list_of_fields.remove('id')

        # remove all fields which are not part of our Products model
        expected_fields = {key: product[key]
                           for key in list_of_fields if key in product.keys()}
        expected_fields['url'] = 'https://world.openfoodfacts.org/product/' + \
            str(barcode)

        Products.objects.create(**expected_fields)

        # print(Products.objects.filter(code=barcode).all().values())
        return HttpResponse(status=201)
    else:
        return HttpResponse('Product already in database', status=409)


@api_view(["POST"])
def add_product_to_shop(request):
    """
    Marks a new product as available at a shop.
    Arguments (given as JSON):
    - product: id of the product
    - node: OSM id of the shop
    """
    data = request.data
    serializer = ProductToNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return HttpResponse()


def validate_spotted(attrs):
    if 'product' not in attrs:
        raise ValidationError("Missing field: 'product'")
    if 'node' not in attrs:
        raise ValidationError("Missing field: 'node'")
    if not isinstance(attrs['product'], int):
        raise ValidationError("Value error: 'product' must be 'int'")
    if not isinstance(attrs['node'], int):
        raise ValidationError("Value error: 'node' must be 'int'")


@api_view(["POST"])
def confirm_product_at_shop(request):
    """
    Confirms a new product as available at a shop.
    Arguments (given as JSON):
    - product: id of the product
    - node: OSM id of the shop
    """
    data = request.data
    validate_spotted(data)
    link = ProductToNode.objects.get(
        product=data['product'], node=data['node'])
    SpottedOn(product_node_link=link).save()

    return HttpResponse()


@api_view(["POST"])
def unconfirm_product_at_shop(request):
    """
    Unconfirms a new product as available at a shop.
    Arguments (given as JSON):
    - product: id of the product
    - node: OSM id of the shop
    """
    data = request.data
    validate_spotted(data)
    link = ProductToNode.objects.get(
        product=data['product'], node=data['node'])
    NotSpottedOn(product_node_link=link).save()

    return HttpResponse()


@api_view(["DELETE"])
def remove_product_to_node_link(request):
    data = request.data
    validate_spotted(data)

    try:
        link = ProductToNode.objects.get(
            product=data['product'], node=data['node'])
        link.delete()

    except ProductToNode.DoesNotExist:
        return HttpResponseNotFound("Product to node entry not found.")

    return HttpResponse("Deleted link.")
