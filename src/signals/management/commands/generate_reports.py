import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from signals.models import TradingPair, Signal, SignalReport, SignalType

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate hourly reports for all signals'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours-ago',
            type=int,
            default=1,
            help='Generate report for signals from this many hours ago'
        )
        parser.add_argument(
            '--pair',
            type=str,
            help='Generate report only for this trading pair (by name)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Generate report only for this user (by email)'
        )
    
    def handle(self, *args, **options):
        hours_ago = options.get('hours_ago')
        pair_name = options.get('pair')
        user_email = options.get('user')
        
        # Calculate the time range
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours_ago)
        
        self.stdout.write(f"Generating reports for signals between {start_time} and {end_time}")
        
        # Filter pairs and users if specified
        pair_filter = Q()
        if pair_name:
            try:
                pair = TradingPair.objects.get(name=pair_name)
                pair_filter = Q(pair=pair)
                self.stdout.write(f"Filtering by pair: {pair_name}")
            except TradingPair.DoesNotExist:
                self.stderr.write(f"Trading pair '{pair_name}' not found")
                return
                
        user_filter = Q()
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                user_filter = Q(user=user)
                self.stdout.write(f"Filtering by user: {user_email}")
            except User.DoesNotExist:
                self.stderr.write(f"User '{user_email}' not found")
                return
        
        # Start by getting all relevant signals
        signals = Signal.objects.filter(
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).filter(pair_filter).filter(user_filter)
        
        if not signals.exists():
            self.stdout.write(self.style.WARNING(
                f"No signals found in the specified time range and filters."
            ))
            return
            
        self.stdout.write(f"Found {signals.count()} signals to analyze")
        
        # Get unique pairs and users in the signals
        pairs = TradingPair.objects.filter(signals__in=signals).distinct()
        users = User.objects.filter(signals__in=signals).distinct()
        
        reports_created = 0
        
        # Generate per-user, per-pair reports
        for user in users:
            for pair in pairs:
                user_pair_signals = signals.filter(user=user, pair=pair)
                
                if not user_pair_signals.exists():
                    continue
                    
                # Count signal types
                buy_count = user_pair_signals.filter(signal_type=SignalType.BUY).count()
                sell_count = user_pair_signals.filter(signal_type=SignalType.SELL).count()
                hold_count = user_pair_signals.filter(signal_type=SignalType.HOLD).count()
                
                # Calculate averages (excluding None values)
                avg_confidence = user_pair_signals.aggregate(avg=Avg('confidence'))['avg'] or Decimal('0')
                
                non_hold_signals = user_pair_signals.exclude(signal_type=SignalType.HOLD)
                avg_risk_reward = None
                if non_hold_signals.exists():
                    # Calculate average risk/reward excluding None values
                    avg_risk_reward = non_hold_signals.exclude(
                        risk_reward_ratio__isnull=True
                    ).aggregate(avg=Avg('risk_reward_ratio'))['avg']
                
                # Get the latest price for this pair
                latest_price = user_pair_signals.latest('timestamp').price
                
                # Additional data to store
                data = {
                    "executed_count": user_pair_signals.filter(is_executed=True).count(),
                    "total_signals": user_pair_signals.count(),
                    "report_period_hours": hours_ago,
                }
                
                # Create the report
                report = SignalReport.objects.create(
                    timestamp=end_time,
                    pair=pair,
                    user=user,
                    price=latest_price,
                    buy_signals=buy_count,
                    sell_signals=sell_count,
                    hold_signals=hold_count,
                    avg_confidence=avg_confidence,
                    avg_risk_reward=avg_risk_reward,
                    data=data
                )
                reports_created += 1
                
                self.stdout.write(
                    f"Created report for {user.email} on {pair.name}: "
                    f"BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}, "
                    f"Avg Confidence={avg_confidence:.2f}"
                )
        
        # Also create pair-level reports (aggregated across users)
        for pair in pairs:
            pair_signals = signals.filter(pair=pair)
            
            # Count signal types
            buy_count = pair_signals.filter(signal_type=SignalType.BUY).count()
            sell_count = pair_signals.filter(signal_type=SignalType.SELL).count()
            hold_count = pair_signals.filter(signal_type=SignalType.HOLD).count()
            
            # Calculate averages
            avg_confidence = pair_signals.aggregate(avg=Avg('confidence'))['avg'] or Decimal('0')
            
            non_hold_signals = pair_signals.exclude(signal_type=SignalType.HOLD)
            avg_risk_reward = None
            if non_hold_signals.exists():
                avg_risk_reward = non_hold_signals.exclude(
                    risk_reward_ratio__isnull=True
                ).aggregate(avg=Avg('risk_reward_ratio'))['avg']
            
            # Get the latest price for this pair
            latest_price = pair_signals.latest('timestamp').price
            
            # Additional data to store
            user_count = User.objects.filter(signals__in=pair_signals).distinct().count()
            data = {
                "executed_count": pair_signals.filter(is_executed=True).count(),
                "total_signals": pair_signals.count(),
                "report_period_hours": hours_ago,
                "user_count": user_count,
            }
            
            # Create the pair-level report (no user assigned)
            report = SignalReport.objects.create(
                timestamp=end_time,
                pair=pair,
                user=None,  # No user for pair-level report
                price=latest_price,
                buy_signals=buy_count,
                sell_signals=sell_count,
                hold_signals=hold_count,
                avg_confidence=avg_confidence,
                avg_risk_reward=avg_risk_reward,
                data=data
            )
            reports_created += 1
            
            self.stdout.write(
                f"Created aggregate report for {pair.name}: "
                f"BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}, "
                f"Users={user_count}, Avg Confidence={avg_confidence:.2f}"
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"Report generation complete. Created {reports_created} reports."
        )) 