import itertools
from typing import Any, Dict, List


class ParameterSuggestion:
    def __init__(self, params: Dict[str, Any], metrics: Dict[str, float]):
        self.params = params
        self.metrics = metrics


class StrategyOptimizer:
    """Simples otimizador de parâmetros para backtests"""

    def __init__(self, backtest_engine):
        self.backtest = backtest_engine

    def optimize_parameters(
        self, df, param_grid: Dict[str, List[Any]], metric: str = "sharpe"
    ) -> Dict:
        """Executa backtest para todas as combinações e retorna melhores parâmetros"""
        combinations = list(itertools.product(*param_grid.values()))
        keys = list(param_grid.keys())

        all_results = []
        best_result = None
        best_params = None

        for combo in combinations:
            params = dict(zip(keys, combo))
            result = self.backtest.run_backtest(df, params)
            metrics = result.get("metrics", {})
            score = metrics.get(metric, 0)
            all_results.append({"params": params, "metrics": metrics})

            if best_result is None or score > best_result:
                best_result = score
                best_params = params

        return {
            "best_params": best_params,
            "best_result": best_result,
            "all_results": sorted(
                all_results, key=lambda x: x["metrics"].get(metric, 0), reverse=True
            ),
        }
