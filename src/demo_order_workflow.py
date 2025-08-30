import asyncio
import time
from temporalio.client import Client
from workflows.orderWorkflow import OrderWorkflow
import uuid



async def demo_order_workflow():
    """Demonstrate the OrderWorkflow with various signals and scenarios"""
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Start the order workflow
    order_id = str(uuid.uuid4())
    print(f"Starting order workflow for order: {order_id}")
    
    handle = await client.start_workflow(
        "OrderWorkflow",
        args=[order_id,"123 Main St, City, State 12345"],
        id=f"order-{order_id}",
        task_queue="order-tq",
    )
    
    print(f"Workflow started with ID: {handle.id}")
    
    # Wait a bit for the workflow to start
    await asyncio.sleep(2)
    
    # Query the workflow status
    status = await handle.query(OrderWorkflow.get_status)
    print(f"Initial status: {status['workflow_status']}")
    
    # Wait for manual review phase
    print("Waiting for workflow to reach manual review phase...")
    while True:
        status = await handle.query(OrderWorkflow.get_status)
        if status['workflow_status'] == 'awaiting_manual_review':
            print("Workflow is now awaiting manual review!")
            break
        await asyncio.sleep(1)
    
    # Demonstrate address update signal
    print("Updating shipping address...")
    await handle.signal(OrderWorkflow.update_address, "456 Oak Ave, New City, State 54321")
    
    # Complete manual review to proceed
    print("Completing manual review...")
    await handle.signal(OrderWorkflow.complete_manual_review)
    
    # Wait for completion
    print("Waiting for workflow completion...")
    result = await handle.result()
    
    print(f"Workflow completed with result: {result}")


async def demo_cancellation():
    """Demonstrate order cancellation"""
    
    client = await Client.connect("localhost:7233")
    
    order_id = f"CANCEL-{int(time.time())}"
    print(f"Starting order workflow for cancellation demo: {order_id}")
    
    handle = await client.start_workflow(
        "OrderWorkflow",
        [order_id,"789 Cancel St, City, State 12345"],  
        id=f"cancel-{order_id}",
        task_queue="order-tq",
    )
    
    print(f"Cancellation demo workflow started with ID: {handle.id}")
    
    # Wait for workflow to start
    await asyncio.sleep(2)
    
    # Cancel the order immediately
    print("Cancelling the order...")
    await handle.signal(OrderWorkflow.cancel_order)
    
    # Wait for cancellation
    result = await handle.result()
    print(f"Workflow cancelled with result: {result}")


async def main():
    """Run the demo scenarios"""
    print("=== Order Workflow Demo ===")
    print("This demo shows:")
    print("1. Order workflow execution with manual review timer")
    print("2. Address update signal")
    print("3. Manual review completion signal")
    print("4. Child workflow execution (ShippingWorkflow)")
    print("5. Order cancellation scenario")
    print()
    
    try:
        # Run the main demo
        await demo_order_workflow()
        print("\n" + "="*50 + "\n")
        
        # Run the cancellation demo
        await demo_cancellation()
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        print("Make sure Temporal server is running and workers are started")


if __name__ == "__main__":
    asyncio.run(main())
