# Arquivo de inicialização do pacote core
from core.exchange import ExchangeManager
from core.indicators import AnaliseTecnica
from core.strategy_avancada import EstrategiaAvancada
from core.trader import TradingBot

__all__ = ["ExchangeManager", "AnaliseTecnica", "EstrategiaAvancada", "TradingBot"]
