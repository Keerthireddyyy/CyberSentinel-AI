
"""
CyberSentinel AI
Rule-Based Security Investigation Engine

Analyzes authentication behavior and produces
evidence-based investigation findings.
"""


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

    # 1. High authentication volume
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

    # 2. Elevated failed login rate
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

    # 3. Authentication volume increase
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

    # 4. Destination expansion
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

    # 5. New network connections
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

    # 6. New user-destination relationships
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

    # 7. Broad user activity
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

    # 8. Broad destination activity
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
