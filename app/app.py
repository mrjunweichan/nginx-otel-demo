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

@app.route('/initiate-transfer', methods=['GET', 'POST'])
def initiate_transfer():
    with tracer.start_as_current_span("payment:initiate-transfer"):
        response_text = "Response from payment at /initiate-transfer\n"
        
        # Internal call: /process-gateway (direct, intra-team)
        with tracer.start_as_current_span("call-process-gateway"):
            try:
                resp = requests.get('http://payment:5002/process-gateway')
                response_text += f"Called process-gateway: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling process-gateway: {str(e)}\n"
        
        # Inter-team call: Accounting's /get-balance (via NGINX)
        with tracer.start_as_current_span("call-account-balance"):
            try:
                # resp = requests.get('http://nginx-gateway:8080/api/accounts/get-balance')
                resp = requests.get('http://nginx-gateway:8080/api/a/')
                response_text += f"Called account-balance: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling account-balance: {str(e)}\n"
        
        # Inter-team call: Risk's /validate-transaction (via NGINX)
        # with tracer.start_as_current_span("call-validate-transaction"):
            # try:
                # resp = requests.get('http://nginx-gateway:8080/api/risk/validate-transaction')
                # response_text += f"Called validate-transaction: {resp.text}\n"
            # except requests.RequestException as e:
                # response_text += f"Error calling validate-transaction: {str(e)}\n"
        
        return response_text

@app.route('/process-gateway', methods=['GET'])
def process_gateway():
    with tracer.start_as_current_span("payment:process-gateway"):
        response_text = "Response from payment at /process-gateway\n"
        
        # Internal call: /record-payment-history (direct, intra-team)
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get('http://payment:5002/record-payment-history')
                response_text += f"Called record-payment-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling record-payment-history: {str(e)}\n"
        
        return response_text

@app.route('/record-payment-history', methods=['GET'])
def record_payment_history():
    with tracer.start_as_current_span("payment:record-payment-history"):
        return "Response from payment at /record-payment-history\n"

@app.route('/get-payment-status', methods=['GET'])
def get_payment_status():
    with tracer.start_as_current_span("payment:get-payment-status"):
        return "Response from payment at /get-payment-status\n"

@app.route('/settle-payment', methods=['POST'])
def settle_payment():
    with tracer.start_as_current_span("payment:settle-payment"):
        response_text = "Response from payment at /settle-payment\n"
        
        # Internal call: /process-gateway (direct, intra-team)
        with tracer.start_as_current_span("call-process-gateway"):
            try:
                resp = requests.get('http://payment:5002/process-gateway')
                response_text += f"Called process-gateway: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling process-gateway: {str(e)}\n"
        
        return response_text

# For debugging
@app.route('/test')
def test():
    return f"Test route for {SERVICE_NAME}\n"

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
