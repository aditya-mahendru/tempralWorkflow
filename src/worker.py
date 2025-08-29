import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.helloFlow import SayHelloWorkflow
from activities.helloWorld import greet

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[SayHelloWorkflow],
        activities=[greet],
        )
    print("Worker started.")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
