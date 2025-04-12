from django.core.management.base import BaseCommand
from chart_analysis.models import Pair


class Command(BaseCommand):
    help = 'Loads initial trading pairs data'

    def handle(self, *args, **options):
        # Define common trading pairs
        pairs = [
            {
                'name': 'EUR/USD',
                'display_name': 'Euro / U.S. Dollar',
                'is_active': True
            },
            {
                'name': 'USD/JPY',
                'display_name': 'U.S. Dollar / Japanese Yen',
                'is_active': True
            },
            {
                'name': 'GBP/USD',
                'display_name': 'British Pound / U.S. Dollar',
                'is_active': True
            },
            {
                'name': 'USD/CHF',
                'display_name': 'U.S. Dollar / Swiss Franc',
                'is_active': True
            },
            {
                'name': 'USD/CAD',
                'display_name': 'U.S. Dollar / Canadian Dollar',
                'is_active': True
            },
            {
                'name': 'AUD/USD',
                'display_name': 'Australian Dollar / U.S. Dollar',
                'is_active': True
            },
            {
                'name': 'NZD/USD',
                'display_name': 'New Zealand Dollar / U.S. Dollar',
                'is_active': True
            },
            {
                'name': 'BTC/USD',
                'display_name': 'Bitcoin / U.S. Dollar',
                'is_active': True
            },
            {
                'name': 'ETH/USD',
                'display_name': 'Ethereum / U.S. Dollar',
                'is_active': True
            },
        ]
        
        # Create pairs if they don't exist
        for pair_data in pairs:
            pair, created = Pair.objects.get_or_create(
                name=pair_data['name'],
                defaults={
                    'display_name': pair_data['display_name'],
                    'is_active': pair_data['is_active']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created pair: {pair.name}'))
            else:
                self.stdout.write(f'Pair already exists: {pair.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial pairs data')) 