
from pathlib import Path
from typing import Optional

import pandas as pd
from src.investigation_engine import build_investigation
from src.investigation_graph import investigation_graph


from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="CyberSentinel AI API",
    description="Cybersecurity anomaly detection and alert investigation API",
    version="0.1.0"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ALERT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "security_alerts.csv"
)

def load_alerts():
    if not ALERT_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Security alert dataset is unavailable"
        )

    return pd.read_csv(ALERT_FILE)

@app.get("/")
def home():
    return {
        "application": "CyberSentinel AI",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "alerts_file_exists": ALERT_FILE.exists()
    }

@app.get("/alerts/summary")
def alert_summary():
    df = load_alerts()

    return {
        "total_alerts": len(df),
        "unique_source_computers": int(
            df["source_computer"].nunique()
        ),
        "severity_distribution": (
            df["severity"].value_counts().to_dict()
        ),
        "dataset_day_range": {
            "min": int(df["dataset_day"].min()),
            "max": int(df["dataset_day"].max())
        }
    }

@app.get("/alerts")
def list_alerts(
    severity: Optional[str] = None,
    source_computer: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    df = load_alerts()

    if severity:
        df = df[
            df["severity"].str.upper()
            == severity.upper()
        ]

    if source_computer:
        df = df[
            df["source_computer"].str.upper()
            == source_computer.upper()
        ]

    total = len(df)

    page = df.iloc[offset:offset + limit]

    # Convert missing values to JSON null.
    records = page.astype(object).where(
        pd.notnull(page), None
    ).to_dict(orient="records")

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "alerts": records
    }

@app.get("/alerts/{alert_id}")
def get_alert(alert_id: str):
    df = load_alerts()

    match = df[
        df["alert_id"] == alert_id
    ]

    if match.empty:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    record = match.iloc[0]

    return {
        key: (
            None if pd.isna(value)
            else value.item() if hasattr(value, "item")
            else value
        )
        for key, value in record.items()
    }

def build_investigation(alert):
    findings = []

    total_events = int(alert["total_events"])
    unique_destinations = int(alert["unique_destinations"])
    unique_users = int(alert["unique_users"])
    failed_logins = int(alert["failed_logins"])
    failure_rate = float(alert["failure_rate"])

    events_vs_history = float(
        alert["events_vs_history"]
    )

    destinations_vs_history = float(
        alert["destinations_vs_history"]
    )

    new_destinations = int(
        alert["new_destinations"]
    )

    new_user_pairs = int(
        alert["new_user_destination_pairs"]
    )

    if total_events >= 10000:
        findings.append({
            "category": "HIGH_AUTHENTICATION_VOLUME",
            "observation": (
                f"{total_events:,} authentication events "
                "were recorded on this source-day."
            ),
            "interpretation": (
                "High authentication volume may warrant "
                "review, depending on the computer's role."
            )
        })

    if failure_rate >= 0.10:
        findings.append({
            "category": "ELEVATED_FAILURE_RATE",
            "observation": (
                f"{failed_logins:,} failed logins; "
                f"failure rate {failure_rate:.1%}."
            ),
            "interpretation": (
                "Review failed authentication patterns "
                "for possible credential misuse."
            )
        })

    if events_vs_history >= 2.0:
        findings.append({
            "category": "AUTHENTICATION_VOLUME_INCREASE",
            "observation": (
                "Authentication volume is approximately "
                f"{events_vs_history:.2f} times its "
                "recent historical baseline."
            ),
            "interpretation": (
                "A sudden increase in activity may "
                "require investigation."
            )
        })

    if destinations_vs_history >= 2.0:
        findings.append({
            "category": "DESTINATION_EXPANSION",
            "observation": (
                "Destination count is approximately "
                f"{destinations_vs_history:.2f} times "
                "its recent historical baseline."
            ),
            "interpretation": (
                "Expanded destination access may be "
                "relevant to lateral-movement analysis."
            )
        })

    if new_destinations >= 20:
        findings.append({
            "category": "NEW_NETWORK_CONNECTIONS",
            "observation": (
                f"{new_destinations:,} previously unseen "
                "source-destination relationships."
            ),
            "interpretation": (
                "Review newly contacted computers "
                "for unusual access patterns."
            )
        })

    if new_user_pairs >= 20:
        findings.append({
            "category": "NEW_USER_DESTINATION_RELATIONSHIPS",
            "observation": (
                f"{new_user_pairs:,} newly observed "
                "user-destination relationships."
            ),
            "interpretation": (
                "Check whether these account-destination "
                "relationships are expected."
            )
        })

    if unique_users >= 1000:
        findings.append({
            "category": "BROAD_USER_ACTIVITY",
            "observation": (
                f"{unique_users:,} distinct user accounts "
                "were associated with this source computer."
            ),
            "interpretation": (
                "This may reflect a shared infrastructure "
                "system or unusual account activity."
            )
        })

    if unique_destinations >= 1000:
        findings.append({
            "category": "BROAD_DESTINATION_ACTIVITY",
            "observation": (
                f"{unique_destinations:,} destination "
                "computers were contacted."
            ),
            "interpretation": (
                "Determine whether the computer's "
                "network role explains this breadth."
            )
        })

    return findings


@app.get("/investigate/{alert_id}")
def investigate_alert(alert_id: str):

    alert = get_alert(alert_id)

    findings = build_investigation(alert)

    return {
        "alert_id": alert["alert_id"],
        "source_computer": alert["source_computer"],
        "dataset_day": alert["dataset_day"],
        "severity": alert["severity"],
        "anomaly_score": alert["anomaly_score"],
        "investigation_type": "RULE_BASED",
        "findings_count": len(findings),
        "findings": findings,
        "assessment": (
            "Behavioral anomalies identified. "
            "These findings are investigative leads, "
            "not confirmation of malicious activity."
        )
    }

@app.get("/investigate/graph/{alert_id}")
def investigate_with_langgraph(alert_id: str):
    # Retrieve the existing security alert
    alert = get_alert(alert_id)

    # Initialize LangGraph state
    initial_state = {
        "alert": alert,
        "findings": [],
        "assessment": "",
        "report": {}
    }

    # Execute the investigation workflow
    result = investigation_graph.invoke(initial_state)

    # Return the generated investigation report
    return result["report"]
