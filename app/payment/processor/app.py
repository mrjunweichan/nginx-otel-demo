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
SERVICE_NAME = "payments-processor"

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "payments"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/process-gateway', methods=['GET'])
def process_gateway():
    with tracer.start_as_current_span(
        "payments-processor:process-gateway",
        attributes={"endpoint.name": "process-gateway"}
    ):
        response_text = "Response from payments-processor at /process-gateway\n"
        
        # Intra-team call: payments-history's /record-payment-history (direct)
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get('http://app-payment-history:5000/record-payment-history')
                response_text += f"Called record-payment-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling record-payment-history: {str(e)}\n"
        
        # Intra-team call: payments-currency's /convert-currency (direct)
        with tracer.start_as_current_span("call-convert-currency"):
            try:
                resp = requests.get('http://app-payment-currency:5000/convert-currency')
                response_text += f"Called convert-currency: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling convert-currency: {str(e)}\n"
        
        return response_text

@app.route('/settle-payment', methods=['POST'])
def settle_payment():
    with tracer.start_as_current_span(
        "payments-processor:settle-payment",
        attributes={"endpoint.name": "settle-payment"}
    ):
        response_text = "Response from payments-processor at /settle-payment\n"
        
        # Intra-team call: /process-gateway (direct, intra-team)
        with tracer.start_as_current_span("call-process-gateway"):
            try:
                resp = requests.get('http://app-payment-processor:5000/process-gateway')
                response_text += f"Called process-gateway: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling process-gateway: {str(e)}\n"
        
        return response_text

@app.route('/refund-payment', methods=['POST'])
def refund_payment():
    with tracer.start_as_current_span(
        "payments-processor:refund-payment",
        attributes={"endpoint.name": "refund-payment"}
    ):
        response_text = "Response from payments-processor at /refund-payment\n"
        
        # Intra-team call: payments-history's /record-payment-history (direct)
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get('http://app-payment-history:5000/record-payment-history')
                response_text += f"Called record-payment-history: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling record-payment-history: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
