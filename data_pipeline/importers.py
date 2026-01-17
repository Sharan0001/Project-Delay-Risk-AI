"""
Data Importers for Project Delay Risk AI.

Provides import functionality for real project data:
- CSV import for task lists
- JSON import for full project structure
- Validation against Pydantic schemas

This allows users to import actual project data instead of
using simulated data.
"""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, field_validator, ValidationError

from data_pipeline.schema import TaskRecord


class ImportedTask(BaseModel):
    """Schema for imported task data."""
    task_id: str
    planned_duration: int = Field(ge=1)
    complexity: int = Field(ge=1, le=5)
    priority: str = Field(pattern="^(high|medium|low)$")
    required_skill: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    status: str = Field(default="not_started")
    
    @field_validator('priority')
    @classmethod
    def lowercase_priority(cls, v: str) -> str:
        return v.lower()


class ImportedProject(BaseModel):
    """Schema for imported project data."""
    name: str
    description: Optional[str] = None
    tasks: List[ImportedTask]


class ImportResult(BaseModel):
    """Result of an import operation."""
    success: bool
    project_id: Optional[int] = None
    tasks_imported: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


def parse_csv_tasks(
    csv_content: str,
    delimiter: str = ","
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parses CSV content into task dictionaries.
    
    Expected columns:
    - task_id (required)
    - planned_duration (required, integer)
    - complexity (required, 1-5)
    - priority (required, high/medium/low)
    - required_skill (optional)
    - dependencies (optional, comma-separated in cell)
    
    Args:
        csv_content: CSV file content as string
        delimiter: CSV delimiter (default comma)
        
    Returns:
        Tuple of (list of task dicts, list of error messages)
    """
    tasks = []
    errors = []
    
    try:
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
        
        # Check required columns
        required = {"task_id", "planned_duration", "complexity", "priority"}
        if reader.fieldnames:
            missing = required - set(reader.fieldnames)
            if missing:
                return [], [f"Missing required columns: {missing}"]
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Parse dependencies (may be comma-separated in cell)
                deps_raw = row.get("dependencies", "") or ""
                dependencies = [d.strip() for d in deps_raw.split(";") if d.strip()]
                
                task = {
                    "task_id": row["task_id"].strip(),
                    "planned_duration": int(row["planned_duration"]),
                    "complexity": int(row["complexity"]),
                    "priority": row["priority"].strip().lower(),
                    "required_skill": row.get("required_skill", "").strip() or None,
                    "dependencies": dependencies,
                    "status": row.get("status", "not_started").strip().lower()
                }
                
                # Validate with Pydantic
                validated = ImportedTask(**task)
                tasks.append(validated.model_dump())
                
            except ValueError as e:
                errors.append(f"Row {row_num}: Invalid value - {e}")
            except ValidationError as e:
                errors.append(f"Row {row_num}: Validation failed - {e}")
                
    except Exception as e:
        errors.append(f"CSV parsing failed: {e}")
    
    return tasks, errors


def parse_json_project(json_content: str) -> Tuple[Optional[ImportedProject], List[str]]:
    """
    Parses JSON content into a project structure.
    
    Expected format:
    {
        "name": "Project Name",
        "description": "Optional description",
        "tasks": [
            {
                "task_id": "T1",
                "planned_duration": 5,
                "complexity": 3,
                "priority": "high",
                "dependencies": ["T0"]
            }
        ]
    }
    
    Args:
        json_content: JSON file content as string
        
    Returns:
        Tuple of (ImportedProject or None, list of error messages)
    """
    errors = []
    
    try:
        data = json.loads(json_content)
        project = ImportedProject(**data)
        return project, []
        
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"Validation error at {loc}: {err['msg']}")
    except Exception as e:
        errors.append(f"Import failed: {e}")
    
    return None, errors


def import_csv_file(
    file_path: Path,
    delimiter: str = ","
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Imports tasks from a CSV file.
    
    Args:
        file_path: Path to CSV file
        delimiter: CSV delimiter
        
    Returns:
        Tuple of (task list, error list)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_csv_tasks(content, delimiter)
    except FileNotFoundError:
        return [], [f"File not found: {file_path}"]
    except Exception as e:
        return [], [f"Failed to read file: {e}"]


def import_json_file(file_path: Path) -> Tuple[Optional[ImportedProject], List[str]]:
    """
    Imports a project from a JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Tuple of (ImportedProject or None, error list)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_json_project(content)
    except FileNotFoundError:
        return None, [f"File not found: {file_path}"]
    except Exception as e:
        return None, [f"Failed to read file: {e}"]


def validate_task_dependencies(tasks: List[Dict[str, Any]]) -> List[str]:
    """
    Validates that all task dependencies reference existing tasks.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        List of warning messages for invalid dependencies
    """
    warnings = []
    task_ids = {t["task_id"] for t in tasks}
    
    for task in tasks:
        for dep in task.get("dependencies", []):
            if dep not in task_ids:
                warnings.append(
                    f"Task {task['task_id']} has unknown dependency: {dep}"
                )
    
    return warnings


def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> List[str]:
    """
    Detects circular dependencies in task list.
    
    Uses DFS to find cycles.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        List of error messages for circular dependencies
    """
    errors = []
    
    # Build adjacency list
    graph = {t["task_id"]: t.get("dependencies", []) for t in tasks}
    
    # Track visited and recursion stack
    visited = set()
    rec_stack = set()
    
    def dfs(node: str, path: List[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path + [neighbor]):
                    return True
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor) if neighbor in path else -1
                cycle = path[cycle_start:] + [neighbor] if cycle_start >= 0 else [node, neighbor]
                errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
                return True
        
        rec_stack.remove(node)
        return False
    
    for task_id in graph:
        if task_id not in visited:
            dfs(task_id, [task_id])
    
    return errors
