from django import forms
from .models import Player


class PlayerValidator(forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"
