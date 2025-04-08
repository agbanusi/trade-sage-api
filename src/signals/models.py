from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class TradingPair(models.Model):
    """Trading pair model (e.g., BTC/USD, ETH/USD)."""
    
    name = models.CharField(_("Name"), max_length=20, unique=True)
    base_asset = models.CharField(_("Base Asset"), max_length=10)
    quote_asset = models.CharField(_("Quote Asset"), max_length=10)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Trading Pair")
        verbose_name_plural = _("Trading Pairs")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Instrument(models.Model):
    """
    Trading instrument/indicator (e.g., RSI, MACD, Moving Average)
    used for making trading decisions.
    """
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Instrument")
        verbose_name_plural = _("Instruments")
        ordering = ["name"]

    def __str__(self):
        return self.name


class WeightedInstrument(models.Model):
    """
    Associates a user's weighted instruments with a trading pair.
    Weights must sum to 100 per user and pair.
    Maximum of 5 instruments per user and pair.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="weighted_instruments",
        verbose_name=_("User")
    )
    pair = models.ForeignKey(
        TradingPair,
        on_delete=models.CASCADE,
        related_name="weighted_instruments",
        verbose_name=_("Trading Pair")
    )
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="weighted_instances",
        verbose_name=_("Instrument")
    )
    weight = models.PositiveIntegerField(
        _("Weight"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
        help_text=_("Weight (1-100) assigned to this instrument for this pair. Sum of weights per pair must be 100.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Weighted Instrument")
        verbose_name_plural = _("Weighted Instruments")
        unique_together = [['user', 'pair', 'instrument']]
        ordering = ["-weight"]

    def __str__(self):
        return f"{self.user.email} - {self.pair.name} - {self.instrument.name} ({self.weight}%)"

    def save(self, *args, **kwargs):
        # Check if adding this would exceed the maximum of 5 instruments per user and pair
        existing_count = WeightedInstrument.objects.filter(
            user=self.user,
            pair=self.pair
        ).exclude(pk=self.pk).count()
        
        if existing_count >= 5:
            raise ValueError("Maximum of 5 instruments allowed per user and trading pair")
        
        # Proceed with regular save
        super().save(*args, **kwargs)
        
        # Check if total weights add up to 100 per user and pair
        total_weight = WeightedInstrument.objects.filter(
            user=self.user,
            pair=self.pair
        ).exclude(pk=self.pk).aggregate(models.Sum('weight'))['weight__sum'] or 0
        total_weight += self.weight
        
        if total_weight > 100:
            raise ValueError(f"Total weights ({total_weight}) exceed 100 for this user and pair")


class SignalType(models.TextChoices):
    BUY = "BUY", _("Buy")
    SELL = "SELL", _("Sell")
    HOLD = "HOLD", _("Hold")


class Signal(models.Model):
    """Trading signal model with trade parameters."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="signals",
        verbose_name=_("User"),
        null=True
    )
    pair = models.ForeignKey(
        TradingPair, 
        on_delete=models.CASCADE, 
        related_name="signals",
        verbose_name=_("Trading Pair")
    )
    signal_type = models.CharField(
        _("Signal Type"),
        max_length=4,
        choices=SignalType.choices,
        default=SignalType.HOLD
    )
    price = models.DecimalField(_("Current Price"), max_digits=20, decimal_places=8)
    entry_price = models.DecimalField(_("Entry Price"), max_digits=20, decimal_places=8, null=True, blank=True)
    stop_loss = models.DecimalField(_("Stop Loss"), max_digits=20, decimal_places=8, null=True, blank=True)
    take_profit = models.DecimalField(_("Take Profit"), max_digits=20, decimal_places=8, null=True, blank=True)
    potential_gain = models.DecimalField(_("Potential Gain (%)"), max_digits=8, decimal_places=2, null=True, blank=True)
    risk_reward_ratio = models.DecimalField(_("Risk/Reward Ratio"), max_digits=8, decimal_places=2, null=True, blank=True)
    confidence = models.DecimalField(_("Confidence"), max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_executed = models.BooleanField(_("Executed"), default=False)
    execution_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Trading Signal")
        verbose_name_plural = _("Trading Signals")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.pair.name} - {self.signal_type} at {self.price}"


class SignalReport(models.Model):
    """
    Hourly report of signal generation for users and pairs.
    Stores aggregated data about signals generated.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    pair = models.ForeignKey(
        TradingPair,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Trading Pair")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="signal_reports",
        verbose_name=_("User"),
        null=True
    )
    price = models.DecimalField(_("Current Price"), max_digits=20, decimal_places=8)
    buy_signals = models.PositiveIntegerField(_("Buy Signals"), default=0)
    sell_signals = models.PositiveIntegerField(_("Sell Signals"), default=0)
    hold_signals = models.PositiveIntegerField(_("Hold Signals"), default=0)
    avg_confidence = models.DecimalField(_("Average Confidence"), max_digits=5, decimal_places=2, default=0)
    avg_risk_reward = models.DecimalField(_("Average Risk/Reward"), max_digits=8, decimal_places=2, default=0, null=True)
    data = models.JSONField(_("Additional Data"), blank=True, default=dict)
    
    class Meta:
        verbose_name = _("Signal Report")
        verbose_name_plural = _("Signal Reports")
        ordering = ["-timestamp"]
        
    def __str__(self):
        if self.user:
            return f"Report for {self.user.email} on {self.pair.name} at {self.timestamp}"
        else:
            return f"Report for {self.pair.name} at {self.timestamp}" 