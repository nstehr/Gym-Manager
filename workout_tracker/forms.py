from crossfit.workout_tracker.models import *
from django.forms import ModelForm,DateField
from django import forms
from django.contrib.localflavor.ca.forms import CAPhoneNumberField

class WorkoutEntryForm(ModelForm):
    class Meta:
	    model = WorkoutEntry
	    exclude = ('athlete')
	
class WorkoutForm(ModelForm):
    tag_list = forms.CharField()
    class Meta:
	    model = Workout
	    exclude = ('creator','creation_date','tags')
	    widgets = {'creation_date':DateField}
	
class ClassForm(ModelForm):
    class Meta:
        model = ClassDescription

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('coach','entry','creation_date')


class UpdateUserForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = CAPhoneNumberField()
    emergency_contact_name = forms.CharField(max_length = 200)
    emergency_contact_phone = CAPhoneNumberField()
    injuries = forms.CharField(widget=forms.Textarea(),required=False)
    medical_history = forms.CharField(widget=forms.Textarea(),required=False)