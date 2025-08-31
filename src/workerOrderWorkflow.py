import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.orderWorkflow import OrderWorkflow
from workflows.shippingWorkflow import ShippingWorkflow
from activities.orderActivities import order_received, order_validated, payment_charged
from activities.shippingActivities import package_prepared, carrier_dispatched

async def main():
    client = await Client.connect("localhost:7233")
    
    # Main worker for order processing
    order_worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow],
        activities=[order_received, order_validated, payment_charged],
    )
    
    # Separate worker for shipping operations
    # shipping_worker = Worker(
    #     client,
    #     task_queue="shipping-tq",
    #     workflows=[ShippingWorkflow],
    #     activities=[package_prepared, carrier_dispatched],
    # )
    
    print("Starting order worker...")
    order_worker_task = asyncio.create_task(order_worker.run())
    
    # print("Starting shipping worker...")
    # shipping_worker_task = asyncio.create_task(shipping_worker.run())
    
    print("All workers started.")
    
    # Wait for both workers
    await asyncio.gather(order_worker_task)

if __name__ == "__main__":
    asyncio.run(main())
