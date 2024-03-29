# Generated by Django 3.2.6 on 2021-11-07 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20211107_1435'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='products.product'),
        ),
    ]
