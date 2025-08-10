from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.scheduler import scheduler as scheduler_module
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")  # type: ignore[misc]
def list_jobs() -> list[dict[str, str]]:
    sched = scheduler_module.get_scheduler()
    return [{"id": job.id} for job in sched.get_jobs()]


@router.post("/{name}")  # type: ignore[misc]
def create_job(name: str) -> dict[str, str]:
    try:
        func = job_service.get(name)
    except KeyError as exc:  # pragma: no cover - job not found
        raise HTTPException(status_code=404, detail="job not found") from exc
    sched = scheduler_module.get_scheduler()
    sched.add_job(func, "interval", minutes=1, id=name, replace_existing=True)
    return {"status": "scheduled"}


@router.delete("/{job_id}")  # type: ignore[misc]
def delete_job(job_id: str) -> dict[str, str]:
    sched = scheduler_module.get_scheduler()
    sched.remove_job(job_id)
    return {"status": "deleted"}


@router.post("/{name}/run")  # type: ignore[misc]
async def run_job(name: str) -> dict[str, str]:
    try:
        func = job_service.get(name)
    except KeyError as exc:  # pragma: no cover - job not found
        raise HTTPException(status_code=404, detail="job not found") from exc
    await func()
    return {"status": "completed"}
