from datetime import datetime
from typing import Dict, List

import numpy as np

from core.indicators import AnaliseTecnica


class EstrategiaAvancada:
    """Versão melhorada com múltiplos indicadores - Estratégia -2%/+4%"""

    def __init__(self):
        self.indicators = AnaliseTecnica()
        self.price_history = []
        self.volume_history = []
        self.position = None
        self.daily_trades = 0

        # Pesos para cada indicador (otimizados para -2%/+4%)
        self.pesos = {
            "rsi": 0.15,
            "macd": 0.20,
            "bollinger": 0.30,  # Bollinger tem mais peso
            "volume": 0.20,
            "suporte_resistencia": 0.15,
        }

    def update_price_history(self, preco: float):
        """Atualiza histórico de preços"""
        self.price_history.append(preco)
        if len(self.price_history) > 100:
            self.price_history.pop(0)

    def update_volume_history(self, volume: float):
        """Atualiza histórico de volume"""
        self.volume_history.append(volume)
        if len(self.volume_history) > 100:
            self.volume_history.pop(0)

    def analisar_momento_compra(self, preco_atual: float) -> Dict:
        """Análise multifatorial para decisão de compra"""

        if len(self.price_history) < 30:
            return {
                "decisao": False,
                "confianca": 0,
                "motivo": "histórico insuficiente",
            }

        score = 0
        motivos = []

        # 1. Verificar queda de 2% (requisito principal)
        if len(self.price_history) > 1:
            queda = (
                (preco_atual - self.price_history[-2]) / self.price_history[-2] * 100
            )
            if queda <= -2.0:
                score += 0.3
                motivos.append(f"Queda de {queda:.1f}% (meta -2%)")
            else:
                return {
                    "decisao": False,
                    "confianca": 0,
                    "motivo": f"Queda insuficiente: {queda:.1f}%",
                }

        # 2. Análise RSI
        rsi = self.indicators.calcular_rsi(self.price_history)
        if rsi < 35:  # Sobre Vendido (ajustado)
            score += self.pesos["rsi"]
            motivos.append(f"RSI oversold: {rsi:.1f}")
        elif rsi < 45:
            score += self.pesos["rsi"] * 0.5
            motivos.append(f"RSI próximo de oversold: {rsi:.1f}")

        # 3. Análise MACD
        macd_data = self.indicators.calcular_macd(self.price_history)
        if macd_data["histogram"] > 0 and macd_data["macd"] > macd_data["signal"]:
            score += self.pesos["macd"]
            motivos.append("MACD com cruzamento positivo")

        # 4. Bandas de Bollinger
        bb = self.indicators.calcular_bandas_bollinger(self.price_history)
        if preco_atual <= bb["inferior"] * 1.01:  # Próximo da banda inferior
            score += self.pesos["bollinger"]
            motivos.append("Preço na banda inferior de Bollinger")
        elif preco_atual <= bb["media"]:
            score += self.pesos["bollinger"] * 0.5
            motivos.append("Preço abaixo da média de Bollinger")

        # 5. Análise de Volume
        if len(self.volume_history) > 5:
            volume_medio = np.mean(self.volume_history[-5:])
            volume_atual = self.volume_history[-1] if self.volume_history else 0

            if volume_atual > volume_medio * 1.3:  # Volume 30% acima da média
                score += self.pesos["volume"]
                motivos.append("Volume acima da média")

        # 6. Suporte/Resistência
        if len(self.price_history) > 20:
            suporte = np.percentile(self.price_history[-20:], 20)
            if preco_atual <= suporte * 1.02:  # Próximo do suporte
                score += self.pesos["suporte_resistencia"]
                motivos.append("Próximo do nível de suporte")

        # Decisão final
        confianca = min(score * 100, 100)

        return {
            "decisao": score >= 0.6,  # 60% de confiança necessário
            "confianca": confianca,
            "score": score,
            "motivos": motivos,
            "rsi": rsi,
        }

    def analisar_momento_venda(self, preco_atual: float, preco_compra: float) -> Dict:
        """Análise para decisão de venda"""

        if len(self.price_history) < 20:
            return {"decisao": False, "confianca": 0}

        score = 0
        motivos = []

        lucro_atual = (preco_atual - preco_compra) / preco_compra * 100

        # 1. Verificar lucro de 4% (requisito principal)
        if lucro_atual >= 4.0:
            score += 0.4
            motivos.append(f"Lucro de {lucro_atual:.1f}% (meta +4%)")
        else:
            return {
                "decisao": False,
                "confianca": 0,
                "motivo": f"Lucro insuficiente: {lucro_atual:.1f}%",
            }

        # 2. RSI sobrecomprado
        rsi = self.indicators.calcular_rsi(self.price_history)
        if rsi > 75:  # Sobrecomprado (ajustado)
            score += self.pesos["rsi"]
            motivos.append(f"RSI sobrecomprado: {rsi:.1f}")

        # 3. Bandas de Bollinger
        bb = self.indicators.calcular_bandas_bollinger(self.price_history)
        if preco_atual >= bb["superior"] * 0.99:  # Próximo da banda superior
            score += self.pesos["bollinger"]
            motivos.append("Preço na banda superior")

        # 4. Resistência
        if len(self.price_history) > 20:
            resistencia = np.percentile(self.price_history[-20:], 80)
            if preco_atual >= resistencia * 0.98:
                score += self.pesos["suporte_resistencia"]
                motivos.append("Próximo da resistência")

        return {
            "decisao": score >= 0.6,  # 60% de confiança
            "confianca": min(score * 100, 100),
            "score": score,
            "motivos": motivos,
            "lucro": lucro_atual,
        }

    def execute_buy(self, preco: float) -> Dict:
        """Executa compra"""
        self.position = {
            "buy_price": preco,
            "buy_time": datetime.now(),
            "lowest_price": preco,
        }
        return self.position

    def execute_sell(self, preco: float) -> Dict:
        """Executa venda"""
        if not self.position:
            return {}

        lucro = (preco - self.position["buy_price"]) / self.position["buy_price"] * 100
        lucro_abs = (preco - self.position["buy_price"]) * 0.001  # Aproximado

        result = {
            "profit_percentage": lucro,
            "profit_abs": lucro_abs,
            "buy_price": self.position["buy_price"],
            "sell_price": preco,
            "hold_time": (datetime.now() - self.position["buy_time"]).total_seconds()
            / 3600,
        }

        self.position = None
        self.daily_trades += 1

        return result
