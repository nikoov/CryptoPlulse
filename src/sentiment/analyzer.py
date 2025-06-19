import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from transformers import pipeline
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_name='finiteautomata/bertweet-base-sentiment-analysis'):
        load_dotenv()
        self.model_name = model_name
        self.analyzer = pipeline('sentiment-analysis', model=model_name)

    def analyze_text(self, text: str) -> Dict[str, Any]:
        try:
            result = self.analyzer(text)[0]
            sentiment = result['label'].lower()
            confidence = float(result['score'])
            return {'sentiment': sentiment, 'confidence': confidence}
        except Exception as e:
            logger.error(f'Error analyzing text: {e}')
            return {'sentiment': 'neutral', 'confidence': 0.0}

    def analyze_file(self, input_path: str, output_path: str, text_key: str = 'text'):
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            text = item.get(text_key, '')
            item['sentiment_analysis'] = self.analyze_text(text)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f'Sentiment analysis complete. Results saved to {output_path}')

    def analyze_directory(self, input_dir: str, output_dir: str, text_key: str = 'text'):
        os.makedirs(output_dir, exist_ok=True)
        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f'sentiment_{filename}')
                self.analyze_file(input_path, output_path, text_key=text_key)

if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    # Example: analyze Reddit posts
    analyzer.analyze_directory('data/reddit', 'data/sentiment/reddit', text_key='text')
    # Example: analyze Tweets
    analyzer.analyze_directory('data/tweets', 'data/sentiment/tweets', text_key='text') 