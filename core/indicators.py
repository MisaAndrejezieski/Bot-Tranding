from typing import Dict, List

import numpy as np
import pandas as pd


class AnaliseTecnica:
    """Indicadores técnicos para melhorar as decisões"""

    @staticmethod
    def calcular_rsi(precos: List[float], periodo: int = 14) -> float:
        """RSI - Relative Strength Index (sobrecomprado/sobrevendido)"""
        if len(precos) < periodo + 1:
            return 50

        series = pd.Series(precos)
        delta = series.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    @staticmethod
    def calcular_macd(precos: List[float]) -> Dict:
        """MACD - Moving Average Convergence Divergence"""
        if len(precos) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0}

        exp1 = pd.Series(precos).ewm(span=12, adjust=False).mean()
        exp2 = pd.Series(precos).ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return {
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "histogram": histogram.iloc[-1],
        }

    @staticmethod
    def calcular_bandas_bollinger(precos: List[float], periodo: int = 20) -> Dict:
        """Bandas de Bollinger"""
        if len(precos) < periodo:
            return {"superior": precos[-1], "media": precos[-1], "inferior": precos[-1]}

        series = pd.Series(precos)
        media = series.rolling(window=periodo).mean()
        desvio = series.rolling(window=periodo).std()

        banda_superior = media + (desvio * 2)
        banda_inferior = media - (desvio * 2)

        return {
            "superior": banda_superior.iloc[-1],
            "media": media.iloc[-1],
            "inferior": banda_inferior.iloc[-1],
        }

    @staticmethod
    def calcular_volume_profile(
        volumes: List[float], precos: List[float], bins: int = 10
    ) -> Dict:
        """Perfil de Volume - áreas de suporte/resistência"""
        if len(precos) < 10:
            return {}

        price_range = np.linspace(min(precos), max(precos), bins)
        volume_by_price = {f"{price:.0f}": 0 for price in price_range}

        for i, price in enumerate(precos):
            idx = np.digitize(price, price_range) - 1
            if 0 <= idx < len(price_range):
                key = f"{price_range[idx]:.0f}"
                volume_by_price[key] += volumes[i] if i < len(volumes) else 0

        max_volume_price = max(volume_by_price, key=volume_by_price.get)

        return {
            "volume_profile": volume_by_price,
            "ponto_controle": float(max_volume_price),
        }
