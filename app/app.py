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
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "default-service")
OTEL_EXPORTER_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318/v1/traces")
HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
PORT = int(os.getenv("SERVICE_PORT", "5000"))
CONFIG_FILE = os.getenv("CONFIG_FILE", "/app/config.json")

# Load routes from config file
try:
    with open(CONFIG_FILE, 'r') as f:
        ROUTES_CONFIG = json.load(f).get("routes", {})
except (FileNotFoundError, json.JSONDecodeError):
    ROUTES_CONFIG = {}

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Dynamic route handler
def create_route_handler(route_name, calls=[]):
    def handler():
        with tracer.start_as_current_span(f"{SERVICE_NAME}:{route_name.lstrip('/')}"):
            response_text = f"Response from {SERVICE_NAME} at {route_name}\n"
            for call in calls:
                service, endpoint = call["service"], call["endpoint"]
                with tracer.start_as_current_span(f"call-{service}"):
                    try:
                        resp = requests.get(endpoint)
                        response_text += f"Called {service}: {resp.text}\n"
                    except requests.RequestException as e:
                        response_text += f"Error calling {service}: {str(e)}\n"
            return response_text
    handler.__name__ = f"handler_{route_name.replace('/', '_')}"
    return handler

# Register routes dynamically
for route, config in ROUTES_CONFIG.items():
    app.route(route, methods=config.get("methods", ["GET"]))(create_route_handler(
        route, config.get("calls", [])
    ))

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
