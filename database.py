#!/usr/bin/env python3
"""
Database management for MetasploitMCP
SQLite database for storing campaign data, results, and audit logs
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class CampaignDatabase:
    """Manage campaign and audit data"""
    
    def __init__(self, db_path: str = "data/campaigns.db"):
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Campaigns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                target_mac TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                os_guess TEXT,
                status TEXT NOT NULL,
                aggressive BOOLEAN,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_exploits INTEGER,
                successful_exploits INTEGER,
                failed_exploits INTEGER,
                skipped_exploits INTEGER,
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
                timestamp TEXT NOT NULL,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        """)
        
        # Audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user TEXT,
                target TEXT,
                details TEXT,
                result TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_campaign(self, campaign_data: Dict):
        """Save campaign metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO campaigns 
            (id, target_mac, target_ip, os_guess, status, aggressive,
             start_time, end_time, total_exploits, successful_exploits,
             failed_exploits, skipped_exploits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_data['id'],
            campaign_data['target_mac'],
            campaign_data['target_ip'],
            campaign_data.get('os_guess'),
            campaign_data['status'],
            campaign_data.get('aggressive', False),
            campaign_data['start_time'],
            campaign_data.get('end_time'),
            campaign_data.get('total_exploits', 0),
            campaign_data.get('successful_exploits', 0),
            campaign_data.get('failed_exploits', 0),
            campaign_data.get('skipped_exploits', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_campaign_result(self, campaign_id: str, result: Dict):
        """Save individual exploit result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO campaign_results
            (campaign_id, exploit, payload, status, error, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            result['exploit'],
            result.get('payload'),
            result['status'],
            result.get('error'),
            result['timestamp']
        ))
        
        conn.commit()
        conn.close()
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        """Retrieve campaign by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        
        if row:
            campaign = dict(row)
            
            # Get results
            cursor.execute(
                "SELECT * FROM campaign_results WHERE campaign_id = ?",
                (campaign_id,)
            )
            campaign['results'] = [dict(r) for r in cursor.fetchall()]
            
            conn.close()
            return campaign
        
        conn.close()
        return None
    
    def get_all_campaigns(self, limit: int = 100) -> List[Dict]:
        """Get all campaigns"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM campaigns ORDER BY start_time DESC LIMIT ?",
            (limit,)
        )
        
        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return campaigns
    
    def log_audit(self, action: str, target: str, result: str,
                  user: str = "system", details: str = None):
        """Log an audit event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs
            (timestamp, action, user, target, details, result)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            action,
            user,
            target,
            details,
            result
        ))
        
        conn.commit()
        conn.close()
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent audit logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs

# Global database instance
db = CampaignDatabase()