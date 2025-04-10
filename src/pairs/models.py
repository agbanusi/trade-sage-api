from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from signals.models import TradingPair

User = get_user_model()


class PatternCategory(models.TextChoices):
    TECHNICAL = "TECHNICAL", _("Technical")
    HARMONIC = "HARMONIC", _("Harmonic")
    CANDLESTICK = "CANDLESTICK", _("Candlestick")


class PatternType(models.Model):
    """
    Defines a specific chart pattern type (e.g., Double Bottom, Head and Shoulders)
    """
    name = models.CharField(_("Name"), max_length=100)
    category = models.CharField(
        _("Category"), 
        max_length=20, 
        choices=PatternCategory.choices
    )
    description = models.TextField(_("Description"), blank=True)
    is_bullish = models.BooleanField(_("Bullish"), default=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Pattern Type")
        verbose_name_plural = _("Pattern Types")
        unique_together = [['name', 'category']]
        ordering = ["category", "name"]
    
    def __str__(self):
        direction = "Bullish" if self.is_bullish else "Bearish"
        return f"{direction} {self.name} ({self.get_category_display()})"


class TimeFrame(models.TextChoices):
    M1 = "1m", _("1 Minute")
    M5 = "5m", _("5 Minutes")
    M15 = "15m", _("15 Minutes")
    M30 = "30m", _("30 Minutes")
    H1 = "1h", _("1 Hour")
    H4 = "4h", _("4 Hours")
    D1 = "1d", _("1 Day")
    W1 = "1w", _("1 Week")
    MN = "1M", _("1 Month")


class PatternStatus(models.TextChoices):
    FORMING = "FORMING", _("Forming")
    COMPLETE = "COMPLETE", _("Complete")
    FAILED = "FAILED", _("Failed")
    TARGET_HIT = "TARGET_HIT", _("Target Hit")


class DetectedPattern(models.Model):
    """
    A pattern that has been detected on a specific trading pair and timeframe
    """
    pair = models.ForeignKey(
        TradingPair,
        on_delete=models.CASCADE,
        related_name="detected_patterns",
        verbose_name=_("Trading Pair")
    )
    pattern_type = models.ForeignKey(
        PatternType,
        on_delete=models.CASCADE,
        related_name="detections",
        verbose_name=_("Pattern Type")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="detected_patterns",
        verbose_name=_("User"),
        null=True,
        blank=True
    )
    timeframe = models.CharField(
        _("Timeframe"),
        max_length=3,
        choices=TimeFrame.choices,
        default=TimeFrame.H1
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=PatternStatus.choices,
        default=PatternStatus.FORMING
    )
    confidence = models.DecimalField(
        _("Confidence (%)"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    price_at_detection = models.DecimalField(
        _("Price at Detection"),
        max_digits=20,
        decimal_places=8
    )
    entry_zone_low = models.DecimalField(
        _("Entry Zone Low"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )
    entry_zone_high = models.DecimalField(
        _("Entry Zone High"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )
    stop_loss = models.DecimalField(
        _("Stop Loss"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )
    target_price = models.DecimalField(
        _("Target Price"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )
    secondary_target = models.DecimalField(
        _("Secondary Target"),
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True
    )
    pattern_start_time = models.DateTimeField(_("Pattern Start Time"))
    detection_time = models.DateTimeField(_("Detection Time"), auto_now_add=True)
    completion_time = models.DateTimeField(_("Completion Time"), null=True, blank=True)
    description = models.TextField(_("Pattern Description"), blank=True)
    completion_percentage = models.DecimalField(
        _("Completion Percentage"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    chart_image = models.URLField(_("Chart Image URL"), blank=True, null=True)
    
    # For harmonic patterns
    ratios = models.JSONField(
        _("Fibonacci Ratios"),
        blank=True,
        default=dict,
        help_text=_("Stores Fibonacci ratio values for harmonic patterns")
    )
    
    # Additional metadata
    metadata = models.JSONField(_("Metadata"), blank=True, default=dict)
    
    class Meta:
        verbose_name = _("Detected Pattern")
        verbose_name_plural = _("Detected Patterns")
        ordering = ["-detection_time"]
        
    def __str__(self):
        return f"{self.pattern_type.name} on {self.pair.name} ({self.timeframe}) - {self.get_status_display()}"
    
    @property
    def is_bullish(self):
        return self.pattern_type.is_bullish
    
    @property
    def is_bearish(self):
        return not self.pattern_type.is_bullish
    
    @property
    def time_since_detection(self):
        """Returns time since detection as a string (e.g., '3h ago')"""
        if not self.detection_time:
            return None
            
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.detection_time
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = diff.days
            return f"{days}d ago"
    
    @property
    def risk_reward_ratio(self):
        """Calculate risk-reward ratio based on entry, stop loss and target"""
        if not (self.entry_zone_low and self.stop_loss and self.target_price):
            return None
            
        # Use middle of entry zone if we have a range
        if self.entry_zone_high:
            entry = (self.entry_zone_low + self.entry_zone_high) / 2
        else:
            entry = self.entry_zone_low
            
        # Calculate risk and reward
        if self.is_bullish:
            risk = entry - self.stop_loss
            reward = self.target_price - entry
        else:
            risk = self.stop_loss - entry
            reward = entry - self.target_price
            
        # Avoid division by zero
        if risk == 0:
            return None
            
        return round(reward / risk, 2) 