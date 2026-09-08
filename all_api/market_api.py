from fastapi import FastAPI
from pydantic import BaseModel
from marketplaces import 

app = FastAPI()
class market_info(BaseModel):
    market_placeCoords : json
    
class MarketGoods(BaseModel):
    goods: str
    stock: int
class OrderedGoods(BaseModel):
    marketplace_id: int
    good: str
    quantity: int
market_goods = {
    101: [
        {
            "goods": "Paracetamol",
            "stock": 50
        },
        {
            "goods": "Soframycin",
            "stock": 20
        },
        {
            "goods": "Bandage",
            "stock": 35
        }
    ]
}

