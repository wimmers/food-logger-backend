# Generated by Django 3.1.4 on 2020-12-18 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_new_product_to_node_columns_and_spotted_tables'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Not_Spotted_On',
            new_name='NotSpottedOn',
        ),
        migrations.RenameModel(
            old_name='Product_To_Node',
            new_name='ProductToNode',
        ),
        migrations.RenameModel(
            old_name='Spotted_On',
            new_name='SpottedOn',
        ),
    ]