"""Distributed tracing middleware - TraceID propagation."""

from __future__ import annotations

import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

TRACE_HEADER = "X-Trace-ID"


class TracingMiddleware(BaseHTTPMiddleware):
    """Injects or propagates TraceID for every request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get(TRACE_HEADER) or str(uuid.uuid4())
        request.state.trace_id = trace_id

        response = await call_next(request)
        response.headers[TRACE_HEADER] = trace_id
        return response
