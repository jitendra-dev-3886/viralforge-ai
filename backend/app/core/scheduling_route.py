import logging
from fastapi import HTTPException
from fastapi.routing import APIRoute
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class SchedulingRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def guarded(request):
            try:
                return await handler(request)
            except SQLAlchemyError as exc:
                # Convert to a handled error so CORS can expose it to the browser.
                # SQLAlchemy messages may include private query parameters.
                logger.error("Scheduling database operation failed (%s)", type(exc).__name__)
                raise HTTPException(503, "The scheduling database could not complete this request. Restart the backend to apply pending schema updates, then retry. An automatic scheduling retry with the same request will not create a duplicate post.") from None

        return guarded
