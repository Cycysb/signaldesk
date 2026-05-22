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


def test_change_severity_updates_incident() -> None:
    incident = Incident.create(
        title="Checkout latency",
        description=None,
        severity=IncidentSeverity.SEV3,
        service_name="checkout-api",
        owner_team="payments",
    )

    incident.change_severity(IncidentSeverity.SEV1)

    assert incident.severity == IncidentSeverity.SEV1


def test_change_status_to_resolved_sets_resolved_at() -> None:
    incident = Incident.create(
        title="Checkout latency",
        description=None,
        severity=IncidentSeverity.SEV2,
        service_name="checkout-api",
        owner_team="payments",
    )

    incident.change_status(IncidentStatus.RESOLVED)

    assert incident.status == IncidentStatus.RESOLVED
    assert incident.resolved_at is not None


def test_resolved_incident_cannot_change_severity() -> None:
    incident = Incident.create(
        title="Checkout latency",
        description=None,
        severity=IncidentSeverity.SEV2,
        service_name="checkout-api",
        owner_team="payments",
    )

    incident.change_status(IncidentStatus.RESOLVED)

    try:
        incident.change_severity(IncidentSeverity.SEV1)
    except ValueError as exc:
        assert str(exc) == "Cannot change severity of a resolved incident"
    else:
        raise AssertionError("Expected ValueError")


def test_create_incident_records_incident_created_event() -> None:
    incident = Incident.create(
        title="Checkout latency",
        description=None,
        severity=IncidentSeverity.SEV2,
        service_name="checkout-api",
        owner_team="payments",
    )

    events = incident.pull_events()

    assert len(events) == 1
    assert events[0].event_type == "incident.created"
    assert events[0].aggregate_id == incident.id
    assert events[0].payload["severity"] == "sev2"


def test_pull_events_clears_events() -> None:
    incident = Incident.create(
        title="Checkout latency",
        description=None,
        severity=IncidentSeverity.SEV2,
        service_name="checkout-api",
        owner_team="payments",
    )

    first_pull = incident.pull_events()
    second_pull = incident.pull_events()

    assert len(first_pull) == 1
    assert second_pull == []
