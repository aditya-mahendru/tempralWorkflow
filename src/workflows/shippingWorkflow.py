from datetime import timedelta
from typing import Dict, Any
from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from activities.shippingActivities import package_prepared, carrier_dispatched
from util.dataObject import OrderObject

@workflow.defn
class ShippingWorkflow:
    def __init__(self):
        self._package_status = "pending"
        self._dispatch_status = "pending"
        self._dispatch_failed_reason = None

    @workflow.run
    async def run(self, order: OrderObject) -> Dict[str, Any]:
        """Main shipping workflow execution"""
        try:
            # Prepare package
            self._package_status = await workflow.execute_activity(
                package_prepared,
                order,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
                task_queue="shipping-tq"
            )
            
            # Dispatch carrier with retry policy
            self._dispatch_status = await workflow.execute_activity(
                carrier_dispatched,
                order,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(minutes=2),
                    maximum_attempts=3,
                ),
                task_queue="shipping-tq"
            )
            
            return {
                "status": "shipped",
                "package_status": self._package_status,
                "dispatch_status": self._dispatch_status,
                "order_id": order.id
            }
            
        except Exception as e:
            # Signal back to parent workflow about dispatch failure
            self._dispatch_failed_reason = str(e)
            workflow.upsert_search_attributes({
                "DispatchFailed": [self._dispatch_failed_reason]
            })
            raise

    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Query current shipping status"""
        return {
            "package_status": self._package_status,
            "dispatch_status": self._dispatch_status,
            "dispatch_failed_reason": self._dispatch_failed_reason
        }

    @workflow.signal
    def retry_dispatch(self):
        """Signal to retry dispatch (can be called by parent)"""
        self._dispatch_status = "pending"
        self._dispatch_failed_reason = None
