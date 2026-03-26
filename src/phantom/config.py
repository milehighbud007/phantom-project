#!/usr/bin/env python3
"""
Configuration Management for MetasploitMCP
Centralized configuration for all services with .env support.
"""
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path

# Try to load dotenv for local development safety
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Config:
    """Main configuration class with environment-aware defaults."""
    
    # Flask/API Settings
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = False

    # Metasploit RPC Settings
    MSF_RPC_HOST: str = "127.0.0.1"
    MSF_RPC_PORT: int = 55553
    MSF_RPC_USER: str = "msf"
    MSF_RPC_PASSWORD: str = "kali"
    MSF_RPC_SSL: bool = True

    # AI Settings
    AI_KNOWLEDGE_FILE: str = "data/knowledge/metasploit_ai_knowledge.json"
    AI_ENABLED: bool = True

    # Campaign Settings
    CAMPAIGN_DATA_DIR: str = "data/campaigns"
    MAX_CONCURRENT_CAMPAIGNS: int = 5

    # Network Scanning
    DEFAULT_SCAN_INTERFACES: list = field(default_factory=lambda: ["wlan0", "wlan1", "eth0", "eth1"])
    SCAN_TIMEOUT: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/metasploitmcp.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5

    def __post_init__(self):
        """Ensure necessary directories exist on initialization."""
        for path_str in [self.CAMPAIGN_DATA_DIR, os.path.dirname(self.LOG_FILE), os.path.dirname(self.AI_KNOWLEDGE_FILE)]:
            if path_str:
                os.makedirs(path_str, exist_ok=True)

    @classmethod
    def from_env(cls):
        """Factory method to load configuration from environment variables."""
        return cls(
            FLASK_HOST=os.getenv("FLASK_HOST", "0.0.0.0"),
            FLASK_PORT=int(os.getenv("FLASK_PORT", 5000)),
            FLASK_DEBUG=os.getenv("FLASK_DEBUG", "False").lower() == "true",
            MSF_RPC_HOST=os.getenv("MSF_RPC_HOST", "127.0.0.1"),
            MSF_RPC_PORT=int(os.getenv("MSF_RPC_PORT", 55553)),
            MSF_RPC_USER=os.getenv("MSF_RPC_USER", "msf"),
            MSF_RPC_PASSWORD=os.getenv("MSF_RPC_PASSWORD", "kali"),
            MSF_RPC_SSL=os.getenv("MSF_RPC_SSL", "True").lower() == "true",
            AI_KNOWLEDGE_FILE=os.getenv("AI_KNOWLEDGE_FILE", "data/knowledge/metasploit_ai_knowledge.json"),
            AI_ENABLED=os.getenv("AI_ENABLED", "True").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO")
        )

    def to_dict(self):
        """Return a dictionary of settings, masking sensitive data."""
        data = self.__dict__.copy()
        if "MSF_RPC_PASSWORD" in data:
            data["MSF_RPC_PASSWORD"] = "********"
        return data

# Global config instance
config = Config.from_env()
