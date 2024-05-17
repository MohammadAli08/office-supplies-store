# Generated by Django 5.0.6 on 2024-05-16 13:00

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_productcomment_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='products.productcomment', verbose_name='والد'),
        ),
        migrations.AlterField(
            model_name='productcomment',
            name='rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='نمره'),
        ),
    ]