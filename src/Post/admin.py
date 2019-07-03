from django import forms
from django.contrib import admin
from .models import GeneralPost, Tag, FilterTagRelation
from ckeditor.widgets import CKEditorWidget
admin.site.register(FilterTagRelation)
admin.site.register(Tag)

class GeneralPostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = GeneralPost
        fields = '__all__'

class GeneralPostAdmin(admin.ModelAdmin):
    form = GeneralPostAdminForm

admin.site.register(GeneralPost, GeneralPostAdmin)

