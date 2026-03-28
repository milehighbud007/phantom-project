#!/usr/bin/env python3
"""
Safe unit tests for current package utilities.
"""

from pathlib import Path

from phantom.config import Config
from phantom.database import CampaignDatabase


def test_config_masks_password_and_creates_directories(tmp_path):
    knowledge_file = tmp_path / "knowledge" / "ai.json"
    log_file = tmp_path / "logs" / "phantom.log"
    campaign_dir = tmp_path / "campaigns"

    cfg = Config(
        AI_KNOWLEDGE_FILE=str(knowledge_file),
        LOG_FILE=str(log_file),
        CAMPAIGN_DATA_DIR=str(campaign_dir),
        MSF_RPC_PASSWORD="secret",
    )

    assert campaign_dir.is_dir()
    assert log_file.parent.is_dir()
    assert knowledge_file.parent.is_dir()
    assert cfg.to_dict()["MSF_RPC_PASSWORD"] == "********"


def test_campaign_database_stores_and_returns_campaign_details(tmp_path):
    db_path = tmp_path / "campaigns.db"
    database = CampaignDatabase(str(db_path))

    campaign_id = database.create_campaign("cmp-001", "192.0.2.10")
    database.log_exploit_result(
        campaign_id,
        {
            "exploit": "demo/module",
            "payload": "payload/demo",
            "status": "success",
            "session_id": "1",
        },
    )

    details = database.get_campaign_details(campaign_id)

    assert details is not None
    assert details["id"] == "cmp-001"
    assert details["success_count"] == 1
    assert len(details["results"]) == 1
    assert details["results"][0]["exploit"] == "demo/module"
