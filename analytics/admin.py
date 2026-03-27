from django.contrib import admin
from analytics.models import FeatureClick

@admin.register(FeatureClick)
class FeatureClickAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'feature_name', 'timestamp')
    list_filter = ('feature_name', 'timestamp', 'user__gender')
    search_fields = ('user__username', 'feature_name')
    readonly_fields = ('id', 'timestamp', 'user')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)