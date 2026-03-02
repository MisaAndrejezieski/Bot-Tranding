import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""

    def __init__(self, db_path="trading_bot.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa tabelas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de trades
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                type TEXT,
                price REAL,
                quantity REAL,
                value REAL,
                fee REAL,
                profit_percentage REAL,
                profit_abs REAL,
                strategy_params TEXT
            )
        """
        )

        # Tabela de capital histórico
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS capital_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                capital REAL,
                btc_price REAL
            )
        """
        )

        # Tabela de configurações
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME
            )
        """
        )

        # Tabela de alerts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                type TEXT,
                message TEXT,
                read BOOLEAN DEFAULT 0
            )
        """
        )

        conn.commit()
        conn.close()

    def save_trade(self, trade_data: Dict):
        """Salva um trade no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO trades 
            (timestamp, type, price, quantity, value, fee, profit_percentage, profit_abs, strategy_params)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                trade_data.get("type", ""),
                trade_data.get("price", 0),
                trade_data.get("quantity", 0),
                trade_data.get("value", 0),
                trade_data.get("fee", 0),
                trade_data.get("profit_percentage", 0),
                trade_data.get("profit_abs", 0),
                json.dumps(trade_data.get("strategy_params", {})),
            ),
        )

        conn.commit()
        conn.close()

    def save_capital_snapshot(self, capital: float, btc_price: float):
        """Salva snapshot do capital"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO capital_history (timestamp, capital, btc_price)
            VALUES (?, ?, ?)
        """,
            (datetime.now().isoformat(), capital, btc_price),
        )

        conn.commit()
        conn.close()

    def get_trade_history(self, days: int = 30) -> pd.DataFrame:
        """Retorna histórico de trades como DataFrame"""
        conn = sqlite3.connect(self.db_path)

        query = f"""
            SELECT * FROM trades 
            WHERE timestamp >= date('now', '-{days} days')
            ORDER BY timestamp DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def get_capital_history(self, days: int = 30) -> pd.DataFrame:
        """Retorna histórico de capital"""
        conn = sqlite3.connect(self.db_path)

        query = f"""
            SELECT * FROM capital_history 
            WHERE timestamp >= date('now', '-{days} days')
            ORDER BY timestamp
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def save_setting(self, key: str, value: str):
        """Salva configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            (key, value, datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

    def get_setting(self, key: str, default=None):
        """Recupera configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else default

    def add_alert(self, alert_type: str, message: str):
        """Adiciona alerta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO alerts (timestamp, type, message)
            VALUES (?, ?, ?)
        """,
            (datetime.now().isoformat(), alert_type, message),
        )

        conn.commit()
        conn.close()

    def get_unread_alerts(self) -> List[Dict]:
        """Retorna alertas não lidos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alerts WHERE read = 0 ORDER BY timestamp DESC")

        alerts = []
        for row in cursor.fetchall():
            alerts.append(
                {"id": row[0], "timestamp": row[1], "type": row[2], "message": row[3]}
            )

        conn.close()
        return alerts

    def mark_alert_read(self, alert_id: int):
        """Marca alerta como lido"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE alerts SET read = 1 WHERE id = ?", (alert_id,))

        conn.commit()
        conn.close()
