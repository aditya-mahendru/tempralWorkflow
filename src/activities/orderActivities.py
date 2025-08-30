from typing import Dict, Any
from util.flakyCall import flaky_call
from temporalio import activity
from util.dataObject import OrderObject
from datetime import datetime

@activity.defn
async def order_received(order_id: str) -> OrderObject:
    # await flaky_call()
    # TODO: Implement DB write: insert new order record
    return OrderObject(
        id=order_id, 
        data={"items": [{"sku": "ABC", "qty": 1}]}, 
        created_at=str(datetime.now()), 
        updated_at=str(datetime.now()), 
        payment_id="", 
        shipping_address="")


@activity.defn
async def order_validated(order: OrderObject) -> bool:
    # TODO: Implement DB read/write: fetch order, update validation status
    if not order.data.get("items"):
        return False
    return True



@activity.defn
async def payment_charged(order: OrderObject, payment_id: str, db) -> Dict[str, Any]:
    """Charge payment after simulating an error/timeout first.
    You must implement your own idempotency logic in the activity or here.
    """
    # await flaky_call()
    # TODO: Implement DB read/write: check payment record, insert/update payment status
    amount = sum(i.get("qty", 1) for i in order.data.get("items", []))
    return {"status": "charged", "amount": amount}

