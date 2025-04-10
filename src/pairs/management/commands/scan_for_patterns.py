import logging
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from signals.models import TradingPair
from pairs.models import TimeFrame, PatternCategory
from pairs.services import PatternRecognitionService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scan for chart patterns on trading pairs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pair',
            type=str,
            help='Only scan a specific trading pair (by name)'
        )
        parser.add_argument(
            '--timeframe',
            type=str,
            help='Only scan a specific timeframe (e.g., 1h, 4h, 1d)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Only scan for a specific pattern category (technical, harmonic, candlestick)'
        )
    
    def handle(self, *args, **options):
        pair_name = options.get('pair')
        timeframe = options.get('timeframe')
        category = options.get('category')
        
        # Get pairs to scan
        if pair_name:
            try:
                pairs = [TradingPair.objects.get(name=pair_name)]
                self.stdout.write(f"Scanning single pair: {pair_name}")
            except TradingPair.DoesNotExist:
                self.stderr.write(f"Trading pair '{pair_name}' not found")
                return
        else:
            # Only get active pairs
            pairs = TradingPair.objects.filter(is_active=True)
            self.stdout.write(f"Scanning {pairs.count()} trading pairs")
        
        # Get timeframes to scan
        if timeframe:
            # Validate timeframe format
            valid_timeframes = [tf[0] for tf in TimeFrame.choices]
            if timeframe not in valid_timeframes:
                self.stderr.write(f"Invalid timeframe: {timeframe}. Valid timeframes: {', '.join(valid_timeframes)}")
                return
            timeframes = [timeframe]
        else:
            # Use common timeframes
            timeframes = [TimeFrame.H1, TimeFrame.H4, TimeFrame.D1]
        
        # Handle category filter
        if category:
            category = category.upper()
            if category not in [cat.value for cat in PatternCategory]:
                self.stderr.write(f"Invalid category: {category}. Valid categories: {', '.join([cat.value for cat in PatternCategory])}")
                return
        
        # Track statistics
        patterns_detected = 0
        pairs_processed = 0
        
        # Process each pair
        for pair in pairs:
            pairs_processed += 1
            
            # Process each timeframe
            for tf in timeframes:
                # Create pattern recognition service
                service = PatternRecognitionService(pair, tf)
                
                # Generate mock historical data for demonstration purposes
                # In a real implementation, this would fetch data from an API or database
                historical_data = self._generate_mock_data(pair.name)
                
                # Detect patterns
                if category:
                    # If category specified, only get patterns of that category
                    patterns = service.detect_patterns(historical_data)
                    patterns = [p for p in patterns if p.pattern_type.category == category]
                else:
                    patterns = service.detect_patterns(historical_data)
                
                # Save detected patterns
                saved_patterns = service.save_detected_patterns(patterns)
                patterns_detected += len(saved_patterns)
                
                self.stdout.write(f"Detected {len(saved_patterns)} patterns for {pair.name} on {tf} timeframe")
        
        self.stdout.write(self.style.SUCCESS(
            f"Pattern scan complete. Processed {pairs_processed} pairs and detected {patterns_detected} patterns."
        ))
    
    def _generate_mock_data(self, pair_name, candles=100):
        """
        Generate mock OHLCV data for testing pattern detection.
        
        Args:
            pair_name: Name of the pair to generate data for
            candles: Number of candles to generate
            
        Returns:
            list: List of dictionaries with OHLCV data
        """
        data = []
        
        # Generate mock price based on pair
        # For crypto: higher values, for forex: lower values
        if "BTC" in pair_name:
            base_price = 40000
            volatility = 1000
        elif "ETH" in pair_name:
            base_price = 2500
            volatility = 100
        elif "XAU" in pair_name:
            base_price = 2400
            volatility = 20
        elif "/" in pair_name:
            # Forex pair
            base_price = 1.1
            volatility = 0.01
        else:
            # Default
            base_price = 100
            volatility = 5
        
        # Generate price data with some randomness but also a trend
        current_price = base_price
        
        # Use a slight uptrend or downtrend
        trend = random.choice([-1, 1]) * volatility * 0.01
        
        for i in range(candles):
            # Add some randomness to the price
            price_change = random.uniform(-volatility, volatility) + trend
            current_price += price_change
            
            # Ensure price is positive
            current_price = max(current_price, volatility)
            
            # Generate OHLCV data
            candle = {
                'timestamp': (timezone.now() - timezone.timedelta(hours=candles-i)).isoformat(),
                'open': current_price - random.uniform(-volatility*0.5, volatility*0.5),
                'high': current_price + random.uniform(0, volatility),
                'low': current_price - random.uniform(0, volatility),
                'close': current_price,
                'volume': random.uniform(100, 1000)
            }
            
            # Ensure high >= open >= close >= low
            candle['high'] = max(candle['high'], candle['open'], candle['close'])
            candle['low'] = min(candle['low'], candle['open'], candle['close'])
            
            data.append(candle)
        
        return data 