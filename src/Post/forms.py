import re
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from .models import GeneralPost



class GeneralPostCreateAlterForm(forms.ModelForm):
	title = forms.CharField(label='Enter Title',max_length=50,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Write a title','size':'30'}))
	content = forms.CharField(label='Enter Content', max_length=1000, widget=CKEditorWidget())
	tag = forms.CharField(label='Tag',max_length=35,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Write a tag (Example: #tag #Sogang )'}))
	class Meta:
		model = GeneralPost
		fields = ('title','content')

	def clean_tag(self):
		data = self.cleaned_data['tag']
		tag_list = re.findall(r'(?<!#)[#]{1}[\w]+', data)
		subtracted_data = re.sub(r'(?<!#)[#]{1}[\w]+', '', data)
		subtracted_data = re.sub(r' ', '', subtracted_data)
		if len(tag_list) > 10:
			raise forms.ValidationError("No more than 10 Tags!")
		if subtracted_data:
			raise forms.ValidationError("Hash tag must have only one Hash")		
		tag_list = set(tag_list)
		# if tag_list() :
		# 	raise forms.VallidationError("Required. 35 characters or fewer for 1tag")
		return tag_list



class GeneralPostDeleteForm(forms.ModelForm):

	class Meta:
		model = GeneralPost
		fields = ()