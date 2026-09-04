from fastapi import FastAPI
from pydantic import BaseModel
from navigation.movement import movement
from map_navigation import pipeline 
app = FastAPI()
# Normal geographic coordinates
class Coordinates(BaseModel):
    latitude: float
    longitude: float
# Kart coordinates + heading
class KartCoordinates(BaseModel):
    latitude: float
    longitude: float
    heading: float
# Route request
class RoutesRequest(BaseModel):
    marketplace: Coordinates
    kart: KartCoordinates
    delivery_point: Coordinates
    general_coordinates : Coordinates
# General kart commands
class GeneralRequest(BaseModel):
    open_kart: int
    closed_kart: int
# Create routes
@app.post("/backend/coordinates/destinations")
def get_coordinates(data: RoutesRequest, Data : KartCoordinates):
    marketplace = data.marketplace
    kart = Data.kart
    delivery_point = data.delivery_point
    general_location = data.general_coordinates
    heading = Data.heading
    result = pipeline(
        marketplace,
        kart,
        delivery_point, 
        heading,
        general_location
    )
    return result
