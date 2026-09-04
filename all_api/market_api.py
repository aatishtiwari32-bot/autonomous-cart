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
@app.get("/marketplaces/{marketplace_id}/goods")
def show_goods(marketplace_id: int):
    return {
        "marketplace_id": marketplace_id,
        "goods": market_goods.get(
            marketplace_id,
            []
        )
    }
@app.post("/marketplaces/order")
def order_goods(data: OrderedGoods):

    return {
        "marketplace_id": data.marketplace_id,
        "good": data.good,
        "quantity": data.quantity,
        "status": "ORDER_RECEIVED"
    }
