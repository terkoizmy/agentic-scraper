import uuid

from fastapi import APIRouter, HTTPException, status

from db import postgres
from models.schemas import JobResponse

router = APIRouter()


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs():
    """Return full scrape job history ordered by most recent first."""
    return await postgres.list_jobs()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID):
    """Return status and statistics for a specific scrape job."""
    job = await postgres.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
