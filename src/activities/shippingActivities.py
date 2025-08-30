from typing import Dict, Any
from temporalio import activity
from util.flakyCall import flaky_call
from util.dataObject import OrderObject


@activity.defn
async def order_shipped(order: OrderObject) -> str:
    # await flaky_call()
    # TODO: Implement DB write: update order status to shipped
    return "Shipped"

@activity.defn
async def package_prepared(order: OrderObject) -> str:
    # await flaky_call()
    # TODO: Implement DB write: mark package prepared in DB
    return "Package ready"

@activity.defn
async def carrier_dispatched(order: OrderObject) -> str:
    # await flaky_call()
    # TODO: Implement DB write: record carrier dispatch status
    return "Dispatched"
