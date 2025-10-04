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
SERVICE_NAME = "risk-manager"

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "risk"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/flag-anomaly', methods=['GET', 'POST'])
def flag_anomaly():
    with tracer.start_as_current_span(
        "risk-manager:flag-anomaly",
        attributes={"endpoint.name": "flag-anomaly"}
    ):
        response_text = "Response from risk-manager at /flag-anomaly\n"
        
        # Intra-team call: risk-orchestrator's /generate-report (direct)
        with tracer.start_as_current_span("call-generate-report"):
            try:
                resp = requests.get('http://app-risk-orchestrator:5000/generate-report')
                response_text += f"Called generate-report: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling generate-report: {str(e)}\n"
        
        return response_text

@app.route('/review-flags', methods=['GET'])
def review_flags():
    with tracer.start_as_current_span(
        "risk-manager:review-flags",
        attributes={"endpoint.name": "review-flags"}
    ):
        return "Response from risk-manager at /review-flags\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
