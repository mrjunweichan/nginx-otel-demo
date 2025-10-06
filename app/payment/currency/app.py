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
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME")# "payments-currency"
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "payments"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/convert-currency', methods=['GET'])
def convert_currency():
    with tracer.start_as_current_span(
        "payments-currency:convert-currency",
        attributes={"endpoint.name": "convert-currency"}
    ):
        return "Response from payments-currency at /convert-currency\n"

@app.route('/get-exchange-rates', methods=['GET'])
def get_exchange_rates():
    with tracer.start_as_current_span(
        "payments-currency:get-exchange-rates",
        attributes={"endpoint.name": "get-exchange-rates"}
    ):
        return "Response from payments-currency at /get-exchange-rates\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
