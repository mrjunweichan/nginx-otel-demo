import os
import json
import random
import time
from flask import Flask, request
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
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
CHAOS_MODE = os.getenv("CHAOS_MODE", "off") # <-- Set to 'on' to activate chaos

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

def chaos_injector():
    if CHAOS_MODE != "on":
        return

    r = random.random()
    if r < 0.15:       # 15% chance of total failure
        raise Exception("Simulated processor crash!")
    elif r < 0.45:     # 30% chance of high latency
        delay = random.uniform(3.0, 9.0)
        time.sleep(delay)
    elif r < 0.55:     # 10% chance of huge payload
        return "A" * 45_000_000  # ~45 MB response

"""
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
"""

@app.route('/process-gateway', methods=['GET'])
def process_gateway():
    with tracer.start_as_current_span(
        "payments-processor:process-gateway",
        attributes={
            "endpoint.name": "process-gateway",
            "chaos.mode": CHAOS_MODE
        }
    ):
        chaos_injector()

        response_text = "Response from payments-processor at /process-gateway\n"

        # Intra-team call: payments-history's /record-payment-history (direct)
        # Simulate downstream call with possible failure
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get('http://app-payment-history:5000/record-payment-history', timeout=5)
                response_text += f"Called record-payment-history: {resp.text[:200]}\n"
            except requests.RequestException as e:
                trace.get_current_span().record_exception(e)
                response_text += f"Error calling record-payment-history: {str(e)}\n"

        # Intra-team call: payments-currency's /convert-currency (direct)
        with tracer.start_as_current_span("call-convert-currency"):
            try:
                resp = requests.get('http://app-payment-currency:5000/convert-currency', timeout=5)
                response_text += f"Called convert-currency: {resp.text[:200]}\n"
            except requests.RequestException as e:
                trace.get_current_span().record_exception(e)
                response_text += f"Error calling convert-currency: {str(e)}\n"

        huge = chaos_injector()
        if huge:
            return huge, 200
        return response_text

"""
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
"""

@app.route('/settle-payment', methods=['POST'])
def settle_payment():
    with tracer.start_as_current_span(
        "payments-processor:settle-payment",
        attributes={
            "endpoint.name": "settle-payment",
            "chaos.mode": CHAOS_MODE
        }
    ):
        chaos_injector()

        # Intra-team call: /process-gateway (direct, intra-team)
        # Retry loop for retry-storm
        for attempt in range(3):
            with tracer.start_as_current_span(f"call-process-gateway-attempt-{attempt+1}"):
                try:
                    resp = requests.get('http://app-payment-processor:5000/process-gateway', timeout=2)
                    return f"Success on attempt {attempt+1}: {resp.text[:200]}"
                except:
                    if attempt == 2:
                        raise
                    time.sleep(0.5)
        return "Should never reach here"

"""
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
"""

@app.route('/refund-payment', methods=['POST'])
def refund_payment():
    with tracer.start_as_current_span(
        "payments-processor:refund-payment",
        attributes={
            "endpoint.name": "refund-payment",
            "http.method": "POST",
            "http.content_type": request.content_type or "unknown",
            "http.payload.size": request.content_length or 0,
            "chaos.mode": CHAOS_MODE
        }
    ):

        huge_payload = chaos_injector() # sleep 3–9s, crash, or return 45 MB
        response_text = "Response from payments-processor at /refund-payment\n"

        # Intra-team call: payments-history's /record-payment-history (direct)
        with tracer.start_as_current_span("call-record-payment-history"):
            try:
                resp = requests.get(
                    'http://app-payment-history:5000/record-payment-history',
                    timeout=5
                )
                resp.raise_for_status()
                response_text += f"Called record-payment-history: {resp.text.strip()}\n"
            except requests.RequestException as e:
                current_span = trace.get_current_span()
                current_span.set_status(trace.StatusCode.ERROR)
                current_span.record_exception(e)
                response_text += f"Error calling record-payment-history: {str(e)}\n"

        if huge_payload:
            return huge_payload, 200

        return response_text, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
