from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Tracer, Span
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider, Meter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def create_metrcis_meter_counter() -> Meter:
    exporter = OTLPMetricExporter(endpoint="http://127.0.0.1:4317", insecure=True)
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader])

    return provider.get_meter(__name__)


def init_otel(service_name: str) -> Tracer:
    resource = Resource(attributes={
        "service.name": service_name,
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_exporter = OTLPSpanExporter(endpoint="http://127.0.0.1:4317", insecure=True)

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )

    tracer = trace.get_tracer(__name__)

    return tracer


def to_span(span: any) -> Span:
    cmp: Span = span
    return cmp
