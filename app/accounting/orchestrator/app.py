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
SERVICE_NAME = "accounting-orchestrator"

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "accounting"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    with tracer.start_as_current_span(
        "accounting-orchestrator:create-account",
        attributes={"endpoint.name": "create-account"}
    ):
        response_text = "Response from accounting-orchestrator at /create-account\n"
        
        # Inter-team call: Customer's /get-profile (via NGINX)
        with tracer.start_as_current_span("call-customer-get-profile"):
            try:
                # resp = requests.get('http://nginx-gateway:8080/api/customer/orchestrator/get-profile')
                resp = requests.get('http://app-customer-orchestrator:5000/get-profile') # To view graph
                response_text += f"Called get-profile: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling get-profile: {str(e)}\n"
        
        # Intra-team call: accounting-ledger's /init-ledger (direct)
        with tracer.start_as_current_span("call-init-ledger"):
            try:
                resp = requests.get('http://app-accounting-ledger:5000/init-ledger')
                response_text += f"Called init-ledger: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling init-ledger: {str(e)}\n"
        
        return response_text

@app.route('/close-account', methods=['POST'])
def close_account():
    with tracer.start_as_current_span(
        "accounting-orchestrator:close-account",
        attributes={"endpoint.name": "close-account"}
    ):
        response_text = "Response from accounting-orchestrator at /close-account\n"
        
        # Intra-team call: accounting-ledger's /log-transaction-history (direct)
        with tracer.start_as_current_span("call-log-transaction-history"):
            try:
                resp = requests.get('http://app-accounting-ledger:5000/log-transaction-history')
                response_text += f"Called log-transaction-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling log-transaction-history: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
