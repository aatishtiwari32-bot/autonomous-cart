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
# General kart commands
class GeneralRequest(BaseModel):
    open_kart: int
    closed_kart: int
# Create routes
@app.get("/backend/coordinates/destinations")
def get_coordinates(data: RoutesRequest, Data : KartCoordinates):
    marketplace = data.marketplace
    kart = data.kart
    delivery_point = data.delivery_point
    heading = Data.heading
    result = pipeline(
        marketplace,
        kart,
        delivery_point, 
        heading 
    )
    return result
