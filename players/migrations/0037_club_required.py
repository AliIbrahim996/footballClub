from django.db import migrations, models
import django.db.models.deletion


def club_fk(related_name):
    return models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name=related_name, to="players.club")


class Migration(migrations.Migration):
    dependencies = [("players", "0036_assign_existing_data_to_default_club")]
    operations = [
        migrations.AlterField("category", "club", club_fk("categories")),
        migrations.AlterField("skills", "club", club_fk("skills")),
        migrations.AlterField("player", "club", club_fk("players")),
        migrations.AlterField("plans", "club", club_fk("plans")),
    ]
