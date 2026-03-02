import os
from datetime import datetime
from typing import Dict, Optional

try:
    import ccxt  # type: ignore[reportMissingImports]
except ImportError:  # pragma: no cover
    ccxt = None  # type: ignore

try:
    from dotenv import load_dotenv  # type: ignore[reportMissingImports]
except ImportError:  # pragma: no cover
    def load_dotenv():  # type: ignore
        pass

load_dotenv()


class ExchangeManager:
    """Gerenciador de conexão com exchanges"""

    def __init__(self, exchange_id: str = "binance"):
        self.exchange_id = exchange_id
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.use_sandbox = os.getenv("USE_SANDBOX", "true").lower() == "true"

        self.exchange = self._initialize_exchange()
        self.last_price = 0

    def _initialize_exchange(self):
        """Inicializa a exchange"""
        exchange_class = getattr(ccxt, self.exchange_id)

        config = {
            "apiKey": self.api_key,
            "secret": self.api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }

        if self.use_sandbox:
            config["urls"] = {
                "api": {
                    "public": "https://testnet.binance.vision/api/v3",
                    "private": "https://testnet.binance.vision/api/v3",
                }
            }

        return exchange_class(config)

    def get_ticker(self, symbol: str = "BTC/USDT") -> Optional[Dict]:
        """Obtém ticker atual"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            self.last_price = ticker["last"]
            return {
                "last": ticker["last"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
                "volume": ticker["baseVolume"],
                "timestamp": ticker["timestamp"],
            }
        except Exception as e:
            print(f"Erro ao buscar ticker: {e}")
            return None

    def create_buy_order(
        self, symbol: str = "BTC/USDT", amount: float = 0.001
    ) -> Optional[Dict]:
        """Cria ordem de compra"""
        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            print(f"✅ Ordem de compra executada: {amount} BTC a {order['price']}")
            return order
        except Exception as e:
            print(f"❌ Erro na ordem de compra: {e}")
            return None

    def create_sell_order(
        self, symbol: str = "BTC/USDT", amount: float = 0.001
    ) -> Optional[Dict]:
        """Cria ordem de venda"""
        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            print(f"✅ Ordem de venda executada: {amount} BTC a {order['price']}")
            return order
        except Exception as e:
            print(f"❌ Erro na ordem de venda: {e}")
            return None

    def get_balance(self, currency: str = "USDT") -> float:
        """Obtém saldo de uma moeda"""
        try:
            balance = self.exchange.fetch_balance()
            return balance[currency]["free"]
        except Exception as e:
            print(f"Erro ao buscar saldo: {e}")
            return 0

    def fetch_ohlcv(
        self, symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 100
    ):
        """Busca dados históricos OHLCV"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Erro ao buscar OHLCV: {e}")
            return None
