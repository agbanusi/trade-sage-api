from django.contrib import admin
from .models import PatternType, DetectedPattern


@admin.register(PatternType)
class PatternTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_bullish', 'is_active', 'created_at']
    list_filter = ['category', 'is_bullish', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(DetectedPattern)
class DetectedPatternAdmin(admin.ModelAdmin):
    list_display = [
        'pattern_type', 'pair', 'timeframe', 'status', 
        'confidence', 'detection_time', 'completion_percentage'
    ]
    list_filter = [
        'status', 'pattern_type__category', 'pattern_type__is_bullish', 
        'timeframe', 'pair', 'user'
    ]
    search_fields = ['pattern_type__name', 'pair__name', 'description']
    readonly_fields = ['detection_time', 'risk_reward_ratio']
    date_hierarchy = 'detection_time'
    fieldsets = (
        ('Basic Information', {
            'fields': ('pattern_type', 'pair', 'user', 'timeframe', 'status', 
                      'confidence', 'description', 'chart_image')
        }),
        ('Price Data', {
            'fields': ('price_at_detection', 'entry_zone_low', 'entry_zone_high', 
                      'stop_loss', 'target_price', 'secondary_target', 'risk_reward_ratio')
        }),
        ('Timing', {
            'fields': ('pattern_start_time', 'detection_time', 'completion_time', 
                      'completion_percentage')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('ratios', 'metadata')
        }),
    ) 