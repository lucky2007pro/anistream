from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='telegram_channel_post_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='telegram_file_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='telegram_message_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]

