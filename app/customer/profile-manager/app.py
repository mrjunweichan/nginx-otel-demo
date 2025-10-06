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
SERVICE_NAME = "customer-profile-manager"
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "customer"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/update-profile', methods=['POST'])
def update_profile():
    with tracer.start_as_current_span(
        "customer-profile-manager:update-profile",
        attributes={"endpoint.name": "update-profile"}
    ):
        response_text = "Response from customer-profile-manager at /update-profile\n"
        
        # Intra-team call: customer-verifier's /generate-auth-token (direct)
        with tracer.start_as_current_span("call-generate-auth-token"):
            try:
                resp = requests.get('http://app-customer-verifier:5000/generate-auth-token')
                response_text += f"Called generate-auth-token: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling generate-auth-token: {str(e)}\n"
        
        return response_text

@app.route('/search-profiles', methods=['GET'])
def search_profiles():
    with tracer.start_as_current_span(
        "customer-profile-manager:search-profiles",
        attributes={"endpoint.name": "search-profiles"}
    ):
        return "Response from customer-profile-manager at /search-profiles\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
