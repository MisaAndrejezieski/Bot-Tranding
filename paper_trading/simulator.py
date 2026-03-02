import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
from utils.logger import logger

from core.strategy_avancada import EstrategiaAvancada


class PaperTradingSimulator:
    """Simulador avançado de trading com cenários realistas"""

    def __init__(self, capital_inicial=1000):
        self.capital_inicial = capital_inicial
        self.capital = capital_inicial
        self.positions = []
        self.trades = []
        self.scenario = "normal"
        self.strategy = None

    def set_scenario(self, scenario: str):
        """Define cenário de mercado para simulação"""
        valid_scenarios = ["normal", "crash", "pump", "lateral", "volatile"]
        if scenario in valid_scenarios:
            self.scenario = scenario
            print(f"📊 Cenário definido: {scenario.upper()}")

    def generate_price_series(self, hours: int = 168) -> List[Dict]:
        """Gera série de preços realista baseada no cenário"""
        prices = []
        current_price = 350000  # Preço inicial BTC (~R$ 350k)

        for hour in range(hours):
            timestamp = datetime.now() + timedelta(hours=hour)

            # Define volatilidade baseada no cenário
            if self.scenario == "normal":
                volatility = 0.015  # 1.5% de variação
                trend = 0.0002
            elif self.scenario == "crash":
                volatility = 0.03
                trend = -0.0015
            elif self.scenario == "pump":
                volatility = 0.03
                trend = 0.002
            elif self.scenario == "lateral":
                volatility = 0.005
                trend = 0
            else:  # volatile
                volatility = 0.04
                trend = random.choice([-0.001, 0.001])

            # Gera variação
            change = np.random.normal(trend, volatility)
            current_price *= 1 + change

            # Adiciona eventos extremos ocasionais
            if random.random() < 0.2:
                if self.scenario == "crash":
                    current_price *= 0.95
                elif self.scenario == "pump":
                    current_price *= 1.05

            prices.append(
                {
                    "timestamp": timestamp,
                    "price": current_price,
                    "volume": random.uniform(100, 1000) * current_price / 1000,
                }
            )

        return prices

    async def run_simulation(self, strategy: EstrategiaAvancada, hours: int = 168):
        """Executa simulação com a estratégia"""
        self.strategy = strategy
        price_series = self.generate_price_series(hours)

        print(f"\n🚀 INICIANDO PAPER TRADING - {hours} horas")
        print(f"💰 Capital inicial: R$ {self.capital:.2f}")
        print(f"📊 Cenário: {self.scenario.upper()}\n")

        for hour, data in enumerate(price_series):
            price = data["price"]
            timestamp = data["timestamp"]
            volume = data["volume"]

            # Atualiza históricos
            self.strategy.update_price_history(price)
            self.strategy.update_volume_history(volume)

            # Executa estratégia
            if not self.strategy.position:
                # Verifica compra
                analise = self.strategy.analisar_momento_compra(price)

                if analise["decisao"]:
                    position = self.strategy.execute_buy(price)
                    self.positions.append(
                        {
                            "buy_price": price,
                            "buy_time": timestamp,
                            "quantity": self.capital / price,
                        }
                    )
                    self.capital = 0

                    print(
                        f"🟢 [{timestamp.strftime('%d/%m %H:%M')}] COMPRA @ R$ {price:,.2f}"
                    )
                    print(f"   Motivos: {', '.join(analise['motivos'])}")

            else:
                # Verifica venda
                analise = self.strategy.analisar_momento_venda(
                    price, self.strategy.position["buy_price"]
                )

                if analise["decisao"]:
                    result = self.strategy.execute_sell(price)
                    self.capital = result["profit_abs"] + self.capital_inicial

                    print(
                        f"🔴 [{timestamp.strftime('%d/%m %H:%M')}] VENDA @ R$ {price:,.2f}"
                    )
                    print(f"   Lucro: {result['profit_percentage']:.2f}%")
                    print(f"   Motivos: {', '.join(analise['motivos'])}")

                    self.trades.append(result)

            # Mostra progresso
            if hour % 24 == 0 and hour > 0:
                dia = hour // 24
                capital_atual = (
                    self.capital
                    if self.capital > 0
                    else self.positions[-1]["buy_price"]
                    * self.positions[-1]["quantity"]
                )
                print(f"\n📅 Dia {dia} - Capital: R$ {capital_atual:.2f}")

        # Relatório final
        self.generate_report()

    def generate_report(self):
        """Gera relatório da simulação"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO PAPER TRADING")
        print("=" * 60)

        if self.trades:
            df_trades = pd.DataFrame(self.trades)

            print(f"\n📈 Estatísticas:")
            print(f"   Total de trades: {len(self.trades)}")
            print(
                f"   Trades com lucro: {len([t for t in self.trades if t['profit_percentage'] > 0])}"
            )
            print(
                f"   Trades com prejuízo: {len([t for t in self.trades if t['profit_percentage'] <= 0])}"
            )
            print(f"   Lucro médio: {df_trades['profit_percentage'].mean():.2f}%")
            print(f"   Maior lucro: {df_trades['profit_percentage'].max():.2f}%")
            print(f"   Maior prejuízo: {df_trades['profit_percentage'].min():.2f}%")

            # Calcula capital final
            capital_final = (
                self.capital
                if self.capital > 0
                else self.positions[-1]["buy_price"] * self.positions[-1]["quantity"]
            )
            lucro_total = capital_final - self.capital_inicial

            print(f"\n💰 Resultado Financeiro:")
            print(f"   Capital inicial: R$ {self.capital_inicial:.2f}")
            print(f"   Capital final: R$ {capital_final:.2f}")
            print(f"   Lucro/Prejuízo: R$ {lucro_total:+.2f}")
            print(f"   Rentabilidade: {(lucro_total/self.capital_inicial)*100:+.2f}%")
        else:
            print("Nenhum trade executado na simulação")
