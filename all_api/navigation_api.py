from fastapi import FastAPI
from pydantic import BaseModel
from navigation import pipeline
from navigation.self_navigation.distance_graph import juet_weighted_graph
from navigation.navigation_tools.close_coords import csd
from all_api.dashboard_api import (
    dashboard_command,
    get_kart_details
)
app = FastAPI()
class Coordinates(BaseModel):
    latitude: float
    longitude: float

# KART COORDINATES + HEADING
class KartCoordinates(BaseModel):
    latitude: float
    longitude: float
    heading: float

# ROUTE REQUEST
class RoutesRequest(BaseModel):
    marketplace: Coordinates
    kart: KartCoordinates
    delivery_point: Coordinates
    general_coordinates: Coordinates
# GENERAL KART COMMAND:
class GeneralRequest(BaseModel):
    open_kart: int
    closed_kart: int
# CREATE ROUTE

@app.post("/backend/coordinates/destinations")
def get_coordinates(data: RoutesRequest):
    marketplace = data.marketplace
    kart = data.kart
    delivery_point = data.delivery_point
    general_location = data.general_coordinates
    heading = kart.heading
    # CHECK DASHBOARD COMMAND
    if dashboard_command["command"] == "go":
        self_route_permission = 0
        manual_control = 0
    elif dashboard_command["command"] == "sc":
        self_route_permission = 1
        manual_control = 0
    else:
        self_route_permission = 0
        manual_control = 1
        manual_command = dashboard_command["command"]
    # CHECK SELF-ROUTE DEPENDENCY
    if csd(
        general_location,
        juet_weighted_graph["juet_coords"]
    ):
        # SELF ROUTE
        if self_route_permission:
            result = pipeline(
                marketplace,
                kart,
                delivery_point,
                heading,
                1
            )
        # MANUAL CONTROL
        elif manual_control:
            result = manual_command
        else:
            result = pipeline(
                marketplace,
                kart,
                delivery_point,
                heading,
                0
            )
    # KART OUTSIDE SELF-ROUTE AREA
    else:
        if manual_control:
            result = manual_command
        else:
            result = pipeline(
                marketplace,
                kart,
                delivery_point,
                heading,
                0
            )
    # GET KART DETAILS FROM DASHBOARD API
    kart_details = get_kart_details()
    # RETURN BOTH ROUTE + KART DETAILS
    return {
        "route": result,
        "kart_details": kart_details
    }