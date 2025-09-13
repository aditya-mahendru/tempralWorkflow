from typing import Dict, Any
from util.flakyCall import flaky_call
from temporalio import activity,workflow
from util.dataObject import OrderObject
from typing import List

from util.db import PostgresDB
@activity.defn
async def order_received(order_data:List[str]) -> OrderObject:
    data = {"items": [{"sku": "ABC", "qty": 1}],"payment_id":order_data[1]}
    await flaky_call()
    pgDB = PostgresDB()
    query = f"""INSERT INTO orders (id, order_data, order_status)
        VALUES
        {order_data[0]}, {data}, 'Received'"""
    await pgDB.query_executor(query, hasReturn=False)
    return OrderObject(
        id=order_data[0], 
        data=data, 
        created_at=str(workflow.now()), 
        updated_at=str(workflow.now()), 
        payment_id=order_data[1], 
        shipping_address="")


@activity.defn
async def order_validated(order: OrderObject) -> bool:
    await flaky_call()
    pgDB = PostgresDB()
    query = f"""UPDATE orders SET 
    order_status = 'Validated',
    updated_at = CURRENT_TIMESTAMP
    where id  = {order.id}
    """
    await pgDB.query_executor(query,False)
    if not order.data.get("items"):
        return False
    return True



@activity.defn
async def payment_charged(order: OrderObject) -> Dict[str, Any]:
    await flaky_call()
    """Charge payment after simulating an error/timeout first.
    You must implement your own idempotency logic in the activity or here.
    """
    pgDb = PostgresDB()
    query =  f""" INSERT INTO payments (id, order_id, payment_status, amount)
    VALUES ({order.payment_id}, {order.id}, 1, {order.data.get("amount", 0)}) ON CONFLICT DO NOTHING
    """
    await pgDb.query_executor(query,False)
    query = f"""UPDATE orders SET 
    order_status = 'Charged',
    updated_at = CURRENT_TIMESTAMP
    where id  = {order.id}
    """
    await pgDb.query_executor(query,False)
    
    amount = sum(i.get("qty", 1) for i in order.data.get("items", []))
    return {"status": "charged", "amount": amount}

