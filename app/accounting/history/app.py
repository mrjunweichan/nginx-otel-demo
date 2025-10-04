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
SERVICE_NAME = "accounting-history"

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

@app.route('/list-transactions', methods=['GET'])
def list_transactions():
    with tracer.start_as_current_span(
        "accounting-history:list-transactions",
        attributes={"endpoint.name": "list-transactions"}
    ):
        response_text = "Response from accounting-history at /list-transactions\n"
        
        # Intra-team call: accounting-ledger's /log-transaction-history (direct)
        with tracer.start_as_current_span("call-log-transaction-history"):
            try:
                resp = requests.get('http://app-accounting-ledger:5000/log-transaction-history')
                response_text += f"Called log-transaction-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling log-transaction-history: {str(e)}\n"
        
        return response_text

@app.route('/export-transactions', methods=['GET'])
def export_transactions():
    with tracer.start_as_current_span(
        "accounting-history:export-transactions",
        attributes={"endpoint.name": "export-transactions"}
    ):
        return "Response from accounting-history at /export-transactions\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
