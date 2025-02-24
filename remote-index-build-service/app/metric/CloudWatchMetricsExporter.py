#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

import time
import boto3
from opentelemetry.sdk.metrics._internal.point import Sum, Gauge, Histogram
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult, MetricsData
from opentelemetry.sdk.metrics.export import AggregationTemporality
from typing import Dict

# Custom CloudWatch exporter class
class CloudWatchMetricsExporter(MetricExporter):
    def __init__(self,
                 namespace: str,
                 preferred_temporality: Dict[type, AggregationTemporality] = None,
                 preferred_aggregation: Dict[
                     type, "opentelemetry.sdk.metrics.view.Aggregation"
                 ] = None
                 ):
        super().__init__(
            preferred_temporality=preferred_temporality,
            preferred_aggregation=preferred_aggregation,
        )
        self.namespace = namespace
        self.client = boto3.client(
            'cloudwatch',
            region_name="us-east-1",
            aws_access_key_id='',
            aws_secret_access_key='',
            aws_session_token=''
        )
        self.max_retries = 3

    def export(
            self,
            metrics_data: MetricsData,
            timeout_millis: float = 10_000,
            **kwargs,
    ) -> MetricExportResult:
        deadline_ns = time.time_ns() + timeout_millis * 10 ** 6

        retries = 0

        # TO DO: Implement error retry with exponential backoff + timeout for export method
        # while retries < self.max_retries:
        #     current_ts = time.time_ns()
        #     if current_ts >= deadline_ns:
        #         raise Exception(
        #             "Timed out while exporting metrics"
        #         )
        print("EXPORTING to CloudWatch")
        try:
            metric_data_batch = []

            print(metrics_data.resource_metrics[0].to_json())
            for resource_metric in metrics_data.resource_metrics:
                for scope_metric in resource_metric.scope_metrics:
                    for metric in scope_metric.metrics:

                        metric_dict = {
                            'MetricName': metric.name,
                            'Dimensions': [{'Name': 'MetricScope', 'Value': 'ServiceMetric'}],
                        }

                        #counter
                        if isinstance(metric.data, Sum):
                            metric_dict['Value'] = metric.data.data_points[0].value
                            metric_dict['Unit'] = 'Count'
                            metric_data_batch.append(metric_dict.copy())
                        #gauge
                        elif isinstance(metric.data, Gauge):
                            metric_dict['Value'] = metric.data.data_points[0].value
                            metric_dict['Unit'] = 'Percent'
                            metric_data_batch.append(metric_dict.copy())
                        #histogram
                        elif isinstance(metric.data, Histogram):
                            sum = metric.data.data_points[0].sum

                            metric_dict['Value'] = sum
                            metric_dict['Unit'] = 'Seconds'
                            metric_data_batch.append(metric_dict.copy())


            if metric_data_batch:
                self.client.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=metric_data_batch
                )
                print(f"Successfully sent {len(metric_data_batch)} metrics to CloudWatch.")

            return MetricExportResult.SUCCESS
        except Exception as e:
            print(f"Failed to export to CloudWatch: {e}")
            return MetricExportResult.FAILURE

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        """Force the exporter to flush any buffered metrics data."""
        print("Forcing flush...")
        return True

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        """Perform cleanup when shutting down the exporter."""
        print("Shutting down CloudWatch exporter.")
        self.client = None  #Clean up the CloudWatch client.
