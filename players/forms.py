"""@package Players application
Forms objects.
At the heart of this system of components is Django’s Form class.
In much the same way that a Django model describes the logical structure of an object, its behavior,
and the way its parts are represented to us, a Form class describes a form and determines how it works and appears.

In a similar way that a model class’s fields map to database fields, a form class’s fields map to HTML form <input> elements.
(A ModelForm maps a model class’s fields to HTML form <input> elements via a Form; this is what the Django admin is based upon.)
A form’s fields are themselves classes; they manage form data and perform validation when a form is submitted.
A DateField and a FileField handle very different kinds of data and have to do different things with it.
A form field is represented to a user in the browser as an HTML “widget” - a piece of user interface machinery.
Each field type has an appropriate default Widget class, but these can be overridden as required.
for more information visit: https://docs.djangoproject.com/en/3.2/topics/forms/
"""
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as tran
from .models import *


class PlayerValidator(forms.ModelForm):
    """
    Documentation for PlayerValidator class:
    it is a class that defines fields, labels, widgets...etc to render an html form
    """

    # labels section
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

    # widgets section
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
    # validators section
    form_validators = {
        'name': [RegexValidator('^[a-zA-Z]*$', message=tran("text_error_message"))],
        'first_name': [RegexValidator('^[a-zA-Z]*$', message=tran("text_error_message"))],
        'phone_number': [RegexValidator('^[0-9]*$', message=tran("phone_number_error_message"))],
    }

    # error messages section
    address_error_dict = post_code_error_dict = erro_dict = dict()
    address_error_dict[
        'required'] = tran("address_required_error_message")
    post_code_error_dict[
        'required'] = tran("post_code_required_error_message")
    erro_dict['required'] = tran("default_required_error_message")

    # fields section
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
        """
        Documentation for PlayerValidator Meta class:
        a class that attach Player model with the Player form set a list of required fields
        """
        model = Player
        fields = ['name', 'first_name', 'address', 'post_code', 'city', 'society', 'date_of_birth'
            , 'phone_number', 'email_address', 'image']


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plans
        fields = "__all__"
