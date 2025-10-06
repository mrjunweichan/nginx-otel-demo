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
SERVICE_NAME = "payments-orchestrator"
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

@app.route('/initiate-transfer', methods=['GET', 'POST'])
def initiate_transfer():
    with tracer.start_as_current_span(
        "payments-orchestrator:initiate-transfer",
        attributes={"endpoint.name": "initiate-transfer"}
    ):
        response_text = "Response from payments-orchestrator at /initiate-transfer\n"
        
        # Inter-team call: Account Management's /get-balance (via NGINX)
        with tracer.start_as_current_span("call-account-get-balance"):
            try:
                # resp = requests.get('http://nginx-gateway:8080/api/accounting/ledger/get-balance')
                resp = requests.get('http://app-accounting-ledger:5000/get-balance') # To view graph
                response_text += f"Called get-balance: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling get-balance: {str(e)}\n"
        
        # Inter-team call: Risk's /validate-transaction (via NGINX)
        with tracer.start_as_current_span("call-risk-validate-transaction"):
            try:
                # resp = requests.get('http://nginx-gateway:8080/api/risk/orchestrator/validate-transaction')
                resp = requests.get('http://app-risk-orchestrator:5000/validate-transaction') # To view graph
                response_text += f"Called validate-transaction: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling validate-transaction: {str(e)}\n"
        
        # Intra-team call: payments-processor's /process-gateway (direct)
        with tracer.start_as_current_span("call-process-gateway"):
            try:
                resp = requests.get('http://app-payment-processor:5000/process-gateway')
                response_text += f"Called process-gateway: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling process-gateway: {str(e)}\n"
        
        return response_text

@app.route('/get-payment-status', methods=['GET'])
def get_payment_status():
    with tracer.start_as_current_span(
        "payments-orchestrator:get-payment-status",
        attributes={"endpoint.name": "get-payment-status"}
    ):
        response_text = "Response from payments-orchestrator at /get-payment-status\n"
        
        # Intra-team call: payments-history's /record-payment-history (direct)
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get('http://app-payment-history:5000/record-payment-history')
                response_text += f"Called record-payment-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling record-payment-history: {str(e)}\n"
        
        return response_text

@app.route('/cancel-transfer', methods=['POST'])
def cancel_transfer():
    with tracer.start_as_current_span(
        "payments-orchestrator:cancel-transfer",
        attributes={"endpoint.name": "cancel-transfer"}
    ):
        response_text = "Response from payments-orchestrator at /cancel-transfer\n"
        
        # Intra-team call: payments-processor's /process-gateway (direct)
        with tracer.start_as_current_span("call-process-gateway"):
            try:
                resp = requests.get('http://app-payment-processor:5000/process-gateway')
                response_text += f"Called process-gateway: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling process-gateway: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
