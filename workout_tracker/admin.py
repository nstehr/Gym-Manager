from crossfit.workout_tracker.models import *
from django.contrib import admin

admin.site.register(Workout)
admin.site.register(Tag)
admin.site.register(WorkoutEntry)
admin.site.register(Comment)
admin.site.register(AthleteProfile)
admin.site.register(ClassDescription)
admin.site.register(ScheduledClass)