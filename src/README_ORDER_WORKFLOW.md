# Order Workflow System

This system implements a comprehensive order processing workflow using Temporal, featuring signals, timers, child workflows, retries, and separate task queues.

## Architecture Overview

### OrderWorkflow (Parent Workflow)
- **Task Queue**: `order-tq`
- **Activities**: `ReceiveOrder` → `ValidateOrder` → `Timer: ManualReview` → `ChargePayment` → `ShippingWorkflow`

### ShippingWorkflow (Child Workflow)
- **Task Queue**: `shipping-tq`
- **Activities**: `PreparePackage` → `DispatchCarrier`
- **Parent Notification**: Signals back to parent on dispatch failure

## Features

### 1. Signals
- **`CancelOrder`**: Cancels the order before shipment
- **`UpdateAddress`**: Updates shipping address prior to dispatch
- **`CompleteManualReview`**: Completes manual review to proceed to payment

### 2. Timer (Manual Review)
- Simulates human approval process
- 24-hour timeout for manual review
- Workflow waits at this step until manually approved

### 3. Retries
- All activities include retry policies
- Configurable retry intervals and maximum attempts
- Exponential backoff for failed operations

### 4. Child Workflow
- `ShippingWorkflow` runs as a separate workflow
- Own task queue for isolation
- Can signal back to parent on failures

### 5. Task Queue Isolation
- **`order-tq`**: Order processing activities
- **`shipping-tq`**: Shipping-specific activities

## Workflow States

1. **`started`**: Workflow initialization
2. **`processing`**: Order received and being processed
3. **`awaiting_manual_review`**: Waiting for human approval
4. **`manual_review_completed`**: Review completed, proceeding to payment
5. **`processing_payment`**: Processing payment
6. **`shipping`**: Executing shipping workflow
7. **`completed`**: Workflow successfully completed
8. **`cancelled`**: Order cancelled by user
9. **`failed`**: Workflow failed due to error

## Usage Examples

### Starting a Workflow
```python
from temporalio.client import Client
from workflows.orderWorkflow import OrderWorkflow

client = await Client.connect("localhost:7233")
handle = await client.start_workflow(
    OrderWorkflow.run,
    "ORDER-123",
    "123 Main St, City, State 12345",
    id="order-123",
    task_queue="order-tq",
)
```

### Sending Signals
```python
# Cancel the order
await handle.signal(OrderWorkflow.cancel_order)

# Update shipping address
await handle.signal(OrderWorkflow.update_address, "New Address")

# Complete manual review
await handle.signal(OrderWorkflow.complete_manual_review)
```

### Querying Status
```python
status = await handle.query(OrderWorkflow.get_status)
print(f"Current status: {status['workflow_status']}")
```

### Getting Results
```python
result = await handle.result()
print(f"Workflow result: {result}")
```

## Running the System

### 1. Start Temporal Server
```bash
# Using Docker Compose (if available)
docker-compose up -d

# Or start Temporal server manually
temporal server start-dev
```

### 2. Start Workers
```bash
cd src
python worker.py
```

### 3. Run Demo
```bash
python demo_order_workflow.py
```

## Activity Details

### Order Activities
- **`order_received`**: Creates order record
- **`order_validated`**: Validates order items
- **`payment_charged`**: Processes payment with idempotency

### Shipping Activities
- **`package_prepared`**: Prepares package for shipping
- **`carrier_dispatched`**: Dispatches to shipping carrier

## Error Handling

- **Retry Policies**: Automatic retries with exponential backoff
- **Failure Signals**: Child workflow signals back to parent on failures
- **Cancellation**: Orders can be cancelled at any point before shipping
- **Timeout Handling**: Configurable timeouts for all operations

## Monitoring and Observability

- **Search Attributes**: Dispatch failures are recorded as search attributes
- **Status Queries**: Real-time workflow status queries
- **Signal History**: All signals are recorded and queryable
- **Child Workflow Tracking**: Full visibility into child workflow execution

## Best Practices

1. **Always check cancellation state** after long-running operations
2. **Use appropriate timeouts** for different activity types
3. **Implement idempotency** in payment and order activities
4. **Handle child workflow failures** gracefully
5. **Use separate task queues** for different concerns
6. **Implement proper error handling** and retry logic

## Troubleshooting

### Common Issues
1. **Workflow stuck in manual review**: Use `complete_manual_review` signal
2. **Shipping failures**: Check child workflow logs and retry policies
3. **Payment timeouts**: Verify payment service connectivity
4. **Task queue issues**: Ensure workers are running on correct queues

### Debug Commands
```python
# Get workflow history
history = await handle.fetch_history()

# Get workflow status
status = await handle.query(OrderWorkflow.get_status)

# Describe workflow
description = await handle.describe()
```
