# -*- coding: utf-8 -*-
from django_filters import *  # noqa: F401, F403

from django import forms
from graphene_django.forms.converter import convert_form_field
from graphene import List, String


@convert_form_field.register(forms.MultipleChoiceField)
def convert_form_field_to_string_list(field):
    return List(String, description=field.help_text, required=field.required)
