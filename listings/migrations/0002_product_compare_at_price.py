from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='compare_at_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Optional original price, shown struck through if higher than price', max_digits=12, null=True),
        ),
    ]