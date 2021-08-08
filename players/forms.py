from django import forms
from django.core.validators import RegexValidator

from .models import Player


class PlayerValidator(forms.ModelForm):
    labels = {
        'name': 'Name',
        'first_name': 'Vorname',
        'address': 'Straße/Hausnummer',
        'post_code': 'Postleitzahl',
        'city': 'Stadt',
        'society': 'Verein',
        'date_of_birth': 'Geburtstag',
        'phone_number': 'Telefonnummer',
        'email_address': 'Emailadresse',
        'image': 'Hochladen'
    }
    widgets = {
        'name': forms.TextInput,
        'first_name': forms.TextInput,
        'address': forms.TextInput,
        'post_code': forms.TextInput,
        'city': forms.TextInput,
        'society': forms.TextInput,
        'date_of_birth': forms.DateTimeInput,
        'phone_number': forms.NumberInput,
        'email_address': forms.EmailInput,
        'image': forms.FileInput
    }

    form_validators = {
        'name': [RegexValidator('^[a-zA-Z]*$', message='Bitte geben Sie nur alphabetische Buchstaben ein')],
        'first_name': [RegexValidator('^[a-zA-Z]*$', message='Bitte geben Sie nur alphabetische Buchstaben ein')],
        'phone_number': [RegexValidator('^[0-9]*$', message='Bitte geben Sie nur alphabetische Buchstaben ein')],
    }

    address_error_dict = post_code_error_dict = erro_dict = dict()
    address_error_dict[
        'required'] = "Überprüfen Sie, ob das Feld nicht leer ist oder ob es eine gültige Adresse ist"
    post_code_error_dict[
        'required'] = "Überprüfen Sie, ob das Feld nicht leer ist oder ob es sich um eine gültige Postleitzahl handelt"
    erro_dict['required'] = "Vergewissern Sie sich, dass das Feld nicht leer ist"

    name = forms.CharField(widget=widgets['name'], max_length=255, error_messages=erro_dict, label=labels['name'],
                           validators=form_validators['name'])  # name
    first_name = forms.CharField(widget=widgets['first_name'], max_length=255, error_messages=erro_dict,
                                 label=labels['first_name'],
                                 validators=form_validators['first_name'])  # first name
    address = forms.CharField(widget=widgets['address'], max_length=255, error_messages=address_error_dict,
                              label=labels['address'])  # Street, house number
    post_code = forms.CharField(widget=widgets['post_code'], max_length=255, error_messages=post_code_error_dict,
                                label=labels['post_code'])  # Post code
    city = forms.CharField(widget=widgets['city'], max_length=255, error_messages=erro_dict,
                           label=labels['city'])  # city
    society = forms.CharField(widget=widgets['society'], max_length=255, error_messages=erro_dict,
                              label=labels['society'])  # Society
    date_of_birth = forms.DateTimeField(widget=widgets['date_of_birth'](attrs={'type': 'date'}),
                                        error_messages=erro_dict,
                                        label=labels['date_of_birth'])  # Date of birth.
    phone_number = forms.CharField(widget=widgets['phone_number'], error_messages=erro_dict,
                                   label=labels['phone_number'])  # phone number
    email_address = forms.EmailField(widget=widgets['email_address'], error_messages=erro_dict,
                                     label=labels['email_address'])  # email address.
    image = forms.ImageField(widget=widgets['image'](attrs={'class': "uploadFile img",
                                                            'style': "width: 0;height: 0;",
                                                            'overflow': "hidden"}),
                             label=labels['image'], required=False)

    class Meta:
        model = Player
        fields = '__all__'
