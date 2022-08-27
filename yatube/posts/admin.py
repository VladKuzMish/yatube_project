from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'post', 'text', 'created')
    empty_value_display = '-пусто-'
    search_fields = ('text',)
    list_filter = ('created',)


admin.site.register(Comment, CommentAdmin)
