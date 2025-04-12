from django.contrib import admin
from .models import (
    Pair, 
    ChartAnalysis, 
    SavedIndicator, 
    SupportResistanceLevel,
    SignalPerformance,
    IndicatorPerformance,
    TimeframePerformance,
    PairPerformance,
    RiskAnalysis
)


@admin.register(Pair)
class PairAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active')
    search_fields = ('name', 'display_name')
    list_filter = ('is_active',)


@admin.register(ChartAnalysis)
class ChartAnalysisAdmin(admin.ModelAdmin):
    list_display = ('pair', 'user', 'timeframe', 'current_price', 'overall_signal', 'volatility_level', 'created')
    list_filter = ('timeframe', 'overall_signal', 'volatility_level')
    search_fields = ('pair__name', 'user__email')
    date_hierarchy = 'created'


@admin.register(SavedIndicator)
class SavedIndicatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'pair', 'indicator_type', 'created')
    list_filter = ('indicator_type',)
    search_fields = ('user__email', 'pair__name')
    date_hierarchy = 'created'


@admin.register(SupportResistanceLevel)
class SupportResistanceLevelAdmin(admin.ModelAdmin):
    list_display = ('pair', 'timeframe', 'level_type', 'price_level', 'strength', 'created_by', 'created')
    list_filter = ('timeframe', 'level_type', 'strength')
    search_fields = ('pair__name', 'created_by__email')
    date_hierarchy = 'created'


@admin.register(SignalPerformance)
class SignalPerformanceAdmin(admin.ModelAdmin):
    list_display = ('pair', 'user', 'timeframe', 'signal_type', 'result', 'profit_loss', 'entry_time', 'exit_time')
    list_filter = ('timeframe', 'signal_type', 'result')
    search_fields = ('pair__name', 'user__email')
    date_hierarchy = 'entry_time'


@admin.register(IndicatorPerformance)
class IndicatorPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'indicator_type', 'pair', 'timeframe', 'accuracy', 'sample_size', 'last_updated')
    list_filter = ('indicator_type', 'timeframe')
    search_fields = ('user__email', 'pair__name')


@admin.register(TimeframePerformance)
class TimeframePerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'timeframe', 'accuracy', 'win_count', 'loss_count', 'sample_size', 'last_updated')
    list_filter = ('timeframe',)
    search_fields = ('user__email',)


@admin.register(PairPerformance)
class PairPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'pair', 'accuracy', 'win_count', 'loss_count', 'sample_size', 'last_updated')
    search_fields = ('user__email', 'pair__name')


@admin.register(RiskAnalysis)
class RiskAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'win_rate', 'avg_risk_reward', 'max_drawdown', 'profit_factor', 'total_trades', 'last_updated')
    search_fields = ('user__email',)
