import logging
from django.core.management.base import BaseCommand
from signals.models import TradingPair

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate the database with available trading pairs across various markets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Only populate pairs from a specific category (forex, crypto, indices, metals, energy)'
        )
    
    def handle(self, *args, **options):
        category = options.get('category')
        
        # Define all trading pairs by category
        all_pairs = {
            'forex': [
                # Main Pairs
                {"name": "EUR/USD", "base_asset": "EUR", "quote_asset": "USD"},
                {"name": "USD/JPY", "base_asset": "USD", "quote_asset": "JPY"},
                {"name": "GBP/USD", "base_asset": "GBP", "quote_asset": "USD"},
                {"name": "USD/CHF", "base_asset": "USD", "quote_asset": "CHF"},
                {"name": "AUD/USD", "base_asset": "AUD", "quote_asset": "USD"},
                {"name": "USD/CAD", "base_asset": "USD", "quote_asset": "CAD"},
                {"name": "NZD/USD", "base_asset": "NZD", "quote_asset": "USD"},
                {"name": "EUR/GBP", "base_asset": "EUR", "quote_asset": "GBP"},
                
                # Commodity Pairs
                {"name": "USD/NOK", "base_asset": "USD", "quote_asset": "NOK"},
                {"name": "USD/RUB", "base_asset": "USD", "quote_asset": "RUB"},
            ],
            'crypto': [
                {"name": "BTC/USD", "base_asset": "BTC", "quote_asset": "USD"},
                {"name": "ETH/USD", "base_asset": "ETH", "quote_asset": "USD"},
                {"name": "BTC/USDT", "base_asset": "BTC", "quote_asset": "USDT"},
                {"name": "ETH/USDT", "base_asset": "ETH", "quote_asset": "USDT"},
                {"name": "BNB/USDT", "base_asset": "BNB", "quote_asset": "USDT"},
                {"name": "XRP/USDT", "base_asset": "XRP", "quote_asset": "USDT"},
                {"name": "SOL/USDT", "base_asset": "SOL", "quote_asset": "USDT"},
                {"name": "ADA/USDT", "base_asset": "ADA", "quote_asset": "USDT"},
                {"name": "DOGE/USDT", "base_asset": "DOGE", "quote_asset": "USDT"},
                {"name": "LTC/USDT", "base_asset": "LTC", "quote_asset": "USDT"},
                {"name": "BTC-PERP", "base_asset": "BTC", "quote_asset": "PERP"},
                {"name": "ETH-PERP", "base_asset": "ETH", "quote_asset": "PERP"},
                {"name": "SOL-PERP", "base_asset": "SOL", "quote_asset": "PERP"},
            ],
            'indices': [
                {"name": "S&P500", "base_asset": "SPX", "quote_asset": "USD"},
                {"name": "NASDAQ100", "base_asset": "NDX", "quote_asset": "USD"},
                {"name": "DOW30", "base_asset": "DJI", "quote_asset": "USD"},
                {"name": "FTSE100", "base_asset": "UKX", "quote_asset": "GBP"},
                {"name": "DAX", "base_asset": "DAX", "quote_asset": "EUR"},
                {"name": "CAC40", "base_asset": "PX1", "quote_asset": "EUR"},
                {"name": "NIKKEI225", "base_asset": "NKY", "quote_asset": "JPY"},
                {"name": "HANGSENG", "base_asset": "HSI", "quote_asset": "HKD"},
                {"name": "SPY", "base_asset": "SPY", "quote_asset": "USD"},
                {"name": "QQQ", "base_asset": "QQQ", "quote_asset": "USD"},
                {"name": "VTI", "base_asset": "VTI", "quote_asset": "USD"},
            ],
            'metals': [
                {"name": "XAU/USD", "base_asset": "XAU", "quote_asset": "USD"},
                {"name": "XAG/USD", "base_asset": "XAG", "quote_asset": "USD"},
                {"name": "XPT/USD", "base_asset": "XPT", "quote_asset": "USD"},
                {"name": "XPD/USD", "base_asset": "XPD", "quote_asset": "USD"},
            ],
            'energy': [
                {"name": "WTI/USD", "base_asset": "WTI", "quote_asset": "USD"},
                {"name": "BRENT/USD", "base_asset": "BRENT", "quote_asset": "USD"},
                {"name": "NGAS/USD", "base_asset": "NGAS", "quote_asset": "USD"},
            ],
        }
        
        # Determine which pairs to process
        pairs_to_process = []
        if category:
            if category.lower() in all_pairs:
                pairs_to_process = all_pairs[category.lower()]
                self.stdout.write(f"Processing {len(pairs_to_process)} pairs in category: {category}")
            else:
                self.stderr.write(f"Category '{category}' not found. Available categories: {', '.join(all_pairs.keys())}")
                return
        else:
            # Process all pairs from all categories
            for cat_pairs in all_pairs.values():
                pairs_to_process.extend(cat_pairs)
            self.stdout.write(f"Processing {len(pairs_to_process)} pairs across all categories")
        
        created_count = 0
        updated_count = 0
        
        for pair_data in pairs_to_process:
            obj, created = TradingPair.objects.update_or_create(
                name=pair_data["name"],
                defaults={
                    "base_asset": pair_data["base_asset"],
                    "quote_asset": pair_data["quote_asset"],
                    "is_active": True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created trading pair: {obj.name}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated trading pair: {obj.name}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed trading pairs. Created: {created_count}, Updated: {updated_count}"
        )) 