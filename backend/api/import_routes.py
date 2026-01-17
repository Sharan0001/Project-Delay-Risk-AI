"""
Import API Routes for Project Delay Risk AI.

Provides endpoints for importing real project data:
- POST /projects/import/json - Import JSON project
- POST /projects/import/csv - Import CSV tasks
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File
from pydantic import BaseModel, Field

from backend.core.database import create_project, add_tasks, get_project
from data_pipeline.importers import (
    parse_json_project, parse_csv_tasks,
    validate_task_dependencies, detect_circular_dependencies,
    ImportedProject, ImportResult
)


router = APIRouter(prefix="/projects", tags=["Import"])


class ImportJSONRequest(BaseModel):
    """Request body for JSON import."""
    name: str
    description: Optional[str] = None
    tasks: List[dict]


class CSVImportRequest(BaseModel):
    """Request body for CSV import."""
    project_name: str
    csv_content: str
    delimiter: str = ","


@router.post("/import/json", response_model=ImportResult)
async def import_json_project(request: ImportJSONRequest):
    """
    Import a project from JSON data.
    
    Request body should contain project name and tasks array.
    """
    errors = []
    warnings = []
    
    # Parse and validate
    json_content = request.model_dump_json()
    project, parse_errors = parse_json_project(json_content)
    
    if parse_errors:
        return ImportResult(
            success=False,
            errors=parse_errors
        )
    
    tasks = [t.model_dump() for t in project.tasks]
    
    # Validate dependencies
    warnings.extend(validate_task_dependencies(tasks))
    
    # Check for circular dependencies
    circular_errors = detect_circular_dependencies(tasks)
    if circular_errors:
        return ImportResult(
            success=False,
            errors=circular_errors
        )
    
    # Create project and add tasks
    try:
        project_id = create_project(
            name=request.name,
            description=request.description
        )
        add_tasks(project_id, tasks)
        
        return ImportResult(
            success=True,
            project_id=project_id,
            tasks_imported=len(tasks),
            warnings=warnings
        )
        
    except Exception as e:
        return ImportResult(
            success=False,
            errors=[f"Database error: {e}"]
        )


@router.post("/import/csv", response_model=ImportResult)
async def import_csv_tasks(request: CSVImportRequest):
    """
    Import tasks from CSV content.
    
    CSV must have columns: task_id, planned_duration, complexity, priority
    Optional columns: required_skill, dependencies (semicolon-separated), status
    """
    errors = []
    warnings = []
    
    # Parse CSV
    tasks, parse_errors = parse_csv_tasks(
        request.csv_content,
        delimiter=request.delimiter
    )
    
    if parse_errors:
        return ImportResult(
            success=False,
            errors=parse_errors
        )
    
    if not tasks:
        return ImportResult(
            success=False,
            errors=["No valid tasks found in CSV"]
        )
    
    # Validate dependencies
    warnings.extend(validate_task_dependencies(tasks))
    
    # Check for circular dependencies
    circular_errors = detect_circular_dependencies(tasks)
    if circular_errors:
        return ImportResult(
            success=False,
            errors=circular_errors
        )
    
    # Create project and add tasks
    try:
        project_id = create_project(name=request.project_name)
        add_tasks(project_id, tasks)
        
        return ImportResult(
            success=True,
            project_id=project_id,
            tasks_imported=len(tasks),
            warnings=warnings
        )
        
    except Exception as e:
        return ImportResult(
            success=False,
            errors=[f"Database error: {e}"]
        )


@router.get("/{project_id}")
async def get_project_details(project_id: int):
    """Get project details by ID."""
    from backend.core.database import get_project_tasks
    
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = get_project_tasks(project_id)
    project["tasks"] = tasks
    
    return project


@router.get("/")
async def list_all_projects():
    """List all projects."""
    from backend.core.database import list_projects
    return {"projects": list_projects()}
