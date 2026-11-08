from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Category, Player, PlayerSkills, Plans, Skills

letters_only = RegexValidator(r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$", _("Letters only."))
digits_only = RegexValidator(r"^\+?[0-9 ]*$", _("Digits only."))


class MediaImageField(serializers.ImageField):
    """Emit relative /media/... URLs so any frontend origin (or proxy) can resolve them."""

    def to_representation(self, value):
        return value.url if value else None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Skills
        fields = ["id", "skill_name", "comment", "category", "category_name"]


class PlayerSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.skill_name", read_only=True)
    category = serializers.IntegerField(source="skill.category_id", read_only=True)
    category_name = serializers.CharField(source="skill.category.name", read_only=True)

    class Meta:
        model = PlayerSkills
        fields = ["id", "skill", "skill_name", "category", "category_name", "value", "modified_by", "modified_at"]
        read_only_fields = ["modified_by", "modified_at"]


class PlayerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[letters_only])
    first_name = serializers.CharField(validators=[letters_only])
    phone_number = serializers.CharField(validators=[digits_only], required=False, allow_blank=True)
    image = MediaImageField(required=False, allow_null=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id", "name", "first_name", "address", "post_code", "city", "society",
            "date_of_birth", "phone_number", "email_address", "image", "average_rating",
        ]

    def get_average_rating(self, obj) -> float | None:
        values = [ps.value for ps in obj.playerskills_set.all()]
        return round(sum(values) / len(values), 2) if values else None


class PlayerDetailSerializer(PlayerSerializer):
    evaluations = PlayerSkillSerializer(source="playerskills_set", many=True, read_only=True)

    class Meta(PlayerSerializer.Meta):
        fields = PlayerSerializer.Meta.fields + ["evaluations"]


class EvaluationItemSerializer(serializers.Serializer):
    skill = serializers.PrimaryKeyRelatedField(queryset=Skills.objects.all())
    value = serializers.IntegerField(min_value=1, max_value=5)


class EvaluationSerializer(serializers.Serializer):
    """Bulk upsert of ratings for one player."""
    ratings = EvaluationItemSerializer(many=True)

    def save(self, player: Player, username: str):
        now = timezone.now()
        for item in self.validated_data["ratings"]:
            PlayerSkills.objects.update_or_create(
                player=player,
                skill=item["skill"],
                defaults={"value": item["value"], "modified_by": username, "modified_at": now},
            )
        return player


class PlanSerializer(serializers.ModelSerializer):
    image = MediaImageField()

    class Meta:
        model = Plans
        fields = ["id", "title", "image", "board", "created_at", "created_by", "comment"]
        read_only_fields = ["created_at", "created_by"]

