from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.utils import simplejson
from django.forms.models import model_to_dict
from crossfit.workout_tracker.models import *
from crossfit.workout_tracker.forms import *
from django.template.loader import get_template
from django.template import Context
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import http
import cStringIO as StringIO
import ho.pisa as pisa
import vobject
import datetime
import time


def index(request):
    c = RequestContext(request,csrf(request))
    week = get_current_week()
    start = week[0]
    end = week[1]
    scheduled_events = ScheduledClass.objects.filter(start__gte=start).filter(start__lte=end).order_by('start')
    c['scheduled_events'] = scheduled_events
    return render_to_response('index.html', c)

#workout stuff
def workout_detail(request,workout_id):
    try: 
	    c = RequestContext(request,csrf(request)) 
	    w = Workout.objects.get(pk=workout_id)
	    c['workout'] = w
    except Workout.DoesNotExist:
	    raise Http404
    return render_to_response('workouts/detail.html', c)

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def create_workout(request):
    if request.method == 'POST':
        workout = Workout(creator=request.user,creation_date=datetime.datetime.today())	
        form = WorkoutForm(request.POST,instance=workout)
        if form.is_valid():
            new_entry = form.save()
            tag_list = request.POST['tag_list']
            tag_list = tag_list.split(',')    
            for tag in tag_list:
                t,created = Tag.objects.get_or_create(name=tag)
                new_entry.tags.add(t.id)
	        new_entry.save()
            return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.workout_detail',args=[new_entry.id]))
    else:
	    form = WorkoutForm()
    return render_to_response('workouts/form.html',  RequestContext(request,{'form': form}))

#entry stuff
def entry_detail(request,entry_id):
    try:
	    c = RequestContext(request,csrf(request)) 
	    e = WorkoutEntry.objects.get(pk=entry_id)
	    c['entry'] = e
    except Workout.DoesNotExist:
	    raise Http404
    return render_to_response('entry/detail.html', c)

@user_passes_test(lambda u: u.groups.filter(name='athlete').count() ==1)
def create_workout_entry(request):
    if request.method == 'POST':
	    entry = WorkoutEntry(athlete=request.user)
	    form = WorkoutEntryForm(request.POST,instance=entry)
	    if form.is_valid():
	        new_entry = form.save()
	        return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_current_user_profile'))
    else:
	    form = WorkoutEntryForm()
    return render_to_response('entry/form.html',  RequestContext(request,{'form': form}))

@user_passes_test(lambda u: u.groups.filter(name='athlete').count() ==1)
def update_workout_entry(request,entry_id):
    entry = WorkoutEntry.objects.get(pk=entry_id)
    if request.method == 'POST':
        form = WorkoutEntryForm(request.POST)
        print form
        if form.is_valid():
            entry.description = form.cleaned_data['description']
            entry.reps = form.cleaned_data['reps']
            entry.time = form.cleaned_data['time']
            entry.weight = form.cleaned_data['weight']
            entry.workout_name = form.cleaned_data['workout_name']
            entry.save()
        else:
            return render_to_response('entry/form.html',  RequestContext(request,{'form': form}))
        return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_current_user_profile'))
    else:
        dict = model_to_dict(entry)
        form = WorkoutEntryForm(dict)
        return render_to_response('entry/update.html',RequestContext(request,{'form':form,'id':entry_id}))
        
#user profile stuff
@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def get_user_profile(request,user):
    try: 
        u = User.objects.get(username=user)
        p = u.profile
        workouts = u.workoutentry_set.all().order_by('-date')
        #paginate the workouts
    	paginator = Paginator(workouts, 10) 
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
           page = 1
        try:
            workouts = paginator.page(page)
        except (EmptyPage, InvalidPage):
            workouts = paginator.page(paginator.num_pages)
    except User.DoesNotExist:
        raise Http404
    return render_to_response('users/profile.html', RequestContext(request,{'profile': p,'workouts':workouts}))

def get_current_user_profile(request):
	p = request.user.profile
	workouts = request.user.workoutentry_set.all().order_by('-date')
	my_classes = []
    #paginate the workouts
	paginator = Paginator(workouts, 10)
	try:
	    page = int(request.GET.get('page','1'))
	except ValueError:
	    page = 1
	try:
	    workouts = paginator.page(page)
	except (EmptyPage, InvalidPage):
	    workouts = paginator.page(paginator.num_pages)
    #if its a coach profile, show the coach's classes    
	if(request.user.groups.filter(name='coach').count() ==1):
	    week_tuple = get_current_week()
	    my_classes = ScheduledClass.objects.filter(start__gte=week_tuple[0]).filter(end__lte=week_tuple[1]).filter(class_desc__coach__username=request.user.username).order_by('start')
	return render_to_response('users/profile.html', RequestContext(request,{'profile': p,'workouts':workouts,'my_classes':my_classes}))

def get_current_user_details(request):
    p = request.user.profile
    return render_to_response('users/details.html', RequestContext(request,{'profile': p}))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def get_user_details(request,user):
    p = AthleteProfile.objects.get(user__username=user)
    return render_to_response('users/details.html', RequestContext(request,{'profile': p}))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def get_users(request):
    users = User.objects.filter(groups__name='athlete')
    return render_to_response('users/list.html', RequestContext(request,{'users':users}))

#calendar and class stuff
def get_schedule(request):
    classes = ClassDescription.objects.all()
    return render_to_response('schedule/schedule.html', RequestContext(request,{'classes':classes}))

def get_users_schedule(request):
    classes = ClassDescription.objects.all()
    print request.user.username
    return render_to_response('schedule/schedule.html', RequestContext(request,{'classes':classes,'username':request.user.username}))

def get_schedule_data(request):
    start = datetime.datetime.fromtimestamp(float(request.GET['start']))
    end = datetime.datetime.fromtimestamp(float(request.GET['end']))
    scheduled_classes = ScheduledClass.objects.filter(start__gte=start).filter(end__lte=end)
    events = []
    for s in scheduled_classes:
        event = {}  
        event['id']=s.id
        event['title'] = s.class_desc.name
        event['start'] = str(s.start)
        event['end'] = str(s.end)
        event['url'] = '/crossfit/class/'+str(s.id)
        event['allDay'] = False
        if(s.students.all().count() == s.class_desc.max_students):
            event['className'] = 'full'
        if(request.user in s.students.all()):
            event['className'] = 'registered'
        if(request.user == s.class_desc.coach):
            event['className'] = 'registered'
        events.append(event)
    return HttpResponse(simplejson.dumps(events),mimetype='application/json')

def get_users_schedule_data(request,user):
    start = datetime.datetime.fromtimestamp(float(request.GET['start']))
    end = datetime.datetime.fromtimestamp(float(request.GET['end']))
    u = User.objects.get(username=user)
    if(u.groups.filter(name='coach').count() ==1):
	    scheduled_classes = ScheduledClass.objects.filter(start__gte=start).filter(end__lte=end).filter(class_desc__coach__username=user) 
    else:
        scheduled_classes = ScheduledClass.objects.filter(start__gte=start).filter(end__lte=end).filter(students__username=user)
    events = []
    for s in scheduled_classes:
        event = {}  
        event['id']=s.id
        event['title'] = s.class_desc.name
        event['start'] = str(s.start)
        event['end'] = str(s.end)
        event['url'] = '/crossfit/class/'+str(s.id)
        event['allDay'] = False
        event['className'] = 'registered'
        events.append(event)
    return HttpResponse(simplejson.dumps(events),mimetype='application/json')

@csrf_exempt
def sched_class_create(request):
    class_name = request.POST['name']
    start_time = request.POST['startTime']
    start_time = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    #set the default start time to 6 am
    if start_time.tm_hour < 6:
        start_time = time.mktime(start_time) + 60*60*6
        start_time = datetime.datetime.fromtimestamp(start_time)
        start_time = start_time.timetuple()
    end_time = start_time
    #add an hour
    end_time =  time.mktime(end_time) + 60*60
    #convert the times to datetime format
    end_time = datetime.datetime.fromtimestamp(end_time)
    start_time = datetime.datetime(*start_time[0:6])
    #create the class
    class_desc = ClassDescription.objects.get(name=class_name)
    sched_class = ScheduledClass(class_desc=class_desc,start=start_time,end=end_time)
    sched_class.save()
    return HttpResponse("Success")

@csrf_exempt
def sched_class_modify(request):
    sched_id = request.POST['id']
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    sched_class = ScheduledClass.objects.get(pk=sched_id)
    sched_class.start = startDate
    sched_class.end = endDate
    sched_class.save()
    return HttpResponse("Success")

def class_detail(request,class_id):
    try:
	    context = RequestContext(request) 
	    c = ScheduledClass.objects.get(pk=class_id)
            if(c.start <= datetime.datetime.now()):
                context['expired'] = True
	    context['class'] = c
    except ClassDescription.DoesNotExist:
        raise Http404
    return render_to_response('class/detail.html', context)

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def create_class(request):
    if request.method == 'POST':
	    class_desc = ClassDescription()
	    form = ClassForm(request.POST,instance=class_desc)
	    if form.is_valid():
		    form.save()
            return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_schedule',args=[]))
    else:
        form = ClassForm()
        form.fields['coach'].queryset = User.objects.all().filter(groups__name='coach')
    return render_to_response('class/form.html',  RequestContext(request,{'form': form}))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def get_class_roster(request,class_id):
    sched_class = ScheduledClass.objects.get(pk=class_id)
    students = sched_class.students.all()
    data = serializers.serialize("json",students,fields=('username','first_name','last_name'))
    return HttpResponse(data,mimetype='application/json')

@user_passes_test(lambda u: u.groups.filter(name='athlete').count() ==1)
def class_register(request,class_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
        c.students.add(request.user.id)
        c.save()
    except ScheduledClass.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.class_detail',args=[class_id]))
    

@user_passes_test(lambda u: u.groups.filter(name='athlete').count() ==1)
def class_register_all_of_type(request,class_id):
    classes = ScheduledClass.objects.filter(class_desc__id=class_id).filter(start__gte=datetime.datetime.now())
    for c in classes:
        c.students.add(request.user.id)
        c.save()
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_schedule',args=[]))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def class_delete_all_of_type(request,class_id):
    ScheduledClass.objects.filter(class_desc__id=class_id).delete()
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_schedule',args=[]))

@user_passes_test(lambda u: u.groups.filter(name='athlete').count() ==1)
def class_leave(request,class_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
        c.students.remove(request.user.id)
        c.save()
    except ScheduledClass.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.class_detail',args=[class_id]))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def remove_user_from_class(request,class_id,student_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
        c.students.remove(student_id)
        c.save()
    except ScheduledClass.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.class_detail',args=[class_id]))
    
@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def class_delete(request,class_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
        c.delete()
    except ScheduledClass.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_schedule',args=[]))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def generate_class_list(request,class_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
    except ScheduledClass.DoesNotExist:
        raise Http404
    return render_to_pdf('class/roster.html',{'pagesize':'A4','class':c})

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def make_event_recurring(request,class_id):
    try:
        c = ScheduledClass.objects.get(pk=class_id)
        class_desc = c.class_desc
        end_date = request.POST['end_date']
        end_date = datetime.datetime.strptime(end_date,"%m/%d/%Y")
        class_start = c.start
        class_end = c.end
        s = class_start+datetime.timedelta(days=7)
        e = class_end+datetime.timedelta(days=7)
        while(s.date() < end_date.date()):
            sched_class = ScheduledClass(class_desc=class_desc,start=s,end=e)
            sched_class.save()
            s = s+datetime.timedelta(days=7)
            e = e+datetime.timedelta(days=7)     
    except ScheduledClass.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_schedule',args=[])) 

def export_schedule(request,user_id):
    u = User.objects.get(pk=user_id)
    if(u.groups.filter(name='coach').count() ==1):
	    scheduled_classes = ScheduledClass.objects.filter(class_desc__coach__username=u.username) 
    else:
        scheduled_classes = ScheduledClass.objects.filter(students__username=u.username)
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'
    for event in scheduled_classes:
        vevent = cal.add('vevent')
        vevent.add('dtstart').value=event.start
        vevent.add('dtend').value=event.end
        vevent.add('summary').value=event.class_desc.name
        vevent.add('uid').value=str(event.id)
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'schedule.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=schedule.ics'
    return response    

#comment stuff
@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def create_comment(request,workout_id):
    entry = WorkoutEntry.objects.get(pk=workout_id)
    if request.method == 'POST':
	    comment = Comment(coach=request.user,entry=entry,creation_date=datetime.datetime.now())  
	    form = CommentForm(request.POST,instance=comment)
	    if form.is_valid():
	        form.save()
	        return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_user_profile',args=[entry.athlete.username]))
    else:
	    form = CommentForm()
    return render_to_response('comment/form.html',  RequestContext(request,{'form': form,'id':entry.id}))

@user_passes_test(lambda u: u.groups.filter(name='coach').count() ==1)
def get_comments(request,profile_id):
    comments = Comment.objects.filter(athlete__id=profile_id).order_by('-creation_date')
    paginator = Paginator(comments, 10) 
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
       page = 1
    try:
        comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        comments = paginator.page(paginator.num_pages)
    return render_to_response('comment/comments.html',  RequestContext(request,{'comments': comments}))

def get_my_comments(request):
    comments = Comment.objects.filter(athlete__id=request.user.profile.id).order_by('-creation_date')
    paginator = Paginator(comments, 10) 
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
       page = 1
    try:
        comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        comments = paginator.page(paginator.num_pages)
    return render_to_response('comment/comments.html',  RequestContext(request,{'comments': comments}))

#authentication methods
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_current_user_profile'))
        else:
            return HttpResponse("Disabled Account")
    else:
        return HttpResponse("Invalid Login")

def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if 'waiver' not in request.POST:
            return render_to_response('users/create_user.html',RequestContext(request,{'form':form,'no_waiver':True}))
        #form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            g = Group.objects.get(name='athlete')
            new_user.groups.add(g)
            new_user.is_active = True
            new_user.save()
            new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            if new_user.is_active:
                login(request,new_user)
            return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.update_user',args=[]))
    else:
        form = UserCreationForm()
    return render_to_response('users/create_user.html',  RequestContext(request,{'form': form}))

def update_user(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            p = AthleteProfile.objects.get(user__id=request.user.id)
            p.phone = form.cleaned_data['phone']
            p.emergency_contact_name = form.cleaned_data['emergency_contact_name']
            p.emergency_contact_phone = form.cleaned_data['emergency_contact_phone']
            p.injuries = form.cleaned_data['injuries']
            p.medical_history = form.cleaned_data['medical_history']
            p.save()
            return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.get_current_user_profile',args=[]))
    else:
        form = UpdateUserForm({'email':request.user.email,'first_name':request.user.first_name,
        'last_name':request.user.last_name,'username':request.user.username,'phone':request.user.profile.phone,
        'emergency_contact_name':request.user.profile.emergency_contact_name,'emergency_contact_phone':request.user.profile.emergency_contact_phone,
        'injuries':request.user.profile.injuries,'medical_history':request.user.profile.medical_history})
    return render_to_response('users/update.html',RequestContext(request,{'form':form}))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('crossfit.workout_tracker.views.index'))
    
    
#misc
#def get_current_week():
#    cal = datetime.datetime.now().isocalendar()
#    year = cal[0]
#    week = cal[1]
#    d = datetime.date(year,1,1)
#    if(d.weekday()>3):
#        d = d+datetime.timedelta(7-d.weekday())
#    else:
#        d = d - datetime.timedelta(d.weekday())
#    dlt = datetime.timedelta(days = (week-1)*7)
#    return d + dlt,  d + dlt + datetime.timedelta(days=6)

#from: http://bytes.com/topic/python/answers/499819-getting-start-end-dates-given-week-number
def get_current_week():
    cal = datetime.datetime.now().isocalendar()
    year = cal[0]
    #iso calendar weeks starts with Monday, I want to start on Sunday, so I use this
    week = int(datetime.datetime.now().strftime('%U'))
    startOfYear = datetime.date(year,1,1)
    week0 = startOfYear - datetime.timedelta(days=startOfYear.isoweekday())
    sun = week0 + datetime.timedelta(weeks = week)
    sat = sun + datetime.timedelta(days=6)
    return sun,sat
  
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))




