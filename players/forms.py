from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as tran
from .models import *


class PlayerValidator(forms.ModelForm):
    labels = {
        'name': tran('name'),
        'first_name': tran('first_name'),
        'address': tran('street_house number'),
        'post_code': tran('post_code'),
        'city': tran('city'),
        'society': tran('society'),
        'date_of_birth': tran('date_of_birth'),
        'phone_number': tran('phone_number'),
        'email_address': tran('email_address'),
        'image': tran('image')
    }
    widgets = {
        'name': forms.TextInput,
        'first_name': forms.TextInput,
        'address': forms.TextInput,
        'post_code': forms.TextInput,
        'city': forms.TextInput,
        'society': forms.TextInput,
        'date_of_birth': forms.DateInput,
        'phone_number': forms.NumberInput,
        'email_address': forms.EmailInput,
        'image': forms.FileInput
    }

    form_validators = {
        'name': [RegexValidator('^[a-zA-Z]*$', message=tran("text_error_message"))],
        'first_name': [RegexValidator('^[a-zA-Z]*$', message=tran("text_error_message"))],
        'phone_number': [RegexValidator('^[0-9]*$', message=tran("phone_number_error_message"))],
    }

    address_error_dict = post_code_error_dict = erro_dict = dict()
    address_error_dict[
        'required'] = tran("address_required_error_message")
    post_code_error_dict[
        'required'] = tran("post_code_required_error_message")
    erro_dict['required'] = tran("default_required_error_message")

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
    date_of_birth = forms.DateField(widget=widgets['date_of_birth'](
        attrs={'type': 'date'}
    ),
        error_messages=erro_dict,
        label=labels['date_of_birth'],
    )  # Date of birth.
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
        fields = ['name', 'first_name', 'address', 'post_code', 'city', 'society', 'date_of_birth'
            , 'phone_number', 'email_address', 'image']


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plans
        fields = "__all__"
