import os
import json
import logging
from datetime import datetime, timedelta
import praw
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'CryptoPulse/1.0')
        if not all([self.client_id, self.client_secret, self.user_agent]):
            raise ValueError('Reddit API credentials not set in .env')
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        self.subreddits = ['CryptoCurrency', 'Bitcoin', 'Ethereum', 'CryptoMarkets', 'Cardano', 'dogecoin']

    def collect_posts(self, subreddit_name, limit=50, days=1):
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        since = datetime.utcnow() - timedelta(days=days)
        for post in subreddit.new(limit=limit):
            if datetime.utcfromtimestamp(post.created_utc) < since:
                continue
            post_data = {
                'id': post.id,
                'title': post.title,
                'text': post.selftext,
                'created_utc': post.created_utc,
                'subreddit': subreddit_name,
                'score': post.score,
                'num_comments': post.num_comments,
                'url': post.url
            }
            posts.append(post_data)
        logger.info(f'Collected {len(posts)} posts from r/{subreddit_name}')
        return posts

    def save_posts(self, posts, subreddit_name):
        if not posts:
            logger.warning(f'No posts to save for r/{subreddit_name}')
            return
        os.makedirs('data/reddit', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/reddit/posts_{subreddit_name}_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f'Saved {len(posts)} posts to {filename}')

    def collect_all(self, limit=50, days=1):
        for subreddit in self.subreddits:
            posts = self.collect_posts(subreddit, limit=limit, days=days)
            self.save_posts(posts, subreddit)

if __name__ == '__main__':
    collector = RedditCollector()
    collector.collect_all() 