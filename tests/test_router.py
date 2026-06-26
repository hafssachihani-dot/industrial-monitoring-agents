from src.agents.router import smart_router


def test_router_normal_case():
    telemetry = {
        "machine_id": "MACHINE-01",
        "temperature": 65,
        "vibration": 2.5,
        "oil_pressure": 3.2,
        "rpm": 1450,
    }

    decision = smart_router.route(telemetry)

    assert decision["route"] == "NORMAL"


def test_router_critical_case():
    telemetry = {
        "machine_id": "MACHINE-01",
        "temperature": 92,
        "vibration": 8.4,
        "oil_pressure": 3.2,
        "rpm": 1450,
    }

    decision = smart_router.route(telemetry)

    assert decision["route"] == "CRITICAL"
    assert "Température critique" in decision["reasons"]
    assert "Vibration critique" in decision["reasons"]

