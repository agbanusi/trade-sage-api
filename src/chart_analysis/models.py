from django.db import models
from django.conf import settings
from core.models import BaseModel


class Pair(models.Model):
    """
    Model representing a trading pair (e.g., EUR/USD)
    """
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name


class Timeframe(models.TextChoices):
    """
    Available chart timeframes
    """
    ONE_MINUTE = '1m', '1 Minute'
    FIVE_MINUTES = '5m', '5 Minutes'
    FIFTEEN_MINUTES = '15m', '15 Minutes'
    THIRTY_MINUTES = '30m', '30 Minutes'
    ONE_HOUR = '1h', '1 Hour'
    FOUR_HOURS = '4h', '4 Hours'
    ONE_DAY = '1d', '1 Day'
    ONE_WEEK = '1w', '1 Week'
    ONE_MONTH = '1mo', '1 Month'


class TechnicalIndicator(models.TextChoices):
    """
    Available technical indicators
    """
    RSI = 'rsi', 'Relative Strength Index'
    MACD = 'macd', 'MACD'
    BOLLINGER = 'bollinger', 'Bollinger Bands'
    MOVING_AVG = 'ma', 'Moving Average'
    EXPONENTIAL_MA = 'ema', 'Exponential Moving Average'
    STOCHASTIC = 'stoch', 'Stochastic Oscillator'
    ADX = 'adx', 'Average Directional Index'
    ICHIMOKU = 'ichimoku', 'Ichimoku Cloud'
    FIBONACCI = 'fib', 'Fibonacci Retracement'


class UserIndicatorSettings(BaseModel):
    """
    Model to store user's indicator weights and active status for signal generation
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    indicator_type = models.CharField(
        max_length=20,
        choices=TechnicalIndicator.choices
    )
    weight = models.DecimalField(max_digits=3, decimal_places=1, default=0.5)
    is_active = models.BooleanField(default=True)
    indicator_parameters = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ('user', 'indicator_type')
        verbose_name_plural = 'User Indicator Settings'
    
    def __str__(self):
        return f"{self.indicator_type} settings for {self.user.email} (Weight: {self.weight})"


class ChartAnalysis(BaseModel):
    """
    Model representing a chart analysis for a specific pair and timeframe
    """
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timeframe = models.CharField(
        max_length=5,
        choices=Timeframe.choices,
        default=Timeframe.ONE_HOUR
    )
    
    # Price data
    current_price = models.DecimalField(max_digits=12, decimal_places=6)
    change_24h = models.DecimalField(max_digits=10, decimal_places=2)  # Percentage
    high_24h = models.DecimalField(max_digits=12, decimal_places=6)
    low_24h = models.DecimalField(max_digits=12, decimal_places=6)
    
    # Technical analysis
    analysis_data = models.JSONField(default=dict)
    overall_signal = models.CharField(
        max_length=10,
        choices=[
            ('buy', 'Buy'),
            ('sell', 'Sell'),
            ('neutral', 'Neutral')
        ]
    )
    
    # Volatility
    volatility_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High')
        ]
    )
    
    class Meta:
        unique_together = ('pair', 'user', 'timeframe')
        verbose_name_plural = 'Chart Analyses'
    
    def __str__(self):
        return f"{self.pair.name} {self.timeframe} - {self.user.email}"


class SavedIndicator(BaseModel):
    """
    Model representing a saved indicator configuration for a user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    indicator_type = models.CharField(
        max_length=20,
        choices=TechnicalIndicator.choices
    )
    settings = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ('user', 'pair', 'indicator_type')
    
    def __str__(self):
        return f"{self.indicator_type} for {self.pair.name} - {self.user.email}"


class SupportResistanceLevel(BaseModel):
    """
    Model representing support and resistance levels for a specific pair
    """
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    timeframe = models.CharField(
        max_length=5,
        choices=Timeframe.choices,
        default=Timeframe.ONE_HOUR
    )
    level_type = models.CharField(
        max_length=10,
        choices=[
            ('support', 'Support'),
            ('resistance', 'Resistance')
        ]
    )
    price_level = models.DecimalField(max_digits=12, decimal_places=6)
    strength = models.IntegerField(default=1)  # 1-10 scale
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.get_level_type_display()} at {self.price_level} for {self.pair.name}"


# Advanced Analytics Models

class SignalPerformance(BaseModel):
    """
    Model to track the performance of trading signals
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    timeframe = models.CharField(
        max_length=5,
        choices=Timeframe.choices,
        default=Timeframe.ONE_HOUR
    )
    signal_type = models.CharField(
        max_length=10,
        choices=[
            ('buy', 'Buy'),
            ('sell', 'Sell')
        ]
    )
    entry_price = models.DecimalField(max_digits=12, decimal_places=6)
    exit_price = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    target_price = models.DecimalField(max_digits=12, decimal_places=6)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=6)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(
        max_length=10,
        choices=[
            ('win', 'Win'),
            ('loss', 'Loss'),
            ('open', 'Open')
        ],
        default='open'
    )
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Percentage
    
    class Meta:
        verbose_name_plural = 'Signal Performances'
    
    def __str__(self):
        return f"{self.pair.name} {self.timeframe} {self.signal_type} - {self.result}"


class IndicatorPerformance(BaseModel):
    """
    Model to track the performance of different indicators
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    indicator_type = models.CharField(
        max_length=20,
        choices=TechnicalIndicator.choices
    )
    timeframe = models.CharField(
        max_length=5,
        choices=Timeframe.choices,
        default=Timeframe.ONE_HOUR
    )
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    sample_size = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'indicator_type', 'timeframe', 'pair')
    
    def __str__(self):
        return f"{self.indicator_type} on {self.pair.name} {self.timeframe} - {self.accuracy}%"


class TimeframePerformance(BaseModel):
    """
    Model to track performance by timeframe
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timeframe = models.CharField(
        max_length=5,
        choices=Timeframe.choices
    )
    accuracy = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    sample_size = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)
    loss_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'timeframe')
    
    def __str__(self):
        return f"{self.timeframe} - {self.accuracy}%"


class PairPerformance(BaseModel):
    """
    Model to track performance by currency pair
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    sample_size = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)
    loss_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'pair')
    
    def __str__(self):
        return f"{self.pair.name} - {self.accuracy}%"


class RiskAnalysis(BaseModel):
    """
    Model to track risk metrics for a user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Risk metrics
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    avg_risk_reward = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 1:2.5
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    profit_factor = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 2.1
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    avg_win_size = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    avg_loss_size = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk Analysis for {self.user.email}"
