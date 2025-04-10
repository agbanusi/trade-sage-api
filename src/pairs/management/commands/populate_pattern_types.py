import logging
from django.core.management.base import BaseCommand
from pairs.models import PatternType, PatternCategory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate the database with available chart pattern types'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Only populate patterns from a specific category (technical, harmonic, candlestick)'
        )
    
    def handle(self, *args, **options):
        category = options.get('category')
        
        # Define patterns by category
        all_patterns = {
            PatternCategory.TECHNICAL: [
                # Bullish Technical Patterns
                {"name": "Double Bottom", "is_bullish": True, 
                 "description": "Double bottom pattern detected at support level, indicating a potential reversal of the previous downtrend. Second bottom formed with higher volume, confirming the pattern."},
                {"name": "Ascending Triangle", "is_bullish": True, 
                 "description": "Ascending triangle detected with resistance at a specific level and rising support trendline. Price consolidation with higher lows suggests bullish pressure building for a potential breakout."},
                {"name": "Cup and Handle", "is_bullish": True, 
                 "description": "Cup and handle pattern formed with a rounded bottom followed by a smaller handle pullback, suggesting a potential bullish continuation."},
                {"name": "Inverse Head and Shoulders", "is_bullish": True, 
                 "description": "Inverse head and shoulders pattern detected with neckline resistance, indicating a potential reversal from bearish to bullish trend."},
                {"name": "Bull Flag", "is_bullish": True, 
                 "description": "Bull flag pattern detected with a strong upward move followed by a consolidation period, suggesting a potential continuation of the uptrend."},
                {"name": "Bullish Rectangle", "is_bullish": True, 
                 "description": "Rectangle pattern formed between support and resistance levels with price expected to break to the upside."},
                {"name": "Rounding Bottom", "is_bullish": True, 
                 "description": "Rounding bottom (saucer) pattern detected, showing a gradual shift from downtrend to uptrend."},
                
                # Bearish Technical Patterns
                {"name": "Double Top", "is_bullish": False, 
                 "description": "Double top pattern detected at resistance level, indicating a potential reversal of the previous uptrend. Second top formed with lower volume, confirming the pattern."},
                {"name": "Descending Triangle", "is_bullish": False, 
                 "description": "Descending triangle detected with support at a specific level and falling resistance trendline. Price consolidation with lower highs suggests bearish pressure building for a potential breakdown."},
                {"name": "Head and Shoulders", "is_bullish": False, 
                 "description": "Head and shoulders pattern detected with neckline support, indicating a potential reversal from bullish to bearish trend."},
                {"name": "Bear Flag", "is_bullish": False, 
                 "description": "Bear flag pattern detected with a strong downward move followed by a consolidation period, suggesting a potential continuation of the downtrend."},
                {"name": "Bearish Rectangle", "is_bullish": False, 
                 "description": "Rectangle pattern formed between support and resistance levels with price expected to break to the downside."},
                {"name": "Rising Wedge", "is_bullish": False, 
                 "description": "Rising wedge pattern detected with converging trendlines, typically a bearish reversal or continuation pattern."},
                {"name": "Falling Wedge", "is_bullish": True, 
                 "description": "Falling wedge pattern detected with converging trendlines, typically a bullish reversal or continuation pattern."},
                {"name": "Triple Top", "is_bullish": False, 
                 "description": "Triple top pattern detected with three peaks at resistance, indicating strong selling pressure."},
                {"name": "Triple Bottom", "is_bullish": True, 
                 "description": "Triple bottom pattern detected with three troughs at support, indicating strong buying pressure."},
            ],
            
            PatternCategory.HARMONIC: [
                # Bullish Harmonic Patterns
                {"name": "Bullish Gartley", "is_bullish": True, 
                 "description": "Bullish Gartley pattern detected with Fibonacci retracements at key levels. The pattern suggests a potential reversal to the upside."},
                {"name": "Bullish Butterfly", "is_bullish": True, 
                 "description": "Bullish Butterfly pattern detected with precise Fibonacci measurements. Potential reversal zone identified at point D."},
                {"name": "Bullish Bat", "is_bullish": True, 
                 "description": "Bullish Bat pattern detected with specific Fibonacci ratios. Look for buying opportunities near the completion of point D."},
                {"name": "Bullish Crab", "is_bullish": True, 
                 "description": "Bullish Crab pattern detected with extreme extension at point D (1.618 of XA). Offers potentially high reward-to-risk entry."},
                {"name": "Bullish Cypher", "is_bullish": True, 
                 "description": "Bullish Cypher pattern detected with specific Fibonacci relationships. Potential buying opportunity at point D."},
                
                # Bearish Harmonic Patterns
                {"name": "Bearish Gartley", "is_bullish": False, 
                 "description": "Bearish Gartley pattern detected with Fibonacci retracements at key levels. The pattern suggests a potential reversal to the downside."},
                {"name": "Bearish Butterfly", "is_bullish": False, 
                 "description": "Bearish Butterfly pattern detected with precise Fibonacci measurements. Potential reversal zone identified at point D."},
                {"name": "Bearish Bat", "is_bullish": False, 
                 "description": "Bearish Bat pattern detected with specific Fibonacci ratios. Look for selling opportunities near the completion of point D."},
                {"name": "Bearish Crab", "is_bullish": False, 
                 "description": "Bearish Crab pattern detected with extreme extension at point D (1.618 of XA). Offers potentially high reward-to-risk entry."},
                {"name": "Bearish Cypher", "is_bullish": False, 
                 "description": "Bearish Cypher pattern detected with specific Fibonacci relationships. Potential selling opportunity at point D."},
            ],
            
            PatternCategory.CANDLESTICK: [
                # Bullish Candlestick Patterns
                {"name": "Bullish Engulfing", "is_bullish": True, 
                 "description": "A bullish engulfing pattern has formed, with the current candle completely engulfing the previous bearish candle, indicating strong buying pressure after a downtrend."},
                {"name": "Hammer", "is_bullish": True, 
                 "description": "Single candle with a small body and long lower shadow, showing rejection of lower prices and potential bullish reversal."},
                {"name": "Morning Star", "is_bullish": True, 
                 "description": "Three-candle pattern with a bearish candle, followed by a small-bodied middle candle and a strong bullish candle, indicating a potential bottom."},
                {"name": "Piercing Line", "is_bullish": True, 
                 "description": "Two-candle pattern where a bearish candle is followed by a bullish candle that closes above the midpoint of the previous candle."},
                {"name": "Bullish Harami", "is_bullish": True, 
                 "description": "Two-candle pattern where a large bearish candle is followed by a smaller bullish candle contained within the previous candle's range."},
                {"name": "Three White Soldiers", "is_bullish": True, 
                 "description": "Three consecutive bullish candles with higher closes, indicating strong buying pressure."},
                {"name": "Shooting Star", "is_bullish": False, 
                 "description": "Single candle with a small body at the bottom and a long upper shadow, indicating rejection of higher prices and potential bearish reversal."},
                
                # Bearish Candlestick Patterns
                {"name": "Bearish Engulfing", "is_bullish": False, 
                 "description": "A bearish engulfing pattern has formed, with the current candle completely engulfing the previous bullish candle, indicating strong selling pressure after an uptrend."},
                {"name": "Hanging Man", "is_bullish": False, 
                 "description": "Single candle with a small body at the top and a long lower shadow appearing in an uptrend, signaling potential reversal."},
                {"name": "Evening Star", "is_bullish": False, 
                 "description": "Three-candle pattern with a small-bodied middle candle followed by a strong bearish candle, indicating exhaustion of the uptrend."},
                {"name": "Dark Cloud Cover", "is_bullish": False, 
                 "description": "Two-candle pattern where a bullish candle is followed by a bearish candle that closes below the midpoint of the previous candle."},
                {"name": "Bearish Harami", "is_bullish": False, 
                 "description": "Two-candle pattern where a large bullish candle is followed by a smaller bearish candle contained within the previous candle's range."},
                {"name": "Three Black Crows", "is_bullish": False, 
                 "description": "Three consecutive bearish candles with lower closes, indicating strong selling pressure."},
                {"name": "Doji", "is_bullish": None, 
                 "description": "Candle with very small or no body, indicating indecision in the market. Can signal potential reversal depending on context."},
            ],
        }
        
        # Determine which patterns to process
        patterns_to_process = []
        if category:
            category_upper = category.upper()
            if category_upper in [cat.value for cat in PatternCategory]:
                patterns_to_process = all_patterns[category_upper]
                self.stdout.write(f"Processing {len(patterns_to_process)} patterns in category: {category}")
            else:
                self.stderr.write(f"Category '{category}' not found. Available categories: technical, harmonic, candlestick")
                return
        else:
            # Process all patterns from all categories
            for category_patterns in all_patterns.values():
                patterns_to_process.extend(category_patterns)
            self.stdout.write(f"Processing {len(patterns_to_process)} patterns across all categories")
        
        created_count = 0
        updated_count = 0
        
        for pattern_data in patterns_to_process:
            for category_key, category_patterns in all_patterns.items():
                if pattern_data in category_patterns:
                    pattern_category = category_key
                    break
            
            try:
                obj, created = PatternType.objects.update_or_create(
                    name=pattern_data["name"],
                    category=pattern_category,
                    defaults={
                        "description": pattern_data["description"],
                        "is_bullish": pattern_data.get("is_bullish", True),
                        "is_active": True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created pattern type: {obj}")
                else:
                    updated_count += 1
                    self.stdout.write(f"Updated pattern type: {obj}")
            except Exception as e:
                self.stderr.write(f"Error creating pattern {pattern_data['name']}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed pattern types. Created: {created_count}, Updated: {updated_count}"
        )) 