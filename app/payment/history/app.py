import os
import json
from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

app = Flask(__name__)

# Parameterized configuration
SERVICE_NAME = "payments-history"

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "payments"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/record-payment-history', methods=['GET'])
def record_payment_history():
    with tracer.start_as_current_span(
        "payments-history:record-payment-history",
        attributes={"endpoint.name": "record-payment-history"}
    ):
        return "Response from payments-history at /record-payment-history\n"

@app.route('/audit-payments', methods=['GET'])
def audit_payments():
    with tracer.start_as_current_span(
        "payments-history:audit-payments",
        attributes={"endpoint.name": "audit-payments"}
    ):
        return "Response from payments-history at /audit-payments\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
