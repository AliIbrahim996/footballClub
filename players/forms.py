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
from django.forms import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as tran
from .models import *
from django_starfield import Stars
from abc import abstractmethod, ABC


class PrefilledExtraFormsFormsetMixin(ABC):
    """
    A formset mixin class that can be added to admin inline formset classes to insert prefilled
    extra forms.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # these instances are better fetched later, as this enables subclasses to access attributes
        # that are later injected into the class e.g. NestedAdminWithFormParents
        self.extra_forms_instances = None

    def total_form_count(self):
        """
        Overrides BaseFormSet.total_form_count() to account for extra prefilled forms.
        """
        count = super().total_form_count()
        # fetch instances by calling the provided abstract method (if we haven't already did)
        if self.extra_forms_instances is None:
            # turn into a list to enable fast random access
            self.extra_forms_instances = list(self.get_prefilled_forms_queryset())
        if not self.is_bound:
            # if it is a bound form, then prefilled form have already been inserted and the count
            # obtained from super().total_form_count() already includes them
            # otherwise, we need to increase count in order to add prefilled forms
            count += len(self.extra_forms_instances)
        return count

    def _construct_form(self, i, **kwargs):
        """
        Overrides BaseFormSet._construct_form to configure initial values for prefilled forms.
        """
        form = super()._construct_form(i, **kwargs)
        # set initial value for added prefilled forms
        # this has to be done even for bound forms, to help django discard unchanged forms
        prefilled_form_idx = i - self.initial_form_count()
        if 0 <= prefilled_form_idx < len(self.extra_forms_instances):
            self.prefill_extra_form(form, self.extra_forms_instances[prefilled_form_idx])
        return form

    @abstractmethod
    def get_prefilled_forms_queryset(self):
        """
        Has to be overridden in subclasses to return a queryset/list of elements for which we need
        to have extra prefilled forms. The length of the returned queryset/list determines the
        number of extra forms to insert.
        """

    @abstractmethod
    def prefill_extra_form(self, form, instance):
        """
        Has to be overridden in subclasses to set the initial field values for form according to
        instance. This method is called for every extra form we have added. The parameter instance
        is the form's corresponding element from the queryset/list returned by
        get_prefilled_form_queryset()
        """


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


class PlayerSkillsForm(forms.ModelForm):
    value = forms.IntegerField(required=False, widget=Stars, min_value=1, max_value=5)
    skill_comment = forms.CharField(required=False, widget=forms.TextInput, max_length=255, disabled=True)

    # modified_by = forms.CharField(required=False, widget=forms.TextInput, max_length=255, disabled=True)
    # modified_at = forms.CharField(required=False, widget=forms.TextInput, max_length=255, disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skill'].disabled = True
        self.fields['skill'].required = False
        if hasattr(self.instance, 'skill'):
            self.fields['skill_comment'].initial = self.instance.skill.comment

    class Meta:
        model = PlayerSkills
        fields = ['skill', 'value', 'modified_by', 'modified_at']


class PlayerSkillsFormset(PrefilledExtraFormsFormsetMixin, BaseInlineFormSet):
    def get_prefilled_forms_queryset(self):
        p_id = self.instance.id
        skills_list = PlayerSkills.objects.filter(player=p_id).values_list("skill", flat=True)
        skills_q_s = Skills.objects.exclude(id__in=skills_list)
        return skills_q_s

    def prefill_extra_form(self, form, instance):
        form.fields['skill'].initial = instance
        form.fields['skill_comment'].initial = instance.comment
