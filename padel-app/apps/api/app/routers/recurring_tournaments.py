from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.recurring_tournament_crud import recurring_tournament_crud
from app.database import get_db
from app.models.tournament import TournamentStatus
from app.schemas.tournament_schemas import (
    RecurringTournamentCreate,
    RecurringTournamentGenerateRequest,
    RecurringTournamentGenerateResponse,
    RecurringTournamentInstancesResponse,
    RecurringTournamentListResponse,
    RecurringTournamentNextOccurrences,
    RecurringTournamentResponse,
    RecurringTournamentStats,
    RecurringTournamentUpdate,
    TournamentListResponse,
)
from app.services.recurring_tournament_service import recurring_tournament_service

router = APIRouter()


@router.post("/", response_model=RecurringTournamentResponse)
async def create_recurring_tournament(
    recurring_tournament: RecurringTournamentCreate,
    db: Session = Depends(get_db),
):
    """Create a new recurring tournament series."""
    try:
        # Extract category templates from the request
        category_templates_data = [
            template.model_dump()
            for template in recurring_tournament.category_templates
        ]

        # Create the recurring tournament data without category templates
        recurring_tournament_data = recurring_tournament.model_dump(
            exclude={"category_templates"}
        )

        # Create the recurring tournament
        db_recurring_tournament = recurring_tournament_crud.create_recurring_tournament(
            db=db, recurring_tournament_data=recurring_tournament_data
        )

        # Create category templates
        recurring_tournament_crud.bulk_update_category_templates(
            db=db,
            recurring_tournament_id=db_recurring_tournament.id,
            category_templates_data=category_templates_data,
        )

        # Refresh to get the category templates
        db.refresh(db_recurring_tournament)

        # Generate initial tournament instances if auto-generation is enabled
        if db_recurring_tournament.auto_generation_enabled:
            recurring_tournament_service.generate_tournament_instances(
                db=db, recurring_tournament_id=db_recurring_tournament.id
            )

        # Get counts for response
        total_instances = recurring_tournament_crud.count_tournament_instances(
            db=db, recurring_tournament_id=db_recurring_tournament.id
        )
        upcoming_instances = recurring_tournament_crud.count_tournament_instances(
            db=db,
            recurring_tournament_id=db_recurring_tournament.id,
            status_filter=[TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN],
        )

        # Build response
        response = RecurringTournamentResponse.model_validate(db_recurring_tournament)
        response.total_instances = total_instances
        response.upcoming_instances = upcoming_instances

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[RecurringTournamentListResponse])
async def get_recurring_tournaments(
    club_id: Optional[int] = Query(None, description="Filter by club ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    """Get list of recurring tournaments with optional filtering."""
    recurring_tournaments = recurring_tournament_crud.get_recurring_tournaments(
        db=db, club_id=club_id, is_active=is_active, skip=skip, limit=limit
    )

    # Build response with counts
    response = []
    for rt in recurring_tournaments:
        total_instances = recurring_tournament_crud.count_tournament_instances(
            db=db, recurring_tournament_id=rt.id
        )
        upcoming_instances = recurring_tournament_crud.count_tournament_instances(
            db=db,
            recurring_tournament_id=rt.id,
            status_filter=[TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN],
        )

        rt_response = RecurringTournamentListResponse.model_validate(rt)
        rt_response.total_instances = total_instances
        rt_response.upcoming_instances = upcoming_instances
        rt_response.club_name = rt.club.name if rt.club else None

        response.append(rt_response)

    return response


@router.get("/{recurring_tournament_id}", response_model=RecurringTournamentResponse)
async def get_recurring_tournament(
    recurring_tournament_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific recurring tournament by ID."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    # Get counts for response
    total_instances = recurring_tournament_crud.count_tournament_instances(
        db=db, recurring_tournament_id=recurring_tournament_id
    )
    upcoming_instances = recurring_tournament_crud.count_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=[TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN],
    )

    # Build response
    response = RecurringTournamentResponse.model_validate(db_recurring_tournament)
    response.total_instances = total_instances
    response.upcoming_instances = upcoming_instances

    return response


@router.put("/{recurring_tournament_id}", response_model=RecurringTournamentResponse)
async def update_recurring_tournament(
    recurring_tournament_id: int,
    recurring_tournament_update: RecurringTournamentUpdate,
    db: Session = Depends(get_db),
):
    """Update a recurring tournament. Only affects future tournament instances."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    try:
        # Extract category templates if provided
        category_templates_data = None
        if recurring_tournament_update.category_templates:
            category_templates_data = [
                template.model_dump()
                for template in recurring_tournament_update.category_templates
            ]

        # Update the recurring tournament
        update_data = recurring_tournament_update.model_dump(
            exclude_unset=True, exclude={"category_templates"}
        )

        db_recurring_tournament = recurring_tournament_crud.update_recurring_tournament(
            db=db,
            recurring_tournament_id=recurring_tournament_id,
            update_data=update_data,
        )

        # Update category templates if provided
        if category_templates_data:
            recurring_tournament_crud.bulk_update_category_templates(
                db=db,
                recurring_tournament_id=recurring_tournament_id,
                category_templates_data=category_templates_data,
            )
            db.refresh(db_recurring_tournament)

        # Get counts for response
        total_instances = recurring_tournament_crud.count_tournament_instances(
            db=db, recurring_tournament_id=recurring_tournament_id
        )
        upcoming_instances = recurring_tournament_crud.count_tournament_instances(
            db=db,
            recurring_tournament_id=recurring_tournament_id,
            status_filter=[TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN],
        )

        # Build response
        response = RecurringTournamentResponse.model_validate(db_recurring_tournament)
        response.total_instances = total_instances
        response.upcoming_instances = upcoming_instances

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{recurring_tournament_id}")
async def delete_recurring_tournament(
    recurring_tournament_id: int,
    cancel_future_only: bool = Query(
        True,
        description="If true, only cancel future instances. If false, cancel all instances.",
    ),
    db: Session = Depends(get_db),
):
    """Delete/cancel a recurring tournament series."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    success = recurring_tournament_service.cancel_recurring_tournament(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        cancel_future_only=cancel_future_only,
    )

    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to cancel recurring tournament"
        )

    return {"message": "Recurring tournament cancelled successfully"}


@router.get(
    "/{recurring_tournament_id}/instances",
    response_model=RecurringTournamentInstancesResponse,
)
async def get_tournament_instances(
    recurring_tournament_id: int,
    start_date: Optional[datetime] = Query(
        None, description="Filter instances from this date"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter instances to this date"
    ),
    include_cancelled: bool = Query(False, description="Include cancelled tournaments"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    """Get tournament instances for a recurring tournament."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    # Get tournament instances
    status_filter = (
        None
        if include_cancelled
        else [
            status
            for status in TournamentStatus
            if status != TournamentStatus.CANCELLED
        ]
    )

    instances = recurring_tournament_crud.get_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        start_date=start_date,
        end_date=end_date,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )

    # Get total count
    total_count = recurring_tournament_crud.count_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=status_filter,
    )

    # Get next occurrences
    next_occurrences = recurring_tournament_service.get_next_occurrences(
        db=db, recurring_tournament_id=recurring_tournament_id, count=5
    )

    # Build response
    instances_response = [
        TournamentListResponse.model_validate(instance) for instance in instances
    ]

    return RecurringTournamentInstancesResponse(
        recurring_tournament_id=recurring_tournament_id,
        series_name=db_recurring_tournament.series_name,
        instances=instances_response,
        total_count=total_count,
        next_occurrences=next_occurrences,
    )


@router.post(
    "/{recurring_tournament_id}/generate",
    response_model=RecurringTournamentGenerateResponse,
)
async def generate_tournament_instances(
    recurring_tournament_id: int,
    generate_request: RecurringTournamentGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate tournament instances for a recurring tournament."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    if not db_recurring_tournament.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot generate instances for inactive recurring tournament",
        )

    try:
        # Generate tournament instances
        generated_tournaments = (
            recurring_tournament_service.generate_tournament_instances(
                db=db,
                recurring_tournament_id=recurring_tournament_id,
                start_date=generate_request.start_date,
                end_date=generate_request.end_date,
                limit=generate_request.limit,
            )
        )

        # Get next occurrences
        next_occurrences = recurring_tournament_service.get_next_occurrences(
            db=db, recurring_tournament_id=recurring_tournament_id, count=5
        )

        # Build response
        generated_tournaments_response = [
            TournamentListResponse.model_validate(tournament)
            for tournament in generated_tournaments
        ]

        return RecurringTournamentGenerateResponse(
            recurring_tournament_id=recurring_tournament_id,
            generated_tournaments=generated_tournaments_response,
            total_generated=len(generated_tournaments),
            next_occurrence_dates=next_occurrences,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{recurring_tournament_id}/next-occurrences",
    response_model=RecurringTournamentNextOccurrences,
)
async def get_next_occurrences(
    recurring_tournament_id: int,
    count: int = Query(
        5, ge=1, le=20, description="Number of next occurrences to return"
    ),
    db: Session = Depends(get_db),
):
    """Get the next occurrence dates for a recurring tournament."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    next_occurrences = recurring_tournament_service.get_next_occurrences(
        db=db, recurring_tournament_id=recurring_tournament_id, count=count
    )

    return RecurringTournamentNextOccurrences(
        recurring_tournament_id=recurring_tournament_id,
        series_name=db_recurring_tournament.series_name,
        next_occurrences=next_occurrences,
    )


@router.get("/{recurring_tournament_id}/stats", response_model=RecurringTournamentStats)
async def get_recurring_tournament_stats(
    recurring_tournament_id: int,
    db: Session = Depends(get_db),
):
    """Get statistics for a recurring tournament series."""
    db_recurring_tournament = recurring_tournament_crud.get_recurring_tournament(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    if not db_recurring_tournament:
        raise HTTPException(status_code=404, detail="Recurring tournament not found")

    # Get counts by status
    total_instances = recurring_tournament_crud.count_tournament_instances(
        db=db, recurring_tournament_id=recurring_tournament_id
    )

    completed_instances = recurring_tournament_crud.count_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=[TournamentStatus.COMPLETED],
    )

    cancelled_instances = recurring_tournament_crud.count_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=[TournamentStatus.CANCELLED],
    )

    upcoming_instances = recurring_tournament_crud.count_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=[TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN],
    )

    # Calculate completion rate
    completion_rate = (
        (completed_instances / total_instances * 100) if total_instances > 0 else 0.0
    )

    # Get all instances to calculate participant stats
    all_instances = recurring_tournament_crud.get_tournament_instances(
        db=db,
        recurring_tournament_id=recurring_tournament_id,
        status_filter=[TournamentStatus.COMPLETED, TournamentStatus.IN_PROGRESS],
    )

    # Calculate participant stats (simplified - would need to join with teams)
    total_participants = sum(len(instance.teams) for instance in all_instances)
    average_participants = (
        (total_participants / len(all_instances)) if all_instances else 0.0
    )

    return RecurringTournamentStats(
        recurring_tournament_id=recurring_tournament_id,
        series_name=db_recurring_tournament.series_name,
        total_instances=total_instances,
        completed_instances=completed_instances,
        cancelled_instances=cancelled_instances,
        upcoming_instances=upcoming_instances,
        total_participants=total_participants,
        average_participants_per_instance=average_participants,
        completion_rate=completion_rate,
    )
