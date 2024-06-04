import traceback
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class TracingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with tracer.start_as_current_span(request.path) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", request.get_full_path())

            try:
                response = self.get_response(request)
                span.set_attribute("http.status_code", response.status_code)
            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("exception.type", type(e).__name__)
                span.set_attribute("exception.message", str(e))
                span.set_attribute("exception.stacktrace", traceback.format_exc())
                raise
        return response
