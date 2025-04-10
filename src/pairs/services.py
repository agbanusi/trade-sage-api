import logging
from decimal import Decimal
from django.utils import timezone
from .models import PatternType, DetectedPattern, PatternCategory, PatternStatus, TimeFrame
from signals.models import TradingPair

logger = logging.getLogger(__name__)


class PatternRecognitionService:
    """
    Service to recognize and analyze chart patterns.
    """
    
    def __init__(self, pair, timeframe=TimeFrame.H1, user=None):
        """
        Initialize the service with a trading pair and timeframe.
        
        Args:
            pair: TradingPair instance
            timeframe: TimeFrame choice
            user: User instance (optional)
        """
        self.pair = pair
        self.timeframe = timeframe
        self.user = user
    
    def detect_patterns(self, historical_data, patterns_to_check=None):
        """
        Detect patterns in the provided historical data.
        
        Args:
            historical_data: List of OHLCV data points for the pair
            patterns_to_check: List of pattern names to check (optional)
            
        Returns:
            list: Detected patterns
        """
        detected_patterns = []
        
        # Get active pattern types to check
        if patterns_to_check:
            pattern_types = PatternType.objects.filter(
                name__in=patterns_to_check,
                is_active=True
            )
        else:
            pattern_types = PatternType.objects.filter(is_active=True)
            
        # Check each pattern type
        for pattern_type in pattern_types:
            # Call the appropriate detection method based on category
            if pattern_type.category == PatternCategory.TECHNICAL:
                pattern = self._detect_technical_pattern(historical_data, pattern_type)
            elif pattern_type.category == PatternCategory.HARMONIC:
                pattern = self._detect_harmonic_pattern(historical_data, pattern_type)
            elif pattern_type.category == PatternCategory.CANDLESTICK:
                pattern = self._detect_candlestick_pattern(historical_data, pattern_type)
            else:
                continue
                
            if pattern:
                detected_patterns.append(pattern)
                
        return detected_patterns
    
    def _detect_technical_pattern(self, data, pattern_type):
        """
        Detect technical patterns in historical data.
        
        Args:
            data: OHLCV data
            pattern_type: PatternType instance
            
        Returns:
            DetectedPattern or None
        """
        # In a real implementation, this would use complex algorithms to detect patterns
        # For demonstration purposes, we're using very simplified mock logic
        
        pattern_name = pattern_type.name.lower()
        
        # Get the last candle's close price
        current_price = Decimal(str(data[-1]['close']))
        
        # Calculate a mock confidence score (between 65 and 95)
        import random
        confidence = Decimal(str(random.uniform(65, 95)))
        
        # Create a basic description
        description = pattern_type.description
        
        # Generate mock entry zone, stop loss and target prices
        if pattern_type.is_bullish:
            # For bullish patterns
            entry_zone_low = current_price * Decimal('0.99')
            entry_zone_high = current_price * Decimal('1.01')
            stop_loss = entry_zone_low * Decimal('0.97')
            target_price = entry_zone_high * Decimal('1.05')
            secondary_target = target_price * Decimal('1.02')
        else:
            # For bearish patterns
            entry_zone_low = current_price * Decimal('0.99')
            entry_zone_high = current_price * Decimal('1.01')
            stop_loss = entry_zone_high * Decimal('1.03')
            target_price = entry_zone_low * Decimal('0.95')
            secondary_target = target_price * Decimal('0.98')
            
        # Calculate completion percentage based on confidence
        completion_percentage = confidence * Decimal('0.9')
            
        # Create a detected pattern
        pattern = DetectedPattern(
            pair=self.pair,
            pattern_type=pattern_type,
            user=self.user,
            timeframe=self.timeframe,
            status=PatternStatus.FORMING,
            confidence=confidence,
            price_at_detection=current_price,
            entry_zone_low=entry_zone_low,
            entry_zone_high=entry_zone_high,
            stop_loss=stop_loss,
            target_price=target_price,
            secondary_target=secondary_target,
            pattern_start_time=timezone.now() - timezone.timedelta(hours=24),
            description=description,
            completion_percentage=completion_percentage
        )
        
        return pattern
    
    def _detect_harmonic_pattern(self, data, pattern_type):
        """
        Detect harmonic patterns using Fibonacci ratios.
        
        Args:
            data: OHLCV data
            pattern_type: PatternType instance
            
        Returns:
            DetectedPattern or None
        """
        # Similar to technical patterns, but with additional Fibonacci ratio calculations
        pattern = self._detect_technical_pattern(data, pattern_type)
        
        if pattern:
            # Add harmonic-specific Fibonacci ratios
            pattern.ratios = {
                "XA/AB": "0.618",
                "BC/AB": "0.382",
                "CD/BC": "1.618",
                "AD/AB": "1.272"
            }
            
        return pattern
        
    def _detect_candlestick_pattern(self, data, pattern_type):
        """
        Detect candlestick patterns.
        
        Args:
            data: OHLCV data
            pattern_type: PatternType instance
            
        Returns:
            DetectedPattern or None
        """
        # Simple candlestick pattern detection
        # In a real implementation, this would check specific candlestick formations
        
        # For demo purposes, use similar logic to technical patterns
        pattern = self._detect_technical_pattern(data, pattern_type)
        
        # For candlestick patterns, we typically have higher confidence
        if pattern:
            # Increase confidence for candlestick patterns
            pattern.confidence = min(pattern.confidence * Decimal('1.1'), Decimal('95'))
            
        return pattern
    
    def save_detected_patterns(self, patterns):
        """
        Save a list of detected patterns to the database.
        
        Args:
            patterns: List of DetectedPattern instances
            
        Returns:
            list: Saved DetectedPattern instances
        """
        saved_patterns = []
        
        for pattern in patterns:
            try:
                pattern.save()
                saved_patterns.append(pattern)
                logger.info(f"Saved pattern: {pattern}")
            except Exception as e:
                logger.error(f"Error saving pattern: {str(e)}")
                
        return saved_patterns
    
    def update_pattern_status(self, pattern_id, new_status, completion_percentage=None):
        """
        Update the status of a detected pattern.
        
        Args:
            pattern_id: ID of the pattern to update
            new_status: New PatternStatus value
            completion_percentage: New completion percentage (optional)
            
        Returns:
            DetectedPattern: Updated pattern or None if not found
        """
        try:
            pattern = DetectedPattern.objects.get(id=pattern_id)
            
            # Update status
            pattern.status = new_status
            
            # Update completion time if moving to a final state
            if new_status in [PatternStatus.COMPLETE, PatternStatus.FAILED, PatternStatus.TARGET_HIT]:
                pattern.completion_time = timezone.now()
                
            # Update completion percentage if provided
            if completion_percentage is not None:
                pattern.completion_percentage = completion_percentage
                
            pattern.save()
            return pattern
        except DetectedPattern.DoesNotExist:
            logger.error(f"Pattern with ID {pattern_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error updating pattern status: {str(e)}")
            return None 