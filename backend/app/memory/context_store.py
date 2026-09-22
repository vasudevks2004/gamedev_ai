import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.config import settings

class TaskItem(BaseModel):
    id: str
    title: str
    category: str  # "Unreal Engine", "Blender", "C++", "Blueprints", "Animation", "Physics"
    completed: bool = False

class AssignedTask(BaseModel):
    task_name: str = "Third-Person Combat System"
    description: str = "Build complete weapon, line tracing, hit reaction and damage system"
    items: List[TaskItem] = Field(default_factory=lambda: [
        TaskItem(id="1", title="Create AWeaponBase C++ Class", category="C++", completed=True),
        TaskItem(id="2", title="Model Rifle & Align Sockets in Blender", category="Blender", completed=True),
        TaskItem(id="3", title="Export FBX with 0.01 Scale to UE5", category="Blender", completed=True),
        TaskItem(id="4", title="Implement Weapon Fire Line Trace", category="C++", completed=True),
        TaskItem(id="5", title="Setup Weapon Fire Enhanced Input Action", category="Unreal Engine", completed=False),
        TaskItem(id="6", title="Create Weapon Blueprint & Mesh Assign", category="Blueprints", completed=False),
        TaskItem(id="7", title="Animation Blueprint Upper-Body Montage Blend", category="Animation", completed=False),
        TaskItem(id="8", title="Health Component & Damage Pipeline", category="C++", completed=False),
        TaskItem(id="9", title="Niagara Muzzle Flash & Impact Decal", category="Unreal Engine", completed=False),
    ])

    @property
    def overall_progress(self) -> int:
        if not self.items:
            return 0
        done = sum(1 for item in self.items if item.completed)
        return int((done / len(self.items)) * 100)

    @property
    def topic_breakdown(self) -> Dict[str, Dict[str, Any]]:
        breakdown: Dict[str, Dict[str, Any]] = {}
        for item in self.items:
            cat = item.category
            if cat not in breakdown:
                breakdown[cat] = {"total": 0, "completed": 0, "percent": 0}
            breakdown[cat]["total"] += 1
            if item.completed:
                breakdown[cat]["completed"] += 1
        for cat, data in breakdown.items():
            if data["total"] > 0:
                data["percent"] = int((data["completed"] / data["total"]) * 100)
        return breakdown

class ActiveProjectContext(BaseModel):
    project_name: str = "ShooterGame"
    engine: str = "Unreal Engine 5.4"
    project_path: str = "V:/Projects/ShooterGame"
    current_task: str = "Third-Person Combat System"
    current_file: str = "WeaponComponent.cpp"
    recent_error: Optional[str] = None
    target_platform: str = "Windows (DX12)"

class ChatMessage(BaseModel):
    id: str
    role: str  # "user", "assistant", "system"
    content: str
    mode: str = "auto"
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextStore:
    def __init__(self, context_path: Path = None, task_path: Path = None):
        self.context_path = context_path or (settings.profiles_dir / "active_context.json")
        self.task_path = task_path or (settings.profiles_dir / "active_task.json")
        self.project_context = self.load_context()
        self.assigned_task = self.load_task()
        self.history: List[ChatMessage] = []

    def load_task(self) -> AssignedTask:
        if self.task_path.exists():
            try:
                with open(self.task_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    task = AssignedTask(**data)
                    if not task.items:
                        default_task = AssignedTask()
                        task.items = default_task.items
                        self.save_task(task)
                    return task
            except Exception as e:
                print(f"[ContextStore] Error loading task: {e}")
        t = AssignedTask()
        self.save_task(t)
        return t

    def save_task(self, task: AssignedTask = None):
        if task:
            self.assigned_task = task
        with open(self.task_path, "w", encoding="utf-8") as f:
            json.dump(self.assigned_task.model_dump(), f, indent=2)

    def toggle_task_item(self, item_id: str) -> AssignedTask:
        for item in self.assigned_task.items:
            if item.id == item_id:
                item.completed = not item.completed
                break
        self.save_task()
        return self.assigned_task

    def add_task_item(self, title: str, category: str = "Unreal Engine") -> AssignedTask:
        import uuid
        new_id = str(uuid.uuid4())[:8]
        new_item = TaskItem(id=new_id, title=title, category=category, completed=False)
        self.assigned_task.items.append(new_item)
        self.save_task()
        return self.assigned_task

    def delete_task_item(self, item_id: str) -> AssignedTask:
        self.assigned_task.items = [i for i in self.assigned_task.items if i.id != item_id]
        self.save_task()
        return self.assigned_task

    def assign_new_task(self, task_name: str, description: str, items: List[TaskItem]) -> AssignedTask:
        self.assigned_task = AssignedTask(
            task_name=task_name,
            description=description,
            items=items
        )
        self.save_task()
        self.update_context(current_task=task_name)
        return self.assigned_task

    def load_context(self) -> ActiveProjectContext:
        if self.context_path.exists():
            try:
                with open(self.context_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return ActiveProjectContext(**data)
            except Exception as e:
                print(f"[ContextStore] Error loading context: {e}")
        ctx = ActiveProjectContext()
        self.save_context(ctx)
        return ctx

    def save_context(self, ctx: ActiveProjectContext = None):
        if ctx:
            self.project_context = ctx
        with open(self.context_path, "w", encoding="utf-8") as f:
            json.dump(self.project_context.model_dump(), f, indent=2)

    def update_context(self, **kwargs) -> ActiveProjectContext:
        current_data = self.project_context.model_dump()
        for k, v in kwargs.items():
            if v is not None and k in current_data:
                current_data[k] = v
        self.project_context = ActiveProjectContext(**current_data)
        self.save_context()
        return self.project_context

    def add_message(self, message: ChatMessage):
        self.history.append(message)
        # Keep last 50 messages in active sliding window
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def get_recent_history(self, count: int = 10) -> List[ChatMessage]:
        return self.history[-count:]

    def clear_history(self):
        self.history = []

context_store = ContextStore()
