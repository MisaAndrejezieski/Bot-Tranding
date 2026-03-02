import time
from typing import Dict, Any

# imports opcionais com fallback para evitar erros de Pylance e em ambientes
# onde o pacote ainda não foi instalado. Esses comentários `type: ignore`
# silenciam avisos de importação ausente.
try:
    import ccxt  # type: ignore[reportMissingImports]
except ImportError:  # pragma: no cover
    ccxt = None  # type: ignore

from utils.logger import logger  # type: ignore[reportMissingImports]


class ArbitrageScanner:
    """Scanner simples de arbitragem entre exchanges.

    O objetivo é monitorar um par (padrão BTC/USDT) em várias exchanges e
    reportar eventuais oportunidades de compra em uma e venda em outra quando
    existir diferença de preço acima de um determinado spread. A implementação
    atual não executa ordens, apenas loga as discrepâncias.
    """

    def __init__(self, symbol: str = "BTC/USDT", spread_threshold: float = 0.5):
        self.symbol = symbol
        self.spread_threshold = spread_threshold  # porcentagem mínima para alertar
        # Any usado porque ccxt pode ser None/omitido; evita erro de tipo
        self.exchanges: Dict[str, Any] = {}  # type: ignore[reportInvalidTypeForm]
        self.running = False

    def add_exchange(self, exchange_id: str):
        """Adiciona uma exchange ao scanner.

        O objeto ccxt é instanciado sem chaves de API, pois apenas buscamos
        preços públicos.
        """
        try:
            exchange_cls = getattr(ccxt, exchange_id)
            exch = exchange_cls({"enableRateLimit": True})
            self.exchanges[exchange_id] = exch
            logger.info(f"✅ Exchange adicionada ao scanner: {exchange_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar exchange {exchange_id}: {e}")

    def start_scanner(self, interval: int = 60):
        """Inicia o loop de verificação de preços.

        Este método bloqueia a chamada e roda até que stop() seja chamado.
        """
        if not self.exchanges:
            logger.warning("Nenhuma exchange cadastrada no scanner de arbitragem.")
            return

        self.running = True
        logger.info("🚀 Scanner de arbitragem iniciado")
        try:
            while self.running:
                prices = {}
                # obtém os últimos preços de cada exchange
                for name, exch in self.exchanges.items():
                    try:
                        ticker = exch.fetch_ticker(self.symbol)
                        prices[name] = ticker.get("last")
                    except Exception as e:
                        logger.warning(f"Erro ao buscar ticker em {name}: {e}")

                if prices:
                    # identifica best buy e best sell
                    best_buy = min(prices, key=prices.get)
                    best_sell = max(prices, key=prices.get)
                    buy_price = prices[best_buy]
                    sell_price = prices[best_sell]
                    spread = (sell_price - buy_price) / buy_price * 100

                    msg = (
                        f"🧮 Spread: {spread:.2f}% "
                        f"(buy em {best_buy}: {buy_price}, "
                        f"sell em {best_sell}: {sell_price})"
                    )
                    logger.info(msg)

                    if spread >= self.spread_threshold:
                        logger.info(f"🎯 Oportunidade de arbitragem detectada! {msg}")

                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("🛑 Scanner de arbitragem interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no scanner de arbitragem: {e}")
        finally:
            self.running = False
            logger.info("🛑 Scanner de arbitragem parado")

    def stop(self):
        """Para o scanner"""
        self.running = False
