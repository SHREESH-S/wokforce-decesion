from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import random

app = FastAPI(
    title="AI Workforce Optimization Engine",
    description="Decoupled backend API for skill matching, capacity risk analytics, and telemetry simulation.",
    version="3.0.0"
)

# Enable CORS for external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class Engineer(BaseModel):
    id: str
    name: str
    skills: List[str]
    workload: int = Field(ge=0)
    max_capacity: int = Field(gt=0)
    location: str
    performance_score: float = Field(ge=0.0, le=1.0)
    hourly_rate: float

class Task(BaseModel):
    task_id: str
    task_name: str
    required_skill: str
    urgency: str
    sla_hours: int
    location: str
    assigned_to: Optional[str] = "Unassigned"

class OptimizationPayload(BaseModel):
    engineers: List[Engineer]
    tasks: List[Task]

# In-Memory Database
ENGINEERS_DB: List[Engineer] = [
    Engineer(id="E101", name="Alice Vance", skills=["Python", "Cloud", "Security"], workload=2, max_capacity=5, location="New York", performance_score=0.95, hourly_rate=85.0),
    Engineer(id="E102", name="Bob Smith", skills=["DevOps", "Cloud"], workload=4, max_capacity=5, location="London", performance_score=0.88, hourly_rate=75.0),
    Engineer(id="E103", name="Charlie Day", skills=["Security", "Network"], workload=1, max_capacity=4, location="New York", performance_score=0.79, hourly_rate=65.0),
    Engineer(id="E104", name="Diana Prince", skills=["Python", "DevOps"], workload=3, max_capacity=3, location="London", performance_score=0.92, hourly_rate=95.0),
]

TASKS_DB: List[Task] = [
    Task(task_id="T201", task_name="Cloud Migration Phase 2", required_skill="Cloud", urgency="Critical", sla_hours=3, location="New York"),
    Task(task_id="T202", task_name="Infrastructure Security Audit", required_skill="Security", urgency="High", sla_hours=6, location="New York"),
    Task(task_id="T203", task_name="CI/CD Pipeline Repair", required_skill="DevOps", urgency="Medium", sla_hours=12, location="London"),
]

# API Endpoints
@app.get("/api/v1/health")
def health_check():
    return {"status": "operational", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/engineers", response_model=List[Engineer])
def get_engineers():
    return ENGINEERS_DB

@app.get("/api/v1/tasks", response_model=List[Task])
def get_tasks():
    return TASKS_DB

@app.post("/api/v1/optimize")
def optimize_allocation(payload: OptimizationPayload):
    """Multi-factor optimization balancing performance, burnout risk, cost, and location proximity."""
    assignments = []
    urgency_scores = {"Critical": 50, "High": 35, "Medium": 20, "Low": 10}

    # Priority sorting based on SLA urgency
    sorted_tasks = sorted(
        payload.tasks,
        key=lambda t: urgency_scores.get(t.urgency, 10) + (24 - t.sla_hours),
        reverse=True
    )

    for task in sorted_tasks:
        if task.assigned_to == "Unassigned":
            candidates = []
            for eng in payload.engineers:
                # Skill qualification & capacity guardrails
                if eng.workload < eng.max_capacity:
                    if task.required_skill.lower() in [s.lower() for s in eng.skills]:
                        # Scoring Algorithm
                        perf_weight = eng.performance_score * 40
                        capacity_headroom = (1 - (eng.workload / eng.max_capacity)) * 30
                        proximity_bonus = 15 if eng.location == task.location else 0
                        cost_factor = max(0, 15 - (eng.hourly_rate / 10.0))

                        composite_score = round(perf_weight + capacity_headroom + proximity_bonus + cost_factor, 2)
                        candidates.append((composite_score, eng))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                score, match = candidates[0]
                assignments.append({
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "assigned_engineer_id": match.id,
                    "assigned_engineer_name": match.name,
                    "match_score": score,
                    "estimated_cost": round(match.hourly_rate * task.sla_hours, 2)
                })

    return {"status": "success", "total_assigned": len(assignments), "assignments": assignments}

@app.get("/api/v1/telemetry")
def get_telemetry():
    """Simulates dynamic real-time resource workload metrics."""
    overloaded = [e.name for e in ENGINEERS_DB if (e.workload / e.max_capacity) >= 0.8]
    critical_unassigned = [t.task_id for t in TASKS_DB if t.assigned_to == "Unassigned" and t.urgency == "Critical"]
    
    return {
        "burnout_risk_warnings": overloaded,
        "sla_breach_risks": critical_unassigned,
        "system_load_index": round(random.uniform(0.65, 0.92), 2),
        "health_status": "Warning" if (overloaded or critical_unassigned) else "Optimal"
    }
