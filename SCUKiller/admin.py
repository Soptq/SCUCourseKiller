from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(UserProfile, )
admin.site.register(jwcAccount, )
admin.site.register(courses, )
admin.site.register(codes, )
admin.site.register(notification, )