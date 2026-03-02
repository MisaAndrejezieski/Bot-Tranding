from datetime import datetime
from typing import Dict, Optional

from utils.logger import logger  # type: ignore[reportMissingImports]

from core.exchange import ExchangeManager
from core.strategy_avancada import EstrategiaAvancada


class TradingBot:
    """Bot de trading principal"""

    def __init__(self, capital_inicial: float = 1000):
        self.capital_inicial = capital_inicial
        self.capital_atual = capital_inicial
        self.strategy = EstrategiaAvancada()
        self.exchange = ExchangeManager()
        self.running = False
        self.trades = []

    def start(self):
        """Inicia o bot"""
        self.running = True
        logger.info("🤖 Bot iniciado")

    def stop(self):
        """Para o bot"""
        self.running = False
        logger.info("🛑 Bot parado")

    def process_ticker(self, ticker: Dict):
        """Processa um novo ticker"""
        if not ticker:
            return

        preco = ticker["last"]
        volume = ticker.get("volume", 0)

        # Atualiza históricos
        self.strategy.update_price_history(preco)
        self.strategy.update_volume_history(volume)

        # Verifica sinais
        if not self.strategy.position:
            # Análise de compra
            analise = self.strategy.analisar_momento_compra(preco)

            if analise["decisao"]:
                logger.info(
                    f"🎯 SINAL DE COMPRA! Confiança: {analise['confianca']:.1f}%"
                )
                for motivo in analise["motivos"]:
                    logger.info(f"   • {motivo}")

                # Executa compra
                order = self.exchange.create_buy_order()
                if order:
                    position = self.strategy.execute_buy(preco)
                    self._registrar_trade("COMPRA", preco, analise)

        else:
            # Análise de venda
            analise = self.strategy.analisar_momento_venda(
                preco, self.strategy.position["buy_price"]
            )

            if analise["decisao"]:
                logger.info(
                    f"🎯 SINAL DE VENDA! Confiança: {analise['confianca']:.1f}%"
                )
                for motivo in analise["motivos"]:
                    logger.info(f"   • {motivo}")

                # Executa venda
                order = self.exchange.create_sell_order()
                if order:
                    resultado = self.strategy.execute_sell(preco)
                    self._registrar_trade("VENDA", preco, analise, resultado)

                    # Atualiza capital
                    lucro = resultado.get("profit_abs", 0)
                    self.capital_atual += lucro

                    logger.info(f"💰 Lucro: {resultado['profit_percentage']:.2f}%")

    def _registrar_trade(
        self, tipo: str, preco: float, analise: Dict, resultado: Dict = None
    ):
        """Registra um trade"""
        trade = {
            "timestamp": datetime.now(),
            "type": tipo,
            "price": preco,
            "analysis": analise,
        }

        if resultado:
            trade["result"] = resultado

        self.trades.append(trade)
        logger.info(f"📝 Trade registrado: {tipo} @ R$ {preco:,.2f}")
