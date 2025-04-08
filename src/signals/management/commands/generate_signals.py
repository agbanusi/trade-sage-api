import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from decimal import Decimal
from datetime import datetime
import random

from signals.models import TradingPair, WeightedInstrument, Signal
from signals.services import TradingDecisionService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate trading signals for all users with weighted instruments setup'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pair',
            type=str,
            help='Generate signals only for this trading pair (by name)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Generate signals only for this user (by email)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not save signals to database'
        )
    
    def handle(self, *args, **options):
        pair_name = options.get('pair')
        user_email = options.get('user')
        dry_run = options.get('dry_run')
        
        # Get relevant trading pairs
        if pair_name:
            try:
                pairs = [TradingPair.objects.get(name=pair_name)]
                self.stdout.write(f"Processing single pair: {pair_name}")
            except TradingPair.DoesNotExist:
                self.stderr.write(f"Trading pair '{pair_name}' not found")
                return
        else:
            # Only get active pairs that have at least one weighted instrument
            pairs = TradingPair.objects.filter(
                is_active=True,
                weighted_instruments__isnull=False
            ).distinct()
            self.stdout.write(f"Processing {pairs.count()} trading pairs")
        
        # Get relevant users
        if user_email:
            try:
                users = [User.objects.get(email=user_email)]
                self.stdout.write(f"Processing single user: {user_email}")
            except User.DoesNotExist:
                self.stderr.write(f"User '{user_email}' not found")
                return
        else:
            # Only get users that have at least one weighted instrument
            users = User.objects.filter(
                weighted_instruments__isnull=False
            ).distinct()
            self.stdout.write(f"Processing {users.count()} users")
        
        # Track statistics
        signals_generated = 0
        
        # Process each pair and user combination
        for pair in pairs:
            # Simulate current market price (in a real system, fetch from API)
            # For example purposes, we generate a random price between 10 and 50000
            current_price = Decimal(str(random.uniform(10, 50000)))
            self.stdout.write(f"Current price for {pair.name}: {current_price}")
            
            for user in users:
                # Check if this user has weighted instruments for this pair
                weighted_instruments = WeightedInstrument.objects.filter(
                    user=user,
                    pair=pair
                )
                
                if not weighted_instruments.exists():
                    continue
                
                # Process the signal
                service = TradingDecisionService(pair, user)
                
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would generate signal for {user.email} on {pair.name}")
                else:
                    try:
                        signal = service.generate_signal(current_price)
                        signals_generated += 1
                        self.stdout.write(
                            f"Generated {signal.signal_type} signal for {user.email} on {pair.name} "
                            f"(entry: {signal.entry_price}, SL: {signal.stop_loss}, TP: {signal.take_profit}, "
                            f"RR: {signal.risk_reward_ratio})"
                        )
                    except Exception as e:
                        self.stderr.write(f"Error generating signal for {user.email} on {pair.name}: {str(e)}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write(self.style.SUCCESS(
            f"[{timestamp}] Signal generation complete. Generated {signals_generated} signals."
        )) 