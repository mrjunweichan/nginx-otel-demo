from flask import Flask
import requests
from opentelemetry import trace

app = Flask(__name__)

@app.route('/')
def hello():
    with trace.get_tracer(__name__).start_as_current_span("call-service-b"):
        response = requests.get('http://service-b:5001/')  # Call Service B
    return f"Hello from Service A! Response from B: {response.text}"

if __name__ == '__main__':
    app.run()
