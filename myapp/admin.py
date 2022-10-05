from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(OxfordWord)
admin.site.register(OxExample)
admin.site.register(Inflection)
admin.site.register(CEFR_Level)
admin.site.register(Topic)
admin.site.register(UserSettings)
admin.site.register(RepeatWord)

### COURSES ###
admin.site.register(Course)
admin.site.register(Data)
admin.site.register(SubCourse)
admin.site.register(ServerChoice)
admin.site.register(VideoObject)
admin.site.register(CraftStack)