from incident_api.domain.incident import Incident, IncidentSeverity, IncidentStatus


def test_create_incident_defaults_to_open_status() -> None:
    incident = Incident.create(
        title="Checkout API latency spike",
        description="p95 latency is above threshold",
        severity=IncidentSeverity.SEV2,
        service_name="checkout-api",
        owner_team="payments",
    )

    assert incident.id is not None
    assert incident.title == "Checkout API latency spike"
    assert incident.status == IncidentStatus.OPEN
    assert incident.severity == IncidentSeverity.SEV2
    assert incident.service_name == "checkout-api"
    assert incident.owner_team == "payments"
    assert incident.resolved_at is None
