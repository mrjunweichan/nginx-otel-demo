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
SERVICE_NAME = "risk-analyzer"
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

# Set up OpenTelemetry
resource = Resource(attributes={"service.name": SERVICE_NAME, "team": "risk"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/check-fraud', methods=['GET', 'POST'])
def check_fraud():
    with tracer.start_as_current_span(
        "risk-analyzer:check-fraud",
        attributes={"endpoint.name": "check-fraud"}
    ):
        response_text = "Response from risk-analyzer at /check-fraud\n"
        
        # Intra-team call: /screen-aml (direct)
        with tracer.start_as_current_span("call-screen-aml"):
            try:
                resp = requests.get('http://app-risk-analyzer:5000/screen-aml')
                response_text += f"Called screen-aml: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling screen-aml: {str(e)}\n"
        
        return response_text

@app.route('/screen-aml', methods=['GET', 'POST'])
def screen_aml():
    with tracer.start_as_current_span(
        "risk-analyzer:screen-aml",
        attributes={"endpoint.name": "screen-aml"}
    ):
        return "Response from risk-analyzer at /screen-aml\n"

@app.route('/score-risk', methods=['GET', 'POST'])
def score_risk():
    with tracer.start_as_current_span(
        "risk-analyzer:score-risk",
        attributes={"endpoint.name": "score-risk"}
    ):
        response_text = "Response from risk-analyzer at /score-risk\n"
        
        # Intra-team call: /check-fraud (direct)
        with tracer.start_as_current_span("call-check-fraud"):
            try:
                resp = requests.get('http://app-risk-analyzer:5000/check-fraud')
                response_text += f"Called check-fraud: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling check-fraud: {str(e)}\n"
        
        # Intra-team call: /screen-aml (direct)
        with tracer.start_as_current_span("call-screen-aml"):
            try:
                resp = requests.get('http://app-risk-analyzer:5000/screen-aml')
                response_text += f"Called screen-aml: {resp.text}\n"
            except requests.RequestException as e:
                response_text += f"Error calling screen-aml: {str(e)}\n"
        
        return response_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
