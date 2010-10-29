from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail,send_mass_mail,EmailMessage
from django.db.models.signals import post_save,pre_delete
import datetime

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length = 200)
    def __unicode__(self):
        return self.name

class Workout(models.Model):
    name = models.CharField(max_length = 200,blank = False)
    description = models.TextField(blank = False)
    coach_tip = models.TextField(blank = True)
    creator = models.ForeignKey(User)
    creation_date = models.DateField()
    tags = models.ManyToManyField(Tag)
    youtube_link = models.URLField(verify_exists=True,blank=True,null=True)
    def __unicode__(self):
        return self.name
	
class WorkoutEntry(models.Model):
    #workout = models.ForeignKey(Workout)
    athlete = models.ForeignKey(User)
    workout_name = models.CharField(max_length = 200,blank = True,null = True)
    time = models.TimeField(null=True,blank=True)
    reps = models.PositiveIntegerField(null=True,blank=True)
    weight = models.PositiveIntegerField(null=True,blank=True)
    description = models.TextField()
    date = models.DateField()
    def __unicode__(self):
        return self.description
        
class AthleteProfile(models.Model):
    user = models.ForeignKey(User,unique = True)
    summary = models.TextField(null=True,blank=True)
    phone = models.TextField(max_length = 12)
    emergency_contact_name = models.CharField(max_length = 200)
    emergency_contact_phone = models.TextField(max_length = 12)
    injuries = models.TextField(null=True,blank=True)
    medical_history = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return self.user.username

class Comment(models.Model):
    comment = models.TextField(blank = False)
    coach = models.ForeignKey(User)
    creation_date = models.DateField()
    entry = models.ForeignKey(WorkoutEntry,null=True,blank=True)
    def __unicode__(self):
	    return self.comment

class ClassDescription(models.Model):
    name = models.CharField(max_length = 200,blank = False)
    description = models.TextField(blank = False)
    max_students = models.PositiveIntegerField()
    coach = models.ForeignKey(User)
    def __unicode__(self):
        return self.name

class ScheduledClass(models.Model):
    class_desc = models.ForeignKey(ClassDescription)
    start = models.DateTimeField()
    end = models.DateTimeField()
    students = models.ManyToManyField(User,null=True,blank=True)
    def __unicode__(self):
        return self.class_desc.name


def class_deleted(sender,instance,**kwargs):
    subject = instance.class_desc.name + " Cancelled"
    message = "Just wanted to let you know that the %s class on %s has been cancelled.\n\n  Sorry for the inconvience.\n\n %s" % (instance.class_desc.name,instance.start.strftime("%A,%B %d"),instance.class_desc.coach.first_name)
    from_email = 'admin@badlands.laserdeathstehr.com'
    email_list = []
    if (instance.start >= datetime.datetime.now()):
        for student in instance.students.all():
            greeting = "Hey %s\n\n" % student.first_name
            personal_msg = greeting+message 
            email = (subject,personal_msg,from_email,[student.email])
            email_list.append(email)
        if(len(email_list) > 0):
            send_mass_mail(tuple(email_list))

def comment_created(sender,instance,**kwargs):
    subject = "A Coach Left You a Comment!"
    coach = instance.coach.first_name
    athlete = instance.entry.athlete
    message = "Hi %s\n\n%s\n\n%s" % (athlete.first_name,instance.comment,coach)
    email = EmailMessage(subject,message,'admin@badlands.laserdeathstehr.com',[athlete.email],headers={'Reply-To':instance.coach.email})
    email.send()

#register signals
pre_delete.connect(class_deleted,sender=ScheduledClass)
post_save.connect(comment_created,sender=Comment)
#create a profile automatically on first lookup
User.profile = property(lambda u: AthleteProfile.objects.get_or_create(user=u)[0])


    
    
	