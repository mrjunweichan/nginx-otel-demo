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
SERVICE_NAME = "accounting-ledger"

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

@app.route('/init-ledger', methods=['GET', 'POST'])
def init_ledger():
    with tracer.start_as_current_span(
        "accounting-ledger:init-ledger",
        attributes={"endpoint.name": "init-ledger"}
    ):
        response_text = "Response from accounting-ledger at /init-ledger\n"
        
        # Intra-team call: /log-transaction-history (direct)
        with tracer.start_as_current_span("call-log-transaction-history"):
            try:
                resp = requests.get('http://app-accounting-ledger:5000/log-transaction-history')
                response_text += f"Called log-transaction-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling log-transaction-history: {str(e)}\n"
        
        return response_text

@app.route('/get-balance', methods=['GET'])
def get_balance():
    with tracer.start_as_current_span(
        "accounting-ledger:get-balance",
        attributes={"endpoint.name": "get-balance"}
    ):
        return "Response from accounting-ledger at /get-balance\n"

@app.route('/log-transaction-history', methods=['GET', 'POST'])
def log_transaction_history():
    with tracer.start_as_current_span(
        "accounting-ledger:log-transaction-history",
        attributes={"endpoint.name": "log-transaction-history"}
    ):
        return "Response from accounting-ledger at /log-transaction-history\n"

@app.route('/reconcile-ledger', methods=['POST'])
def reconcile_ledger():
    with tracer.start_as_current_span(
        "accounting-ledger:reconcile-ledger",
        attributes={"endpoint.name": "reconcile-ledger"}
    ):
        response_text = "Response from accounting-ledger at /reconcile-ledger\n"
        
        # Intra-team call: /log-transaction-history (direct)
        with tracer.start_as_current_span("call-log-transaction-history"):
            try:
                resp = requests.get('http://app-accounting-ledger:5000/log-transaction-history')
                response_text += f"Called log-transaction-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling log-transaction-history: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
