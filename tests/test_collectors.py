import pytest
import os
from src.data.twitter_collector import TwitterCollector
from src.data.reddit_collector import RedditCollector
from src.data.price_collector import PriceCollector

def test_twitter_collector_init():
    try:
        collector = TwitterCollector()
    except Exception:
        pytest.skip('Twitter API credentials not set')

def test_reddit_collector_init():
    try:
        collector = RedditCollector()
    except Exception:
        pytest.skip('Reddit API credentials not set')

def test_price_collector_current_prices():
    collector = PriceCollector()
    prices = collector.get_current_prices()
    assert isinstance(prices, dict)
    assert 'bitcoin' in prices 