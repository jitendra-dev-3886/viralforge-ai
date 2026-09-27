import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.scheduling_route import SchedulingRoute
from app.database import get_db
from app.models.automation import AutomationRule, AutomationRun
from app.models.schedule import Schedule
from app.models.content import Content
from app.schemas.automation import AutomationConfig, AutomationState
from app.services.automation_service import next_occurrence, validate_resources, utc
from app.services.publishing_accounts import now

router = APIRouter(prefix="/api/automations", tags=["Auto Mode"], route_class=SchedulingRoute)


def data(rule):
    return {**rule.config, "id": rule.id, "enabled": rule.enabled, "next_run_at": utc(rule.next_run_at)}


def owned_rule(db, user_id, rule_id):
    rule = db.query(AutomationRule).filter_by(id=rule_id, user_id=user_id).with_for_update().first()
    if not rule:
        raise HTTPException(404, "Automation not found.")
    return rule


@router.get("/")
def list_automations(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rules = db.query(AutomationRule).filter_by(user_id=user_id).order_by(AutomationRule.id.desc()).all()
    runs = db.query(AutomationRun, Schedule.status, Content.generation_config).outerjoin(Schedule, AutomationRun.schedule_id == Schedule.id).outerjoin(Content, AutomationRun.content_id == Content.id).filter(
        AutomationRun.user_id == user_id).order_by(AutomationRun.id.desc()).limit(100).all()
    return {"rules": [data(rule) for rule in rules], "runs": [
        {"id": run.id, "rule_id": run.rule_id, "scheduled_at": utc(run.scheduled_at), "status": status or run.status,
         "content_id": run.content_id, "schedule_id": run.schedule_id, "error_message": run.error_message,
         "topic": (config or {}).get("topic", "")}
        for run, status, config in runs
    ], "worker_enabled": os.getenv("AUTO_GENERATION_ENABLED", "true").lower() == "true"}


@router.post("/")
def create_automation(request: AutomationConfig, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    validate_resources(db, user_id, request)
    rule = AutomationRule(user_id=user_id, project_id=request.project_id, config=request.model_dump(), enabled=request.enabled,
                          next_run_at=next_occurrence(request, now() + timedelta(minutes=request.lead_minutes)))
    db.add(rule)
    db.commit()
    return {"rule": data(rule)}


@router.put("/{rule_id}")
def update_automation(rule_id: int, request: AutomationConfig, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rule = owned_rule(db, user_id, rule_id)
    if db.query(AutomationRun.id).filter_by(rule_id=rule.id, status="generating").first():
        raise HTTPException(409, "This schedule is generating content. Pause it now, or edit after generation finishes.")
    validate_resources(db, user_id, request)
    rule.project_id, rule.config, rule.enabled = request.project_id, request.model_dump(), request.enabled
    rule.next_run_at = next_occurrence(request, now() + timedelta(minutes=request.lead_minutes))
    db.commit()
    return {"rule": data(rule)}


@router.patch("/{rule_id}")
def set_automation_state(rule_id: int, request: AutomationState, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rule = owned_rule(db, user_id, rule_id)
    config = AutomationConfig(**rule.config)
    if request.enabled and not rule.enabled:
        validate_resources(db, user_id, config)
        rule.next_run_at = next_occurrence(config, now() + timedelta(minutes=config.lead_minutes))
    rule.enabled = request.enabled
    db.commit()
    return {"rule": data(rule)}
