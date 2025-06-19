import os
import json
import logging
from datetime import datetime
import tweepy
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError('Twitter API credentials not set in .env')
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        self.crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc', '#bitcoin', '#btc'],
            'ethereum': ['ethereum', 'eth', '#ethereum', '#eth'],
            'binancecoin': ['bnb', 'binance coin', '#bnb'],
            'ripple': ['ripple', 'xrp', '#ripple', '#xrp'],
            'cardano': ['cardano', 'ada', '#cardano', '#ada'],
            'dogecoin': ['dogecoin', 'doge', '#dogecoin', '#doge']
        }

    def collect_tweets(self, crypto_id, max_results=100):
        if crypto_id not in self.crypto_keywords:
            logger.error(f'Unknown cryptocurrency: {crypto_id}')
            return []
        query = ' OR '.join(self.crypto_keywords[crypto_id])
        tweets = []
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'lang', 'public_metrics']
            )
            if not response.data:
                logger.warning(f'No tweets found for {crypto_id}')
                return []
            for tweet in response.data:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'lang': tweet.lang,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'crypto_id': crypto_id
                }
                tweets.append(tweet_data)
            logger.info(f'Collected {len(tweets)} tweets for {crypto_id}')
            return tweets
        except Exception as e:
            logger.error(f'Error collecting tweets for {crypto_id}: {str(e)}')
            return []

    def save_tweets(self, tweets, crypto_id):
        if not tweets:
            logger.warning(f'No tweets to save for {crypto_id}')
            return
        os.makedirs('data/tweets', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/tweets/tweets_{crypto_id}_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        logger.info(f'Saved {len(tweets)} tweets to {filename}')

    def collect_all_tweets(self, max_results_per_crypto=100):
        for crypto_id in self.crypto_keywords:
            logger.info(f'Collecting tweets for {crypto_id}')
            tweets = self.collect_tweets(crypto_id, max_results_per_crypto)
            if tweets:
                self.save_tweets(tweets, crypto_id)

if __name__ == '__main__':
    collector = TwitterCollector()
    collector.collect_all_tweets() 