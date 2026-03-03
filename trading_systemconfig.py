"""
Configuration management with environment variables and type safety
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from dotenv import load_dotenv

load_dotenv()

class TradingMode(Enum):
    """Trading operation modes"""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

class RiskLevel(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    credential_path: str = field(default_factory=lambda: os.getenv("FIREBASE_CREDENTIAL_PATH", "credentials/firebase.json"))
    project_id: str = field(default_factory=lambda: os.getenv("FIREBASE_PROJECT_ID", "evolution-trading"))
    database_url: str = field(default_factory=lambda: os.getenv("FIREBASE_DATABASE_URL", ""))
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not os.path.exists(self.credential_path):
            logging.error(f"Firebase credential file not found: {self.credential_path}")
            return False
        return bool(self.project_id)

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    exchange: str = field(default_factory=lambda: os.getenv("EXCHANGE", "binance"))
    api_key: str = field(default_factory=lambda: os.getenv("EXCHANGE_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("EXCHANGE_API_SECRET", ""))
    sandbox_mode: bool = field(default_factory=lambda: os.getenv("EXCHANGE_SANDBOX", "True").lower() == "true")
    
    def validate(self) -> bool:
        """Validate exchange configuration"""
        return bool(self.api_key and self.api_secret)

@dataclass
class ModelConfig:
    """Machine learning model configuration"""
    model_path: str = field(default_factory=lambda: os.getenv("MODEL_PATH", "models/"))
    retrain_interval_hours: int = field(default_factory=lambda: int(os.getenv("MODEL_RETRAIN_HOURS", "24")))
    prediction_horizon: int = field(default_factory=lambda: int(os.getenv("PREDICTION_HORIZON", "60")))  # minutes
    feature_window: int = field(default_factory=lambda: int(os.getenv("FEATURE_WINDOW", "100")))  # candles
    
    def validate(self) -> bool:
        """Validate model configuration"""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path, exist_ok=True)
        return True

@dataclass
class SystemConfig:
    """Main system configuration"""
    trading_mode: TradingMode = field(default_factory=lambda: TradingMode(os.getenv("TRADING_MODE", "paper")))
    risk_level: RiskLevel = field(default_factory=lambda: RiskLevel(os.getenv("RISK_LEVEL", "moderate")))
    max_position_size_usd: float = field(default_factory=lambda: float(os.getenv("MAX_POSITION_SIZE_USD", "1000.0")))
    max_daily_loss_pct: float = field(default_factory=lambda: float(os.getenv("MAX_DAILY_LOSS_PCT", "5.0")))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    
    # Sub-configurations
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)
    exchange: ExchangeConfig = field(default_factory=ExchangeConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    
    def validate(self) -> bool:
        """Validate entire configuration"""
        validations = [
            self.firebase.validate(),
            self.exchange.validate() if self.trading_mode != TradingMode.BACKTEST else True,
            self.model.validate()
        ]
        return all(validations)

# Global configuration instance
config = SystemConfig()

def get_config() -> SystemConfig:
    """Get validated configuration instance"""
    if not config.validate():
        logging.warning("Configuration validation failed. Some features may not work properly.")
    return config