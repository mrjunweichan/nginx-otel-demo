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
SERVICE_NAME = "risk-orchestrator"

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

@app.route('/validate-transaction', methods=['GET', 'POST'])
def validate_transaction():
    with tracer.start_as_current_span(
        "risk-orchestrator:validate-transaction",
        attributes={"endpoint.name": "validate-transaction"}
    ):
        response_text = "Response from risk-orchestrator at /validate-transaction\n"
        
        # Intra-team call: risk-analyzer's /check-fraud (direct)
        with tracer.start_as_current_span("call-check-fraud"):
            try:
                resp = requests.get('http://app-risk-analyzer:5000/check-fraud')
                response_text += f"Called check-fraud: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling check-fraud: {str(e)}\n"
        
        return response_text

@app.route('/generate-report', methods=['GET', 'POST'])
def generate_report():
    with tracer.start_as_current_span(
        "risk-orchestrator:generate-report",
        attributes={"endpoint.name": "generate-report"}
    ):
        response_text = "Response from risk-orchestrator at /generate-report\n"
        
        # Intra-team call: risk-manager's /flag-anomaly (direct)
        with tracer.start_as_current_span("call-flag-anomaly"):
            try:
                resp = requests.get('http://app-risk-manager:5000/flag-anomaly')
                response_text += f"Called flag-anomaly: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling flag-anomaly: {str(e)}\n"
        
        return response_text

@app.route('/block-transaction', methods=['POST'])
def block_transaction():
    with tracer.start_as_current_span(
        "risk-orchestrator:block-transaction",
        attributes={"endpoint.name": "block-transaction"}
    ):
        response_text = "Response from risk-orchestrator at /block-transaction\n"
        
        # Intra-team call: risk-analyzer's /check-fraud (direct)
        with tracer.start_as_current_span("call-check-fraud"):
            try:
                resp = requests.get('http://app-risk-analyzer:5000/check-fraud')
                response_text += f"Called check-fraud: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling check-fraud: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
