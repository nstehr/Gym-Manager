from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset


urlpatterns = patterns('crossfit.workout_tracker.views',
    (r'^$', 'index'),
    (r'^schedule/$', 'get_schedule'),
    (r'^schedule/registered/$', 'get_users_schedule'),
    (r'^schedule/feed/$', 'get_schedule_data'),
    (r'^schedule/feed/(?P<user>\w+)/$', 'get_users_schedule_data'),
    (r'^schedule/export/(?P<user_id>\d+)/schedule.ics$', 'export_schedule'),
    (r'^class/(?P<class_id>\d+)/$', 'class_detail'),
    #(r'^class/(?P<class_id>\d+)/roster/$', 'get_class_roster'),
    (r'^class/(?P<class_id>\d+)/register/$', 'class_register'),
    (r'^class/(?P<class_id>\d+)/register/all/$', 'class_register_all_of_type'),
    (r'^class/(?P<class_id>\d+)/leave/$', 'class_leave'),
    (r'^class/(?P<class_id>\d+)/delete/$', 'class_delete'),
    (r'^class/(?P<class_id>\d+)/delete/all/$', 'class_delete_all_of_type'),
    (r'^class/(?P<class_id>\d+)/roster/roster.pdf$', 'generate_class_list'),
    (r'^class/(?P<class_id>\d+)/remove/user/(?P<student_id>\d+)$', 'remove_user_from_class'),
    (r'^class/create/$', 'sched_class_create'),
    (r'^class/modify/$', 'sched_class_modify'),
    (r'^class/(?P<class_id>\d+)/recur/$', 'make_event_recurring'),
    (r'^class/description/create/$', 'create_class'),
    (r'^workout/(?P<workout_id>\d+)/$', 'workout_detail'),
    (r'^workout/create/$', 'create_workout'),
    (r'^login/$', 'login_user'),
    (r'^logout/$', 'logout_user'),
    (r'^user/(?P<user>\w+)/$', 'get_user_profile'),
    (r'^profile/$', 'get_current_user_profile'),
    (r'^profile/(?P<workout_id>\d+)/comment/create/$', 'create_comment'),
    (r'^profile/(?P<profile_id>\d+)/comments/$', 'get_comments'),
    (r'^profile/comments/$', 'get_my_comments'),
    (r'^profile/update/$', 'update_user'),
    (r'^profile/details/$', 'get_current_user_details'),
    (r'^profile/details/(?P<user>\w+)/$', 'get_user_details'),
    (r'^users/$', 'get_users'),
    (r'^register/$', 'create_user'),
    (r'^result/create/$', 'create_workout_entry'),
    (r'^result/(?P<entry_id>\d+)/$', 'entry_detail'),
    (r'^result/(?P<entry_id>\d+)/update/$', 'update_workout_entry'),
    

   
)