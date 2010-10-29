
#from http://djangosnippets.org/snippets/895/
#from http://djangosnippets.org/snippets/858/

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import SafeUnicode
import re
from django.utils.safestring import mark_safe

register=template.Library()



@register.filter
def in_group(user, group):
	"""Returns True/False if the user is in the given group(s).
	Usage::
		{% if user|in_group:"Friends" %}
		or
		{% if user|in_group:"Friends,Enemies" %}
		...
		{% endif %}
	You can specify a single group or comma-delimited list.
	No white space allowed.
	"""
	import re
	if re.search(',', group): group_list = re.sub('\s+','',group).split(',')
	elif re.search(' ', group): group_list = group.split()
	else: group_list = [group]
	user_groups = []
	for group in user.groups.all(): user_groups.append(str(group.name))
	if filter(lambda x:x in user_groups, group_list): return True
	else: return False

@register.filter
@stringfilter
def youtube(url):
    regex = re.compile(r"^(http://)?(www\.)?(youtube\.com/watch\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})")
    match = regex.match(url)
    if not match: return ""
    video_id = match.group('id')
    
    val = """<object width="480" height="385"><param name="movie" 
          value="http://www.youtube.com/v/%s&amp;hl=en_US&amp;fs=1">
          </param><param name="allowFullScreen" value="true"></param>
          <param name="allowscriptaccess" value="always"></param>
          <embed src="http://www.youtube.com/v/%s&amp;hl=en_US&amp;fs=1" 
          type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" 
           width="480" height="385"></embed></object>"""  % (video_id, video_id)
    return mark_safe(val)
	
	
youtube.is_safe = False
in_group.is_safe = True