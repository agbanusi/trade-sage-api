import logging
from django.core.management.base import BaseCommand
from signals.models import Instrument

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate the database with available trading instruments/indicators'
    
    def handle(self, *args, **options):
        instruments = [
            {
                "name": "RSI",
                "description": "Relative Strength Index - Momentum oscillator that measures the speed and change of price movements on a scale from 0 to 100."
            },
            {
                "name": "MACD",
                "description": "Moving Average Convergence Divergence - Trend-following momentum indicator showing the relationship between two moving averages of a security's price."
            },
            {
                "name": "EMA",
                "description": "Exponential Moving Average - Moving average that places a greater weight on recent data points."
            },
            {
                "name": "SMA",
                "description": "Simple Moving Average - Arithmetic moving average calculated by adding recent prices and dividing by the number of periods."
            },
            {
                "name": "Bollinger Bands",
                "description": "Set of three lines: a simple moving average and two standard deviations, one above and one below, to predict upper and lower price volatility boundaries."
            },
            {
                "name": "Ichimoku Cloud",
                "description": "Technical indicator that defines support and resistance, identifies trend direction, and gauges momentum."
            },
            {
                "name": "Stochastic Oscillator",
                "description": "Momentum indicator comparing a closing price to its price range over a specific period, showing overbought/oversold conditions."
            },
            {
                "name": "Fibonacci Retracement",
                "description": "Uses horizontal lines to indicate areas of support or resistance at the key Fibonacci levels before the price continues in the original direction."
            },
            {
                "name": "ATR",
                "description": "Average True Range - Measures market volatility by decomposing the entire range of an asset price for a period."
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for instrument_data in instruments:
            obj, created = Instrument.objects.update_or_create(
                name=instrument_data["name"],
                defaults={"description": instrument_data["description"], "is_active": True}
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created instrument: {obj.name}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated instrument: {obj.name}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed instruments. Created: {created_count}, Updated: {updated_count}"
        )) 