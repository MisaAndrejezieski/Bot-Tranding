from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np


class RiskManager:
    """Gerenciador de risco profissional"""

    def __init__(self, capital_inicial: float):
        self.capital_inicial = capital_inicial
        self.capital_atual = capital_inicial
        self.max_drawdown = 0
        self.peak_capital = capital_inicial
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.last_reset = datetime.now()

        # Limites (ajustados para -2%/+4%)
        self.max_daily_trades = 3
        self.max_consecutive_losses = 2
        self.max_daily_loss = capital_inicial * 0.06  # 6% ao dia
        self.max_weekly_loss = capital_inicial * 0.15  # 15% na semana

        # Histórico
        self.trade_history = []
        self.daily_pnl = {}

    def check_trade_allowed(self, trade_value: float) -> Dict:
        """Verifica se o trade pode ser executado"""
        self._reset_daily_counters()

        reasons = []
        allowed = True

        # 1. Limite diário de trades
        if self.daily_trades >= self.max_daily_trades:
            allowed = False
            reasons.append(f"Limite diário de {self.max_daily_trades} trades atingido")

        # 2. Perdas consecutivas
        if self.consecutive_losses >= self.max_consecutive_losses:
            allowed = False
            reasons.append(
                f"{self.consecutive_losses} perdas consecutivas - pausa forçada"
            )

        # 3. Drawdown máximo
        current_drawdown = (
            (self.peak_capital - self.capital_atual) / self.peak_capital * 100
        )
        if current_drawdown > 10:
            allowed = False
            reasons.append(f"Drawdown de {current_drawdown:.1f}% - reduzindo posição")

        # 4. Tamanho da posição (não arriscar mais que 2% do capital)
        max_position_size = self.capital_atual * 0.02
        if trade_value > max_position_size:
            allowed = False
            reasons.append(f"Posição de R$ {trade_value:.2f} excede 2% do capital")

        # 5. Horário de trading (evitar noturno)
        hora_atual = datetime.now().hour
        if hora_atual < 9 or hora_atual > 18:
            if self.capital_atual < self.capital_inicial * 1.1:
                allowed = False
                reasons.append("Fora do horário recomendado")

        return {
            "allowed": allowed,
            "reasons": reasons,
            "risk_score": self._calculate_risk_score(),
            "suggested_position": min(trade_value, self.capital_atual * 0.02),
        }

    def register_trade(self, trade_result: Dict):
        """Registra resultado do trade para análise de risco"""

        self.trade_history.append(trade_result)
        self.daily_trades += 1

        # Atualiza capital
        self.capital_atual += trade_result.get("pnl", 0)

        # Atualiza peak capital
        if self.capital_atual > self.peak_capital:
            self.peak_capital = self.capital_atual

        # Atualiza perdas consecutivas
        if trade_result.get("pnl", 0) < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        # Registra PnL diário
        today = datetime.now().date()
        if today not in self.daily_pnl:
            self.daily_pnl[today] = 0
        self.daily_pnl[today] += trade_result.get("pnl", 0)

    def _reset_daily_counters(self):
        """Reseta contadores diários"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_trades = 0
            self.last_reset = now

    def _calculate_risk_score(self) -> float:
        """Calcula score de risco atual (0-100)"""
        score = 0

        # Drawdown atual
        drawdown = (self.peak_capital - self.capital_atual) / self.peak_capital * 100
        if drawdown > 5:
            score += 30
        elif drawdown > 2:
            score += 15

        # Perdas consecutivas
        score += self.consecutive_losses * 10

        # Volatilidade recente
        if len(self.trade_history) >= 5:
            recent_trades = self.trade_history[-5:]
            volatility = np.std([t.get("pnl", 0) for t in recent_trades])
            if volatility > self.capital_atual * 0.01:
                score += 20

        return min(score, 100)

    def get_risk_report(self) -> Dict:
        """Gera relatório de risco"""
        return {
            "capital_atual": self.capital_atual,
            "peak_capital": self.peak_capital,
            "drawdown": (self.peak_capital - self.capital_atual)
            / self.peak_capital
            * 100,
            "consecutive_losses": self.consecutive_losses,
            "daily_trades": self.daily_trades,
            "risk_score": self._calculate_risk_score(),
            "total_trades": len(self.trade_history),
            "win_rate": (
                len([t for t in self.trade_history if t.get("pnl", 0) > 0])
                / len(self.trade_history)
                * 100
                if self.trade_history
                else 0
            ),
            "avg_trade": (
                np.mean([t.get("pnl", 0) for t in self.trade_history])
                if self.trade_history
                else 0
            ),
        }
