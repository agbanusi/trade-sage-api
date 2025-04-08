from django.contrib import admin
from .models import TradingPair, Signal, Instrument, WeightedInstrument, SignalReport


@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    list_display = ["name", "base_asset", "quote_asset", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "base_asset", "quote_asset"]


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(WeightedInstrument)
class WeightedInstrumentAdmin(admin.ModelAdmin):
    list_display = ["user", "pair", "instrument", "weight", "updated_at"]
    list_filter = ["pair", "instrument", "user"]
    search_fields = ["user__email", "pair__name", "instrument__name"]


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = [
        "pair", "user", "signal_type", "price", "entry_price", 
        "stop_loss", "take_profit", "risk_reward_ratio", 
        "confidence", "timestamp", "is_executed"
    ]
    list_filter = ["signal_type", "is_executed", "pair", "user"]
    search_fields = ["pair__name", "user__email"]
    date_hierarchy = "timestamp"


@admin.register(SignalReport)
class SignalReportAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp", "pair", "user", "price", 
        "buy_signals", "sell_signals", "hold_signals",
        "avg_confidence", "avg_risk_reward"
    ]
    list_filter = ["pair", "user", "timestamp"]
    search_fields = ["pair__name", "user__email"]
    date_hierarchy = "timestamp" 