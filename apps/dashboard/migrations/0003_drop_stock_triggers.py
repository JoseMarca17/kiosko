from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_triggers_views_seeds'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TRIGGER IF EXISTS trg_descontar_stock;",
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="DROP TRIGGER IF EXISTS trg_restaurar_stock_cancelacion;",
            reverse_sql=""
        ),
    ]
