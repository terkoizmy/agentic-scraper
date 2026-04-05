import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from db import postgres
from models.schemas import SourceCreate, SourceResponse, SourceUpdate
from scheduler.cron import sync_jobs

router = APIRouter()


@router.get("/", response_model=list[SourceResponse])
async def list_sources():
    """Return all registered scraping sources."""
    return await postgres.list_sources()


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(body: SourceCreate):
    """Register a new scraping source."""
    result = await postgres.create_source(
        url=body.url,
        name=body.name,
        source_type=body.source_type,
        schedule_hours=body.schedule_hours,
    )
    await sync_jobs()
    return result


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(source_id: uuid.UUID, body: SourceUpdate):
    """Update a source configuration. Only provided fields are changed."""
    updates = body.model_dump(exclude_none=True)
    updated = await postgres.update_source(source_id, updates)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    await sync_jobs()
    return updated


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: uuid.UUID):
    """Delete a source and all its associated documents and jobs."""
    deleted = await postgres.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    await sync_jobs()
