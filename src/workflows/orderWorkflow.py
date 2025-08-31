from datetime import timedelta
from typing import Dict, Any, Optional
from temporalio import workflow
from temporalio.common import RetryPolicy
from activities.orderActivities import order_received, order_validated, payment_charged
from workflows.shippingWorkflow import ShippingWorkflow
from util.dataObject import OrderObject
from temporalio.workflow import ParentClosePolicy


@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self._order_data: Optional[OrderObject] = None
        self._validation_result: Optional[bool] = None
        self._payment_result: Optional[Dict[str, Any]] = None
        self._shipping_result: Optional[Dict[str, Any]] = None
        self._is_cancelled = False
        self._shipping_address: Optional[str] = None
        self._manual_review_completed = False
        self._workflow_status = "started"

    @workflow.run
    async def run(self, order_id: str, initial_address: str = "Default Address") -> Dict[str, Any]:
        """Main order workflow execution"""
        try:
            self._shipping_address = initial_address
            self._workflow_status = "processing"
            
            # Step 1: Receive Order
            self._order_data = await workflow.execute_activity(
                order_received,
                order_id,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                )
            )
            
            # Check for cancellation after order received
            if self._is_cancelled:
                return {"status": "cancelled", "reason": "Order cancelled by user"}
            
            # Step 2: Validate Order
            self._validation_result = await workflow.execute_activity(
                order_validated,
                self._order_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                )
            )
            
            if not self._validation_result:
                return {"status": "failed", "reason": "Order validation failed"}
            
            # Check for cancellation after validation
            if self._is_cancelled:
                return {"status": "cancelled", "reason": "Order cancelled by user"}
            
            # Step 3: Timer for Manual Review (simulated human approval)
            self._workflow_status = "awaiting_manual_review"
            await workflow.wait_condition(
                lambda: self._manual_review_completed,
                timeout=timedelta(hours=24)  # 24 hour timeout for manual review
            )
            
            # Check for cancellation after manual review
            if self._is_cancelled:
                return {"status": "cancelled", "reason": "Order cancelled by user"}
            
            # Step 4: Charge Payment
            self._workflow_status = "processing_payment"
            payment_id = f"PAY-{order_id}-{workflow.info().workflow_id}"
            self._payment_result = await workflow.execute_activity(
                payment_charged,
                args=[self._order_data, payment_id, "mock_db"],  # db parameter - replace with actual DB connection
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(minutes=2),
                    maximum_attempts=3,
                )
            )
            
            # Check for cancellation after payment
            if self._is_cancelled:
                return {"status": "cancelled", "reason": "Order cancelled by user"}
            
            # Step 5: Execute Shipping Workflow (Child Workflow)
            self._workflow_status = "shipping"
            # shipping_order = {
                # **self._order_data,
            #     "shipping_address": self._shipping_address,
            #     "payment_id": payment_id
            # }
            
            self._shipping_result = await workflow.execute_child_workflow(
                ShippingWorkflow.run,
                self._order_data,
                id=f"shipping-{order_id}",
                task_queue="shipping-tq",
                # start_to_close_timeout=timedelta(hours=2),
                # retry_policy=RetryPolicy(
                #     initial_interval=timedelta(minutes=1),
                #     maximum_interval=timedelta(minutes=10),
                #     maximum_attempts=3,
                # ),
                parent_close_policy=ParentClosePolicy.ABANDON
                )
            
            
            self._workflow_status = "completed"
            return {
                "status": "completed",
                "order_id": order_id,
                "order_data": self._order_data,
                "payment_result": self._payment_result,
                "shipping_result": self._shipping_result,
                "shipping_address": self._shipping_address
            }
            
        except Exception as e:
            self._workflow_status = "failed"
            return {
                "status": "failed",
                "error": str(e),
                "order_id": order_id
            }

    @workflow.signal
    def cancel_order(self):
        """Signal to cancel the order before shipment"""
        self._is_cancelled = True
        self._workflow_status = "cancelled"

    @workflow.signal
    def update_address(self, new_address: str):
        """Signal to update shipping address prior to dispatch"""
        self._shipping_address = new_address

    @workflow.signal
    def complete_manual_review(self):
        """Signal to complete manual review and proceed to payment"""
        self._manual_review_completed = True
        self._workflow_status = "manual_review_completed"

    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Query current workflow status"""
        return {
            "workflow_status": self._workflow_status,
            "order_data": self._order_data,
            "validation_result": self._validation_result,
            "payment_result": self._payment_result,
            "shipping_result": self._shipping_result,
            "is_cancelled": self._is_cancelled,
            "shipping_address": self._shipping_address,
            "manual_review_completed": self._manual_review_completed
        }
