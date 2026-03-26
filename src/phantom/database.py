#!/usr/bin/env python3
"""
Database management for MetasploitMCP
Thread-safe SQLite implementation for campaign data and audit logs.
"""
import sqlite3
import os
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional
from phantom.config import config

logger = logging.getLogger("Phantom.Database")

class CampaignDatabase:
    """Thread-safe manager for campaign and audit data."""

    def __init__(self, db_path: str = None):
        # Use path from config if not explicitly provided
        self.db_path = db_path or os.path.join(config.CAMPAIGN_DATA_DIR, "campaigns.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()

    @contextmanager
    def connection(self):
        """Context manager for thread-safe database connections."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema with robust constraints."""
        with self.connection() as conn:
            cursor = conn.cursor()
            # Campaigns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    target_mac TEXT,
                    target_ip TEXT NOT NULL,
                    os_guess TEXT,
                    status TEXT DEFAULT 'pending',
                    aggressive BOOLEAN DEFAULT 0,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Campaign results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    exploit TEXT NOT NULL,
                    payload TEXT,
                    status TEXT NOT NULL,
                    error TEXT,
                    session_id TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                )
            """)
            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    user TEXT DEFAULT 'system',
                    target TEXT,
                    result TEXT NOT NULL,
                    details TEXT
                )
            """)

    def create_campaign(self, campaign_id: str, target_ip: str, name: str = "Auto"):
        """Initialize a new campaign entry."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO campaigns (id, target_ip, status, start_time)
                VALUES (?, ?, ?, ?)
            """, (campaign_id, target_ip, 'running', datetime.now().isoformat()))
        return campaign_id

    def log_exploit_result(self, campaign_id: str, result: Dict):
        """Log an individual exploit attempt and update campaign counters."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO campaign_results (campaign_id, exploit, payload, status, error, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, result['exploit'], result.get('payload'),
                result['status'], result.get('error'), result.get('session_id')
            ))
            
            # Increment success/fail counters
            column = "success_count" if result['status'] == 'success' else "fail_count"
            conn.execute(f"UPDATE campaigns SET {column} = {column} + 1 WHERE id = ?", (campaign_id,))

    def get_all_campaigns(self, limit: int = 50) -> List[Dict]:
        """Fetch summary list of recent campaigns."""
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY start_time DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_campaign_details(self, campaign_id: str) -> Optional[Dict]:
        """Retrieve a full report including all exploit attempts for a campaign."""
        with self.connection() as conn:
            campaign = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
            if not campaign:
                return None
            
            results = conn.execute("SELECT * FROM campaign_results WHERE campaign_id = ?", (campaign_id,)).fetchall()
            data = dict(campaign)
            data['results'] = [dict(r) for r in results]
            return data

    def log_audit(self, action: str, target: str, result: str, details: str = None):
        """System-wide audit logging for security tracking."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO audit_logs (action, target, result, details)
                VALUES (?, ?, ?, ?)
            """, (action, target, result, details))

# Global database instance using paths from centralized config
db = CampaignDatabase()
