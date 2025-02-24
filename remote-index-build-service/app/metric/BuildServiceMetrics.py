#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from metric.CloudWatchMetricsExporter import CloudWatchMetricsExporter

class BuildServiceMetrics():
    def __init__(self):
        # Create the custom CloudWatch exporter
        self.cloudwatch_exporter = CloudWatchMetricsExporter(namespace="POCMetrics")

        # Create a PeriodicExportingMetricReader to export metrics at set intervals
        self.reader = PeriodicExportingMetricReader(self.cloudwatch_exporter, export_interval_millis=10000, export_timeout_millis=3000)  # Export every 10 seconds

        # Initialize MeterProvider with reader
        self.meter_provider = MeterProvider(metric_readers=[self.reader])

        self.meter = self.meter_provider.get_meter("my-meter")

        self.build_api_4xx_error_count = self.meter.create_counter("build_api_4xx_error_count", description="Build API 4xx Error Count")
        self.build_api_5xx_error_count = self.meter.create_counter("build_api_5xx_error_count", description="Build API 5xx Error Count")

        self.cancel_api_4xx_error_count = self.meter.create_counter("cancel_api_4xx_error_count", description="Cancel API 4xx Error Count")
        self.cancel_api_5xx_error_count = self.meter.create_counter("cancel_api_5xx_error_count", description="Cancel API 5xx Error Count")

        self.status_api_4xx_error_count = self.meter.create_counter("status_api_4xx_error_count", description="Status API 4xx Error Count")
        self.status_api_5xx_error_count = self.meter.create_counter("status_api_5xx_error_count", description="Status API 5xx Error Count")

        self.build_api_latency = self.meter.create_histogram("build_api_latency", description="Build API Request Latency")
        self.cancel_api_latency = self.meter.create_histogram("cancel_api_latency", description="Cancel API Request Latency")
        self.status_api_latency = self.meter.create_histogram("status_api_latency", description="Status API Request Latency")
