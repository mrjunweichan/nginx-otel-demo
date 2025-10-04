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
SERVICE_NAME = "customer-orchestrator"

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "customer"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    with tracer.start_as_current_span(
        "customer-orchestrator:register-user",
        attributes={"endpoint.name": "register-user"}
    ):
        response_text = "Response from customer-orchestrator at /register-user\n"
        
        # Intra-team call: customer-verifier's /verify-kyc (direct)
        with tracer.start_as_current_span("call-verify-kyc"):
            try:
                resp = requests.get('http://app-customer-verifier:5000/verify-kyc')
                response_text += f"Called verify-kyc: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling verify-kyc: {str(e)}\n"
        
        return response_text

@app.route('/get-profile', methods=['GET'])
def get_profile():
    with tracer.start_as_current_span(
        "customer-orchestrator:get-profile",
        attributes={"endpoint.name": "get-profile"}
    ):
        return "Response from customer-orchestrator at /get-profile\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
