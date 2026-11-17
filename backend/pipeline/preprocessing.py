"""
Drain3 Template Extractor and Preprocessing.
Extracts recurring log templates (event IDs) using Drain3.
Masks dynamic tokens like IPs, ports, UUIDs, and numbers.
"""

import re
from typing import Dict, List, Tuple
import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.masking import MaskingInstruction

# Regex patterns to mask dynamic variables before Drain clustering
MASKING_RULES = [
    # IPv4 addresses
    (r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b", "<IP>"),
    # UUIDs
    (r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b", "<UUID>"),
    # Numbers/IDs/Durations (e.g. 1240ms, PID 4120, user 1029)
    (r"\b\d+ms\b", "<DURATION>"),
    (r"\b\d+\b", "<NUM>"),
]


def create_template_miner() -> TemplateMiner:
    """Create a configured Drain3 TemplateMiner instance."""
    config = TemplateMinerConfig()
    config.drain_sim_th = 0.5  # similarity threshold
    config.drain_depth = 4     # parse tree depth
    config.drain_max_children = 100

    # Add custom masking instructions
    custom_masks = [
        MaskingInstruction(pattern, replacement)
        for pattern, replacement in MASKING_RULES
    ]
    config.masking_instructions = custom_masks
    return TemplateMiner(config=config)


class LogTemplateExtractor:
    """
    Mines templates and maps log lines to Event IDs (e.g. E001, E002).
    Tracks cluster frequencies to detect rare templates.
    """

    def __init__(self, rare_threshold: float = 0.05):
        """
        rare_threshold: Templates appearing in less than this fraction
        of total logs are considered 'rare'.
        """
        self.miner = create_template_miner()
        self.cluster_id_to_event_id: Dict[int, str] = {}
        self.event_id_to_template: Dict[str, str] = {}
        self.event_counts: Dict[str, int] = {}
        self.rare_threshold = rare_threshold

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the DataFrame's 'message' column.
        Appends:
        - 'template': mined pattern string
        - 'event_id': E001, E002, etc.
        - 'is_rare_event': boolean flag
        """
        if df.empty or "message" not in df.columns:
            df["template"] = []
            df["event_id"] = []
            df["is_rare_event"] = []
            return df

        df = df.copy()
        templates: List[str] = []
        event_ids: List[str] = []

        # Step 1: Mine templates for each log message
        for msg in df["message"]:
            msg_str = str(msg)
            result = self.miner.add_log_message(msg_str)
            cluster_id = result["cluster_id"]
            template_str = result["template_mined"]

            if cluster_id not in self.cluster_id_to_event_id:
                eid = f"E{len(self.cluster_id_to_event_id) + 1:03d}"
                self.cluster_id_to_event_id[cluster_id] = eid
                self.event_id_to_template[eid] = template_str
            else:
                eid = self.cluster_id_to_event_id[cluster_id]

            templates.append(template_str)
            event_ids.append(eid)
            self.event_counts[eid] = self.event_counts.get(eid, 0) + 1

        df["template"] = templates
        df["event_id"] = event_ids

        # Step 2: Determine rare events
        total_logs = len(df)
        rare_event_ids = {
            eid for eid, count in self.event_counts.items()
            if (count / max(total_logs, 1)) <= self.rare_threshold
        }
        df["is_rare_event"] = df["event_id"].isin(rare_event_ids)

        return df

    def get_template_catalog(self) -> pd.DataFrame:
        """Return a summary DataFrame of all discovered templates and counts."""
        rows = []
        for eid, template in self.event_id_to_template.items():
            count = self.event_counts.get(eid, 0)
            rows.append({
                "event_id": eid,
                "template": template,
                "count": count
            })
        return pd.DataFrame(rows).sort_values(by="count", ascending=False).reset_index(drop=True)
