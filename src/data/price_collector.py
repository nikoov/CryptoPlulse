import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceCollector:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cryptocurrencies = {
            'bitcoin': 'Bitcoin',
            'ethereum': 'Ethereum',
            'binancecoin': 'BNB',
            'ripple': 'XRP',
            'cardano': 'Cardano',
            'dogecoin': 'Dogecoin'
        }
        self.fiat_currencies = ['usd', 'eur', 'gbp', 'jpy']

    def get_current_prices(self, vs_currencies: List[str] = None) -> Dict[str, Dict[str, float]]:
        if vs_currencies is None:
            vs_currencies = self.fiat_currencies
        crypto_ids = ','.join(self.cryptocurrencies.keys())
        vs_currencies_str = ','.join(vs_currencies)
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': crypto_ids,
            'vs_currencies': vs_currencies_str,
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to fetch current prices: {response.status_code}")
        return {}

    def get_historical_prices(self, crypto_id: str, vs_currency: str = 'usd', days: int = 365) -> pd.DataFrame:
        url = f"{self.base_url}/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily'
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"Failed to fetch historical prices for {crypto_id}: {response.status_code}")
            return pd.DataFrame()
        data = response.json()
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['volume'] = [x[1] for x in data['total_volumes']]
        df['market_cap'] = [x[1] for x in data['market_caps']]
        return df

    def save_price_data(self, data: Any, data_type: str):
        filename = f'data/prices_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if isinstance(data, pd.DataFrame):
            data.to_csv(f"{filename}.csv")
            logger.info(f"Saved {data_type} price data to {filename}.csv")
        else:
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {data_type} price data to {filename}.json")

    def collect_all_data(self):
        current_prices = self.get_current_prices()
        if current_prices:
            self.save_price_data(current_prices, 'current')
            time.sleep(2)
        for crypto_id in self.cryptocurrencies:
            logger.info(f"Collecting historical prices for {self.cryptocurrencies[crypto_id]}")
            historical_prices = self.get_historical_prices(crypto_id)
            if not historical_prices.empty:
                self.save_price_data(historical_prices, f'historical_{crypto_id}')
            logger.info("Waiting 10 seconds before next request...")
            time.sleep(10)

if __name__ == '__main__':
    collector = PriceCollector()
    collector.collect_all_data() 