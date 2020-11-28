# from api.models import Products
from api.models import Products, Product_To_Node, Not_Spotted_On
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from api.serializers import UserSerializer, GroupSerializer,\
    ProductsSerializer, Product_To_NodeSerializer, NotSpottedOnSerializer
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


class Product_To_Node_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows mappings from products to OSM nodes
    to be viewed or edited.
    """
    queryset = Product_To_Node.objects.all()
    serializer_class = Product_To_NodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class Not_Spotted_On_View_Set(viewsets.ModelViewSet):
    queryset = Not_Spotted_On.objects.all()
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


@api_view(["GET"])
def get_products(request):
    """
    Result: A JSON consisting of
    - a JSON of all products in our catalog
    - a list of categories
    """
    queryset = Products.objects.all()
    cheeses = queryset.filter(categories__contains='Cheeses')
    wines = queryset.filter(categories__contains='Wines')
    products = cheeses | wines
    products_serialized = ProductsSerializer(products, many=True).data
    category_results = []
    for category in ["Cheeses", "Wines"]:
        filtered = products.filter(categories__contains=category)
        results = [product.id for product in filtered.all()]
        category_results.append({'name': category, 'products': results})

    return JsonResponse({
        "products": products_serialized, "categories": category_results
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
    try:
        code = Products.objects.get(id=product_id).code
    except Products.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    entries = Product_To_Node.objects.all().\
        filter(code=code).\
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
    entries = Product_To_Node.objects.all().\
        filter(node__in=node_ids).\
        distinct()
    codes = list(entry.code for entry in entries)
    products = Products.objects.filter(code__in=codes)
    product_ids = [product.id for product in products]
    return JsonResponse({
        'products': product_ids
    })


@api_view(["POST"])
def post_single_product(request):
    """
    expects a json body with "barcode" as single field
    """
    barcode = json.loads(request.body.decode("utf-8")).get('barcode', '')
    request = requests.get('https://world.openfoodfacts.org/api/v0/product/' + str(barcode) + '.json')
    if request.json()['status_verbose'] == 'product not found':
        return HttpResponse('Product does not exist in Open Food Facts', status=404)

    product = request.json()['product']

    # for test purposes
    #Products.objects.filter(code=barcode).delete()

    if not Products.objects.filter(code=barcode).exists():

        list_of_fields = [field.get_attname_column()[1] for field in Products._meta.fields]
        #list_of_fields.remove('id')

        # remove all fields which are not part of our Products model
        expected_fields = {key: product[key] for key in list_of_fields if key in product.keys()}
        expected_fields['url'] = 'https://world.openfoodfacts.org/product/' + str(barcode)

        Products.objects.create(**expected_fields)

        #print(Products.objects.filter(code=barcode).all().values())
        return HttpResponse(status=201)
    else:
        return HttpResponse('Product already in database', status=409)

