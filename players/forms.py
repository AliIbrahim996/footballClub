from django import forms


class PlayerValidator(forms.Form):
    name = forms.CharField
    first_name = forms.CharField
    address = forms.CharField
    post_code = forms.CharField
    city = forms.CharField
    society = forms.CharField
    date_of_birth = forms.DateField
    phone_number = forms.IntegerField
    email = forms.EmailField
    image = forms.ImageField
