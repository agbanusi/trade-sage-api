import logging
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from .models import TradingPair, Signal, SignalType, WeightedInstrument

logger = logging.getLogger(__name__)


class TradingDecisionService:
    """
    Service to make trading decisions based on various weighted instruments.
    """
    
    def __init__(self, pair, user=None):
        """
        Initialize the service with a trading pair and user.
        
        Args:
            pair: TradingPair instance
            user: User instance (optional)
        """
        self.pair = pair
        self.user = user
        
    def generate_signal(self, price, strategy="default"):
        """
        Generate a trading signal for the pair based on weighted instruments.
        
        Args:
            price: Current price
            strategy: Name of the strategy to use (ignored if weighted instruments are used)
            
        Returns:
            Signal: The generated signal
        """
        # If user is provided, use their weighted instruments
        if self.user:
            return self._weighted_instruments_strategy(price)
        # Fallback to default strategy
        else:
            return self._default_strategy(price)
    
    def _weighted_instruments_strategy(self, price):
        """
        Generate a signal using weighted instruments for the user.
        
        Args:
            price: Current price
            
        Returns:
            Signal: The generated signal
        """
        # Get the user's weighted instruments for this pair
        weighted_instruments = WeightedInstrument.objects.filter(
            user=self.user,
            pair=self.pair
        ).select_related('instrument')
        
        # If no weighted instruments, use default strategy
        if not weighted_instruments.exists():
            logger.warning(f"No weighted instruments for user {self.user.email} and pair {self.pair.name}")
            return self._default_strategy(price)
        
        # Calculate weighted signal
        buy_score = Decimal('0')
        sell_score = Decimal('0')
        hold_score = Decimal('0')
        
        # In a real implementation, you would calculate a score for each instrument
        # Here we're using a simplified example for different indicators
        for wi in weighted_instruments:
            # Get normalized weight (0-1)
            weight_decimal = Decimal(str(wi.weight / 100))
            instrument_name = wi.instrument.name.lower()
            
            # Get signal based on instrument type
            instrument_buy, instrument_sell, instrument_hold = self._get_instrument_signals(
                instrument_name, price
            )
            
            # Add weighted scores
            buy_score += weight_decimal * instrument_buy
            sell_score += weight_decimal * instrument_sell
            hold_score += weight_decimal * instrument_hold
        
        # Determine signal type based on scores
        if buy_score > sell_score and buy_score > hold_score:
            signal_type = SignalType.BUY
            confidence = buy_score
        elif sell_score > buy_score and sell_score > hold_score:
            signal_type = SignalType.SELL
            confidence = sell_score
        else:
            signal_type = SignalType.HOLD
            confidence = hold_score
        
        # Calculate trade parameters
        entry_price, stop_loss, take_profit, potential_gain, risk_reward = self._calculate_trade_parameters(
            price, signal_type, confidence
        )
        
        # Create and return the signal
        signal = Signal.objects.create(
            user=self.user,
            pair=self.pair,
            signal_type=signal_type,
            price=price,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            potential_gain=potential_gain,
            risk_reward_ratio=risk_reward,
            confidence=confidence * Decimal('100')  # Scale to 0-100
        )
        
        logger.info(f"Generated {signal_type} signal for {self.pair.name} at price {price}")
        return signal
    
    def _get_instrument_signals(self, instrument_name, price):
        """
        Get buy/sell/hold signals for a specific instrument.
        In a real implementation, this would calculate actual technical indicators.
        
        Args:
            instrument_name: Name of the instrument (lowercase)
            price: Current price
            
        Returns:
            tuple: (buy_score, sell_score, hold_score) each from 0-1
        """
        # In a real implementation, you would:
        # 1. Fetch historical price data for the pair
        # 2. Calculate the actual technical indicator
        # 3. Generate signals based on the indicator values
        
        # For demonstration purposes, we're using simplified logic
        # based on the instrument name
        
        # RSI - Relative Strength Index
        if "rsi" in instrument_name:
            # Simulate RSI being oversold (suggesting buy)
            return Decimal('0.8'), Decimal('0.1'), Decimal('0.1')
            
        # MACD - Moving Average Convergence Divergence
        elif "macd" in instrument_name:
            # Simulate MACD crossing below signal line (suggesting sell)
            return Decimal('0.2'), Decimal('0.7'), Decimal('0.1')
            
        # EMA - Exponential Moving Average
        elif "ema" in instrument_name:
            # Simulate price above EMA (suggesting buy)
            return Decimal('0.7'), Decimal('0.2'), Decimal('0.1')
            
        # SMA - Simple Moving Average
        elif "sma" in instrument_name:
            # Simulate price crossing below SMA (suggesting sell)
            return Decimal('0.3'), Decimal('0.6'), Decimal('0.1')
            
        # Bollinger Bands
        elif "bollinger" in instrument_name:
            # Simulate price touching lower band (suggesting buy)
            return Decimal('0.75'), Decimal('0.15'), Decimal('0.1')
            
        # Ichimoku Cloud
        elif "ichimoku" in instrument_name:
            # Simulate price above the cloud (suggesting buy)
            return Decimal('0.6'), Decimal('0.3'), Decimal('0.1')
            
        # Stochastic Oscillator
        elif "stochastic" in instrument_name:
            # Simulate stochastic in overbought territory (suggesting sell)
            return Decimal('0.2'), Decimal('0.7'), Decimal('0.1')
            
        # Fibonacci Retracement
        elif "fibonacci" in instrument_name:
            # Simulate price at a strong Fibonacci support level (suggesting buy)
            return Decimal('0.65'), Decimal('0.25'), Decimal('0.1')
            
        # ATR - Average True Range
        elif "atr" in instrument_name:
            # ATR doesn't provide directional signals by itself
            # Here we're simulating high volatility (suggesting hold)
            return Decimal('0.3'), Decimal('0.3'), Decimal('0.4')
            
        # Moving Average (general)
        elif "ma" in instrument_name or "average" in instrument_name:
            # Simulate price near moving average (suggesting hold)
            return Decimal('0.3'), Decimal('0.3'), Decimal('0.4')
            
        # Default for unrecognized instruments
        else:
            return Decimal('0.33'), Decimal('0.33'), Decimal('0.34')
    
    def _default_strategy(self, price):
        """
        Default simple strategy for generating signals when no weighted instruments are available.
        
        Args:
            price: Current price
            
        Returns:
            Signal: The generated signal
        """
        # Get the previous signals for the pair
        filter_kwargs = {'pair': self.pair}
        if self.user:
            filter_kwargs['user'] = self.user
            
        previous_signals = Signal.objects.filter(**filter_kwargs).order_by('-timestamp')[:5]
        
        # Simple placeholder logic
        if not previous_signals.exists():
            signal_type = SignalType.BUY
            confidence = Decimal('0.75')
        else:
            last_signal = previous_signals.first()
            
            # Simple alternating strategy for demonstration
            if last_signal.signal_type == SignalType.BUY:
                signal_type = SignalType.SELL
                confidence = Decimal('0.70')
            else:
                signal_type = SignalType.BUY
                confidence = Decimal('0.70')
                
        # Calculate trade parameters
        entry_price, stop_loss, take_profit, potential_gain, risk_reward = self._calculate_trade_parameters(
            price, signal_type, confidence
        )
        
        # Create and return the signal
        signal = Signal.objects.create(
            user=self.user,
            pair=self.pair,
            signal_type=signal_type,
            price=price,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            potential_gain=potential_gain,
            risk_reward_ratio=risk_reward,
            confidence=confidence * Decimal('100')  # Scale to 0-100
        )
        
        logger.info(f"Generated {signal_type} signal for {self.pair.name} at price {price}")
        return signal
    
    def _calculate_trade_parameters(self, current_price, signal_type, confidence):
        """
        Calculate trade parameters (entry, stop loss, take profit, etc.)
        
        Args:
            current_price: Current market price
            signal_type: Type of signal (BUY/SELL/HOLD)
            confidence: Confidence score (0-1)
            
        Returns:
            tuple: (entry_price, stop_loss, take_profit, potential_gain, risk_reward_ratio)
        """
        current_price = Decimal(str(current_price))
        
        # For HOLD signals, we don't calculate trade parameters
        if signal_type == SignalType.HOLD:
            return None, None, None, None, None
            
        # Calculate entry price (slightly different from current for realism)
        if signal_type == SignalType.BUY:
            # Buy slightly above current price
            entry_price = current_price * Decimal('1.001')
            
            # Stop loss 2-5% below entry, depending on confidence
            stop_loss_percent = Decimal('0.05') - (confidence * Decimal('0.03'))
            stop_loss = entry_price * (Decimal('1') - stop_loss_percent)
            
            # Take profit 5-15% above entry, depending on confidence
            take_profit_percent = Decimal('0.05') + (confidence * Decimal('0.10'))
            take_profit = entry_price * (Decimal('1') + take_profit_percent)
            
            potential_gain = take_profit_percent * Decimal('100')
            
        else:  # SELL
            # Sell slightly below current price
            entry_price = current_price * Decimal('0.999')
            
            # Stop loss 2-5% above entry, depending on confidence
            stop_loss_percent = Decimal('0.05') - (confidence * Decimal('0.03'))
            stop_loss = entry_price * (Decimal('1') + stop_loss_percent)
            
            # Take profit 5-15% below entry, depending on confidence
            take_profit_percent = Decimal('0.05') + (confidence * Decimal('0.10'))
            take_profit = entry_price * (Decimal('1') - take_profit_percent)
            
            potential_gain = take_profit_percent * Decimal('100')
            
        # Calculate risk-to-reward ratio
        if signal_type == SignalType.BUY:
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:  # SELL
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
            
        # Avoid division by zero
        if risk > Decimal('0'):
            risk_reward_ratio = reward / risk
        else:
            risk_reward_ratio = Decimal('0')
            
        return entry_price, stop_loss, take_profit, potential_gain, risk_reward_ratio
    
    def execute_signal(self, signal):
        """
        Execute a trading signal.
        This is a placeholder implementation.
        
        Args:
            signal: Signal to execute
            
        Returns:
            bool: True if executed successfully, False otherwise
        """
        # In a real implementation, this would connect to a trading API
        # to execute the trade
        
        logger.info(f"Executing {signal.signal_type} signal for {signal.pair.name}")
        
        # Update the signal as executed
        signal.is_executed = True
        signal.execution_time = timezone.now()
        signal.save()
        
        return True 