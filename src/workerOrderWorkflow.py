import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.orderWorkflow import OrderWorkflow
from activities.orderActivities import order_received, order_validated, payment_charged

async def main():
    client = await Client.connect("localhost:7233")
    
    # Main worker for order processing
    order_worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow],
        activities=[order_received, order_validated, payment_charged],
    )

    
    print("Starting order worker...")
    order_worker_task = asyncio.create_task(order_worker.run())
    

    
    print("All workers started.")
    
    # Wait for both workers
    await asyncio.gather(order_worker_task)

if __name__ == "__main__":
    asyncio.run(main())
