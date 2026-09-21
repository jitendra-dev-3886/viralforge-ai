"""Return readable API errors from the render endpoints, including CORS headers."""
import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def run_render(operation, **kwargs):
    try:
        from app.services.billing_service import billed_render
        return billed_render(operation, **kwargs)
    except HTTPException:
        raise
    except (ValueError, RuntimeError) as exc:
        logger.exception("Media rendering failed")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Media rendering failed")
        raise HTTPException(
            status_code=500,
            detail="Media rendering failed. Check the backend render log for details, then retry.",
        ) from exc
