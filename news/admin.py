from django.contrib import admin
from .models import PostCategory
from .models import NewsPost
from .models import Source


class NewsPostAdmin(admin.ModelAdmin):
    list_filter = ('source_id',)


admin.site.register(PostCategory)
admin.site.register(Source)
admin.site.register(NewsPost, NewsPostAdmin)

