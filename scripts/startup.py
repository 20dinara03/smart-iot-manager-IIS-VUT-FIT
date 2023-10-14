import requests

server = "localhost:8000/api/v1"
username = "superuser"
password = "secret"


def add_groups():
    sets = [
        {
            "name": "admin",
            "permissions": [
                9,  # Can add user
                10,  # Can view permission
                12,  # Can update user
            ]
        },
        {
            "name": "broker",
            "permissions": [
                37  # Can add metric
            ]
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/groups/", json=s, auth=(username, password))
        print(response.status_code, response.text)


def add_users():
    sets = [
        {
            "username": "admin",
            "email": "admin@grafita.cz",
            "password": "secret",
            "groups": [
                1
            ]
        },
        {
            "username": "broker",
            "email": "broker@grafita.cz",
            "groups": [
                2
            ]
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/users/", json=s, auth=(username, password))
        print(response.status_code, response.text)


def add_device_types():
    sets = [
        {
            "name": "thermometer",
            "attributes": [
                "temperature"
            ]
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/device_types/", json=s, auth=(username, password))
        print(response.status_code, response.text)


def add_kpis():
    sets = [
        {
            "name": "higher",
            "value": [
                0
            ]
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/kpis/", json=s, auth=(username, password))
        print(response.status_code, response.text)


def add_device():
    sets = [
        {
            "name": "thermometer-1",
            "model": "FitKit",
            "location": "room-1",
            "device_type": 1,
            "created_by": 2,
            "value_min": -100,
            "value_max": 100,
            "default_kpi": 1
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/devices/", json=s, auth=(username, password))
        print(response.status_code, response.text)


def add_metrics():
    sets = [
        {
            "device": 1,
            "time": "2020-01-01T00:00:00Z",
            "value": 0,
            "attributes": "temperature",
        }
    ]
    for s in sets:
        response = requests.post(f"http://{server}/metrics/", json=s, auth=(username, password))
        print(response.status_code, response.text)


if __name__ == "__main__":
    add_groups()
    add_users()
    add_device_types()
    add_kpis()
    add_device()
    # add_metrics()
