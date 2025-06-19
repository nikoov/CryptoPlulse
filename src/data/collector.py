import logging
from src.data.twitter_collector import TwitterCollector
from src.data.reddit_collector import RedditCollector
from src.data.price_collector import PriceCollector
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.twitter = TwitterCollector()
        self.reddit = RedditCollector()
        self.price = PriceCollector()

    def collect_all(self):
        logger.info('Starting Twitter data collection...')
        self.twitter.collect_all_tweets()
        logger.info('Starting Reddit data collection...')
        self.reddit.collect_all()
        logger.info('Starting price data collection...')
        self.price.collect_all_data()
        logger.info('All data collection complete.')

    def schedule_collection(self, interval_minutes=60):
        while True:
            self.collect_all()
            logger.info(f'Waiting {interval_minutes} minutes until next collection...')
            time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    collector = DataCollector()
    collector.collect_all() 