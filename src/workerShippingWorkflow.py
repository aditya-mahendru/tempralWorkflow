import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.shippingWorkflow import ShippingWorkflow
from activities.shippingActivities import package_prepared, carrier_dispatched

async def main():
    client = await Client.connect("localhost:7233")

    # Separate worker for shipping operations
    shipping_worker = Worker(
        client,
        task_queue="shipping-tq",
        workflows=[ShippingWorkflow],
        activities=[package_prepared, carrier_dispatched],
    )
    
    
    print("Starting shipping worker...")
    shipping_worker_task = asyncio.create_task(shipping_worker.run())
    
    print("All workers started.")
    
    # Wait for both workers
    await asyncio.gather(shipping_worker_task)

if __name__ == "__main__":
    asyncio.run(main())
