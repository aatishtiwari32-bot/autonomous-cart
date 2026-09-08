from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
# COORDINATES

class Coordinates(BaseModel):
    latitude: float
    longitude: float
# KART PARAMETERS


class KartParameters(BaseModel):
    camera_url: str
    kart_coordinates: Coordinates
    marketplace: Coordinates
    delivery_point: Coordinates
# DASHBOARD COMMAND TYPE

class DashboardCommandType(BaseModel):
    manual: int = 0
    google_route: int = 0
    self_route: int = 0
# SELF ROUTE
class SelfRoute(BaseModel):
    self: int = 0
# MANUAL CONTROL
class ManualControl(BaseModel):
    control_command: str = ""
# KART DETAILS
class KartDetails(BaseModel):
    kart_info: KartParameters
# SHARED DASHBOARD COMMAND
dashboard_command = {
    "command": "go"
}
# SHARED KART DETAILS
kart_details = None
# DASHBOARD CONTROL APi
@app.post("/dashboard/control")
def getcontrol(
    data: DashboardCommandType,
    manual_data: ManualControl
):
    if data.manual:
        dashboard_command["command"] = manual_data.control_command
    elif data.google_route:
        dashboard_command["command"] = "go"
    elif data.self_route:
        dashboard_command["command"] = "sc"
    return dashboard_command
# UPDATE KART DETAILS

def update_kart_details(data: KartDetails):
    global kart_details
    kart_details = data
    return kart_details
# GET KART DETAILS
def get_kart_details():
    return kart_details
# KART DETAILS API
@app.post("/dashboard/kart-details")
def set_kart_details(data: KartDetails):
    return update_kart_details(data)
@app.get("/dashboard/kart-details")
def get_kart_details_api():
    return get_kart_details()