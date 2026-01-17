"""
Database Module for Project Delay Risk AI.

Provides SQLite persistence for:
- Projects and their metadata
- Task definitions and states
- Analysis results history

Uses synchronous sqlite3 for simplicity.
For async operations, consider migrating to aiosqlite.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


# Default database path (relative to project root)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "project_risk.db"


@contextmanager
def get_connection(db_path: Optional[Path] = None):
    """
    Context manager for database connections.
    
    Args:
        db_path: Optional path to database file
        
    Yields:
        sqlite3.Connection with row factory set
    """
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initializes the database schema.
    
    Creates tables if they don't exist:
    - projects: Project metadata
    - tasks: Task definitions
    - analyses: Analysis run history
    - risk_results: Individual task risk results
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                task_id TEXT NOT NULL,
                planned_duration INTEGER NOT NULL,
                complexity INTEGER NOT NULL,
                priority TEXT NOT NULL,
                required_skill TEXT,
                dependencies TEXT,  -- JSON array
                status TEXT DEFAULT 'not_started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, task_id)
            )
        """)
        
        # Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                what_if_scenario TEXT,
                model_type TEXT,
                num_tasks INTEGER,
                high_risk_count INTEGER,
                medium_risk_count INTEGER,
                low_risk_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)
        
        # Risk results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                task_id TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                delay_probability REAL NOT NULL,
                reasons TEXT,  -- JSON array
                recommended_actions TEXT,  -- JSON array
                what_if_impact TEXT,  -- JSON object
                FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()


# =============================================================================
# Project Operations
# =============================================================================

def create_project(
    name: str,
    description: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """
    Creates a new project.
    
    Args:
        name: Project name
        description: Optional description
        db_path: Optional database path
        
    Returns:
        Project ID
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        return cursor.lastrowid


def get_project(project_id: int, db_path: Optional[Path] = None) -> Optional[Dict]:
    """Gets a project by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def list_projects(db_path: Optional[Path] = None) -> List[Dict]:
    """Lists all projects."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


# =============================================================================
# Task Operations
# =============================================================================

def add_tasks(
    project_id: int,
    tasks: List[Dict[str, Any]],
    db_path: Optional[Path] = None
) -> int:
    """
    Adds tasks to a project.
    
    Args:
        project_id: Project ID
        tasks: List of task dictionaries
        db_path: Optional database path
        
    Returns:
        Number of tasks added
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        for task in tasks:
            deps = json.dumps(task.get("dependencies", []))
            cursor.execute("""
                INSERT OR REPLACE INTO tasks 
                (project_id, task_id, planned_duration, complexity, priority, 
                 required_skill, dependencies, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                task["task_id"],
                task["planned_duration"],
                task["complexity"],
                task["priority"],
                task.get("required_skill"),
                deps,
                task.get("status", "not_started")
            ))
        
        conn.commit()
        return len(tasks)


def get_project_tasks(
    project_id: int,
    db_path: Optional[Path] = None
) -> List[Dict]:
    """Gets all tasks for a project."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY task_id",
            (project_id,)
        )
        tasks = []
        for row in cursor.fetchall():
            task = dict(row)
            task["dependencies"] = json.loads(task["dependencies"] or "[]")
            tasks.append(task)
        return tasks


# =============================================================================
# Analysis Operations
# =============================================================================

def save_analysis(
    results: List[Dict[str, Any]],
    what_if_scenario: Optional[str] = None,
    model_type: str = "logistic",
    project_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> int:
    """
    Saves analysis results to database.
    
    Args:
        results: List of task risk results
        what_if_scenario: Optional scenario name
        model_type: ML model type used
        project_id: Optional project ID
        db_path: Optional database path
        
    Returns:
        Analysis ID
    """
    # Count risk levels
    high = sum(1 for r in results if r["risk_level"] == "High")
    medium = sum(1 for r in results if r["risk_level"] == "Medium")
    low = sum(1 for r in results if r["risk_level"] == "Low")
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Insert analysis record
        cursor.execute("""
            INSERT INTO analyses 
            (project_id, what_if_scenario, model_type, num_tasks,
             high_risk_count, medium_risk_count, low_risk_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, what_if_scenario, model_type,
            len(results), high, medium, low
        ))
        analysis_id = cursor.lastrowid
        
        # Insert individual results
        for result in results:
            cursor.execute("""
                INSERT INTO risk_results
                (analysis_id, task_id, risk_level, risk_score, delay_probability,
                 reasons, recommended_actions, what_if_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                result["task_id"],
                result["risk_level"],
                result["risk_score"],
                result["delay_probability"],
                json.dumps(result.get("reasons", [])),
                json.dumps(result.get("recommended_actions", [])),
                json.dumps(result.get("what_if_impact"))
            ))
        
        conn.commit()
        return analysis_id


def get_analysis(analysis_id: int, db_path: Optional[Path] = None) -> Optional[Dict]:
    """Gets an analysis with its results."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get analysis record
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        analysis = cursor.fetchone()
        if not analysis:
            return None
        
        result = dict(analysis)
        
        # Get risk results
        cursor.execute(
            "SELECT * FROM risk_results WHERE analysis_id = ?",
            (analysis_id,)
        )
        results = []
        for row in cursor.fetchall():
            r = dict(row)
            r["reasons"] = json.loads(r["reasons"] or "[]")
            r["recommended_actions"] = json.loads(r["recommended_actions"] or "[]")
            r["what_if_impact"] = json.loads(r["what_if_impact"]) if r["what_if_impact"] else None
            results.append(r)
        
        result["results"] = results
        return result


def list_analyses(
    limit: int = 20,
    project_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> List[Dict]:
    """Lists recent analyses."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        if project_id:
            cursor.execute("""
                SELECT * FROM analyses 
                WHERE project_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (project_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM analyses 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]


def get_analysis_stats(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Gets aggregate statistics from all analyses."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_analyses,
                SUM(num_tasks) as total_tasks_analyzed,
                SUM(high_risk_count) as total_high_risk,
                SUM(medium_risk_count) as total_medium_risk,
                SUM(low_risk_count) as total_low_risk,
                MAX(created_at) as last_analysis
            FROM analyses
        """)
        
        row = cursor.fetchone()
        return dict(row) if row else {}


# Initialize database on module import
init_database()
