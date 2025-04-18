# Trade Sage Backend API

## Overview

Trade Sage is an advanced trading analysis platform designed to help traders identify entry and exit points, receive AI-powered insights, and analyze market conditions. This backend provides a robust REST API that powers the Trade Sage application with features including technical analysis, trading signals, pattern recognition, economic calendar data, market sentiment analysis, and personalized trading setups.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Core API](#core-api)
  - [Signals API](#signals-api)
  - [Insights API](#insights-api)
  - [Calendar API](#calendar-api)
  - [Setups API](#setups-api)
  - [Notifications API](#notifications-api)
  - [Dashboard API](#dashboard-api)
- [External Integrations](#external-integrations)
- [Development](#development)

## Features

### Core Trading Features

- **Trading Pairs Management**: Track and analyze numerous forex trading pairs
- **User Accounts & Profiles**: Personalized trading preferences and settings
- **Trade Management**: Record and analyze trading history

### Technical Analysis

- **Customizable Indicator Sets**: Create sets of weighted technical indicators for signal generation
- **Backtesting Engine**: Test indicator performance on historical data
- **Performance Analytics**: Win rate, profit factor, Sharpe ratio, and other metrics

### Pattern Recognition

- **Chart Pattern Detection**: Identify key patterns like Head & Shoulders, Double Tops/Bottoms, etc.
- **Candlestick Patterns**: Recognize and interpret candlestick formations
- **Trend Analysis**: Automated trend identification and analysis

### AI-Powered Insights

- **Trading Recommendations**: AI-generated entry/exit points with confidence scores
- **Risk Assessment**: Stop loss and take profit recommendations with risk/reward analysis
- **Market Analysis**: Contextual analysis of market conditions

### Market Sentiment Analysis

- **News Sentiment**: Analysis of financial news coverage for trading pairs
- **Social Media Sentiment**: Monitoring of social media sentiment indicators
- **Institutional Positioning**: Tracking of institutional investment positions
- **Composite Sentiment**: Combined sentiment scores from multiple sources

### Economic Calendar

- **Economic Events Tracking**: Comprehensive calendar of market-moving economic releases
- **Impact Analysis**: Rating system for event impact on specific currency pairs
- **Customizable Alerts**: User-defined notification settings for important events

### Trading Setups

- **Custom Setup Creation**: Save personal trading strategies and setups
- **Setup Sharing**: Community sharing of successful trading approaches
- **Setup Categorization**: Organization by pattern type, timeframe, and strategy

### Notifications System

- **Signal Alerts**: Notifications for new trading signals
- **Price Alerts**: Customizable price movement notifications
- **Economic Calendar Alerts**: Reminders for upcoming economic events
- **Multi-Channel Delivery**: Email and push notification support

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery task queue)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/trade_sage_backend.git
cd trade_sage_backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
# Database configuration
export DATABASE_URL=postgres://username:password@localhost:5432/trade_sage
# API Keys
export ALPHA_VANTAGE_API_KEY=your_api_key
export NEWS_API_KEY=your_api_key
export TRADING_ECONOMICS_API_KEY=your_api_key
# Email settings
export EMAIL_HOST_USER=your_email@example.com
export EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

7. Start Celery worker (in a separate terminal):

```bash
celery -A trade_sage_backend worker -l INFO
```

## API Documentation

### Authentication

Trade Sage uses token-based authentication.

#### Get Authentication Token

```
POST /api/token/
```

**Request Body:**

```json
{
  "username": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

For all subsequent requests, include the token in the Authorization header:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Core API

#### Trading Pairs

```
GET /api/core/trading-pairs/
```

Returns list of available trading pairs with current price information.

#### Trading Accounts

```
GET /api/core/trading-accounts/
POST /api/core/trading-accounts/
```

Manage user trading accounts.

#### Trades

```
GET /api/core/trades/
POST /api/core/trades/
GET /api/core/trades/{id}/
```

#### User Profile

```
GET /api/core/profile/
PUT /api/core/profile/
```

Manage user preferences including default trade size, risk settings, and UI preferences.

### Signals API

#### Trading Signals

```
GET /api/signals/trading-signals/
```

Get trading signals with filtering support for:

- `trading_pair`: Filter by trading pair code
- `timeframe`: Filter by timeframe
- `direction`: Filter by signal direction (BUY/SELL/NEUTRAL)
- `min_confidence`: Minimum confidence score
- `created_after`: Signals created after specified date

#### Indicator Sets

```
GET /api/signals/indicator-sets/
POST /api/signals/indicator-sets/
```

Manage custom indicator sets with weighted technical indicators.

```
GET /api/signals/indicator-sets/{id}/backtest/
```

Run backtests on indicator sets with parameters:

- `trading_pair`: Trading pair code
- `timeframe`: Timeframe for backtesting
- `start_date`: Start date for backtest period (YYYY-MM-DD)
- `end_date`: End date for backtest period (YYYY-MM-DD)

### Insights API

#### Trading Insights

```
GET /api/insights/trading-insights/
GET /api/insights/trading-insights/{id}/
```

Get AI-generated trading insights with filtering support.

```
POST /api/insights/trading-insights/generate/
```

Generate a new AI trading insight with parameters:

- `trading_pair`: Trading pair code
- `timeframe`: Timeframe for analysis

#### Pattern Recognition

```
GET /api/insights/patterns/
```

Get detected chart patterns with parameters:

- `trading_pair`: Trading pair code
- `timeframe`: Timeframe for analysis

#### Market Sentiment

```
GET /api/insights/sentiment/
```

Get market sentiment data with filtering support.

```
GET /api/insights/sentiment/by_source/
```

Get sentiment data grouped by source with parameter:

- `trading_pair`: Trading pair code

```
GET /api/insights/articles/
```

Get news articles with sentiment analysis.

```
GET /api/insights/institutional/
```

Get institutional positioning data.

### Calendar API

#### Economic Events

```
GET /api/calendar/events/
```

Get economic events with filtering support:

- `country`: Filter by country code
- `impact`: Filter by impact level (LOW/MEDIUM/HIGH)
- `start_date`: Start date for events (YYYY-MM-DD)
- `end_date`: End date for events (YYYY-MM-DD)

```
GET /api/calendar/events/upcoming/
```

Get upcoming economic events with parameters:

- `days`: Number of days to look ahead (default: 7)
- `impact`: Filter by impact level
- `country`: Filter by country code

```
POST /api/calendar/events/sync/
```

Manually trigger calendar synchronization (admin only).

### Setups API

#### Trading Setups

```
GET /api/setups/setups/
POST /api/setups/setups/
GET /api/setups/setups/{id}/
PUT /api/setups/setups/{id}/
DELETE /api/setups/setups/{id}/
```

Manage trading setups with filtering support:

- `trading_pair`: Filter by trading pair code
- `setup_type`: Filter by setup type
- `timeframe`: Filter by timeframe
- `is_public`: Filter by public status

```
GET /api/setups/setups/my_setups/
```

Get only the current user's setups.

```
GET /api/setups/setups/popular/
```

Get popular setups based on favorites count.

#### Setup Images

```
POST /api/setups/images/
```

Upload images for trading setups.

#### Setup Favorites

```
POST /api/setups/favorites/toggle/
```

Toggle favorite status for a setup.

### Notifications API

#### Notification Settings

```
GET /api/notifications/settings/
PUT /api/notifications/settings/
```

Manage notification preferences.

#### Price Alerts

```
GET /api/notifications/price-alerts/
POST /api/notifications/price-alerts/
GET /api/notifications/price-alerts/{id}/
PUT /api/notifications/price-alerts/{id}/
DELETE /api/notifications/price-alerts/{id}/
```

Manage price alerts with support for various condition types.

#### Notifications

```
GET /api/notifications/notifications/
GET /api/notifications/notifications/{id}/
```

Get user notifications.

```
POST /api/notifications/notifications/{id}/mark_read/
```

Mark a notification as read.

```
POST /api/notifications/notifications/mark_all_read/
```

Mark all notifications as read.

#### Device Tokens

```
POST /api/notifications/device-tokens/
```

Register a device for push notifications.

### Dashboard API

#### Dashboard Overview

```
GET /api/core/dashboard/
```

Get comprehensive dashboard data including:

- Top trading pairs
- Top gainers and losers
- Recent signals and insights
- Upcoming economic events
- Market sentiment overview
- Backtesting summary
- Saved setups

#### Pairs Performance

```
GET /api/core/performance/
```

Get performance metrics for trading pairs with parameters:

- `timeframe`: Filter by timeframe
- `days`: Analysis period in days (default: 30)
- `limit`: Number of pairs to return (default: 10)
- `sort_by`: Sort metric (return, win_rate, profit_factor)

## External Integrations

Trade Sage integrates with several external services:

### Market Data

- **Alpha Vantage API**: Historical and real-time forex data
- **Custom Mock Data**: Fallback data generation for development

### News and Sentiment

- **News API**: Financial news aggregation
- **Sentiment Analysis**: Custom NLP processing of news and social content

### Economic Calendar

- **Trading Economics API**: Economic event data
- **Custom Mock Calendar**: Fallback data generation for development

## Development

### Project Structure

```
trade_sage_backend/
├── trade_sage_backend/        # Project package
│   ├── core/                  # Core functionality
│   ├── signals/               # Trading signals
│   ├── insights/              # AI insights and analysis
│   ├── calendar/              # Economic calendar
│   ├── setups/                # Saved trading setups
│   ├── notifications/         # Notifications system
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL routing
│   ├── celery.py              # Celery configuration
│   └── wsgi.py                # WSGI configuration
├── manage.py                  # Django management script
└── requirements.txt           # Project dependencies
```

### Background Tasks

Trade Sage uses Celery for background tasks:

- Periodic backtesting of indicator sets
- Economic calendar synchronization
- Sentiment analysis updates
- Price alert monitoring
- Notification sending

### Adding New Features

1. Create models in the appropriate app
2. Implement serializers for API responses
3. Create views and register them with a router
4. Add URL patterns
5. Write tests for the new functionality

---

## License

This project is proprietary and confidential. All rights reserved.

---

For questions or support, contact: support@tradesage.com
