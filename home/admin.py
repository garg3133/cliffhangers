from django.contrib import admin

from .models import Road, Image, Issue, IssueDetail

# Register your models here.
@admin.register(Road)
class Roadadmin(admin.ModelAdmin):
    list_display = ('road_id', 'pci', 'state', 'district', 'block')
    search_fields = ('road_id', 'state', 'district', 'block')
    ordering = ('state', 'district', 'block', 'road_id',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('get_road_id', 'image_id')
    search_fields = ('road__road_id', 'image_id')
    ordering = ('road__road_id', 'image_id')

    def get_road_id(self, obj):
        return f'{obj.road.road_id}'
    get_road_id.short_description = 'Road ID'
    get_road_id.admin_order_field = 'road__road_id'

    # def get_location(self, obj):
    #     return f'{obj.road.location}'
    # get_location.short_description = 'Location'
    # get_location.admin_order_field = 'road__location'

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'name')
    search_fields = ('issue_id', 'name')
    ordering = ('issue_id',)

@admin.register(IssueDetail)
class IssueDetailAdmin(admin.ModelAdmin):
    list_display = ('get_image_id', 'get_issue_name', 'count', 'quality')
    search_fields = ('image__image_id', 'issue__name')
    list_filter = ('issue__name', 'quality')
    ordering = ('image__image_id', 'issue__issue_id')

    def get_image_id(self, obj):
        return f'{obj.image.image_id}'
    get_image_id.short_description = 'Image ID'
    get_image_id.admin_order_field = 'image__image_id'

    def get_issue_name(self, obj):
        return f'{obj.issue.name}'
    get_issue_name.short_description = 'Issue'
    get_issue_name.admin_order_field = 'issue__name'
