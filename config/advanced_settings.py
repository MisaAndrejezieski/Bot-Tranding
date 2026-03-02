import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AdvancedSettings:
    """Configurações avançadas do bot - Estratégia -2%/+4%"""

    # Trading
    symbol: str = "BTC/USDT"
    base_currency: str = "USDT"
    trade_quantity: float = 0.001  # Quantidade em BTC

    # 🎯 ESTRATÉGIA PRINCIPAL -2%/+4%
    buy_threshold: float = -2.0  # Compra na queda de 2%
    sell_threshold: float = 4.0  # Vende na alta de 4%
    stop_loss: float = -3.0  # Stop loss em -3%

    # Proteção Avançada
    enable_dynamic_stop: bool = True
    trailing_stop: bool = True
    trailing_distance: float = 1.0  # %
    protection_trigger: float = -5.0  # Ativa proteção após queda de 5%

    # Limites
    max_daily_trades: int = 3
    max_consecutive_losses: int = 2
    max_drawdown: float = 15.0  # %
    min_volume_btc: float = 100  # Volume mínimo em BTC

    # Indicadores Técnicos
    use_rsi: bool = True
    rsi_period: int = 14
    rsi_oversold: int = 35  # Mais sensível para -2%/+4%
    rsi_overbought: int = 75

    use_macd: bool = True
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    use_bollinger: bool = True
    bb_period: int = 20
    bb_std: float = 2.0

    # Timeframes
    primary_timeframe: str = "1h"
    secondary_timeframe: str = "15m"
    analysis_periods: int = 100

    # Risk Management
    risk_per_trade: float = 2.0  # % do capital por trade
    max_position_size: float = 10.0  # % do capital máximo em posição
    use_kelly_criterion: bool = False

    # Notifications
    notify_on_trade: bool = True
    notify_on_drawdown: bool = True
    notify_daily_report: bool = True
    notify_time: str = "20:00"

    # Advanced Features
    use_ml_predictions: bool = False
    ml_model_path: Optional[str] = None

    enable_arbitrage: bool = False
    arbitrage_exchanges: list = None

    # Database
    save_trades: bool = True
    save_capital_history: bool = True
    save_signals: bool = False

    def __post_init__(self):
        if self.arbitrage_exchanges is None:
            self.arbitrage_exchanges = ["binance", "bybit", "kraken"]

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def save_to_file(self, filename: str = "config.json"):
        """Salva configurações em arquivo"""
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str = "config.json"):
        """Carrega configurações de arquivo"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            return cls()
