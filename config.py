#!/usr/bin/env python3
"""
Configuration Management for MetasploitMCP
Centralized configuration for all services
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    """Main configuration class"""
    
    # Flask/API Settings
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = False
    
    # Metasploit RPC Settings
    MSF_RPC_HOST: str = "127.0.0.1"
    MSF_RPC_PORT: int = 55553
    MSF_RPC_PASSWORD: str = "kali"
    MSF_RPC_SSL: bool = False
    
    # AI Settings
    AI_KNOWLEDGE_FILE: str = "data/knowledge/metasploit_ai_knowledge.json"
    AI_ENABLED: bool = True
    
    # Campaign Settings
    CAMPAIGN_DATA_DIR: str = "data/campaigns"
    MAX_CONCURRENT_CAMPAIGNS: int = 5
    
    # Network Scanning
    DEFAULT_SCAN_INTERFACES: list = None
    SCAN_TIMEOUT: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/metasploitmcp.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    def __post_init__(self):
        if self.DEFAULT_SCAN_INTERFACES is None:
            self.DEFAULT_SCAN_INTERFACES = ["wlan0", "wlan1", "eth0", "eth1"]
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            FLASK_HOST=os.getenv("FLASK_HOST", "0.0.0.0"),
            FLASK_PORT=int(os.getenv("FLASK_PORT", 5000)),
            FLASK_DEBUG=os.getenv("FLASK_DEBUG", "False").lower() == "true",
            MSF_RPC_HOST=os.getenv("MSF_RPC_HOST", "127.0.0.1"),
            MSF_RPC_PORT=int(os.getenv("MSF_RPC_PORT", 55553)),
            MSF_RPC_PASSWORD=os.getenv("MSF_RPC_PASSWORD", "kali"),
            AI_KNOWLEDGE_FILE=os.getenv("AI_KNOWLEDGE_FILE", "data/knowledge/metasploit_ai_knowledge.json"),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        )

# Global config instance
config = Config.from_env()