import uuid
import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.prompt_engine import prompt_engine
from app.core.llm_adapter import llm_manager
from app.memory.user_profile import profile_manager, UserProfile
from app.memory.context_store import context_store, ActiveProjectContext, ChatMessage

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "auto"

class PlanRequest(BaseModel):
    goal: str
    timeframe_days: Optional[int] = 7

class SettingsUpdateRequest(BaseModel):
    active_provider: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None

class ToggleTaskRequest(BaseModel):
    item_id: str

class AssignTaskRequest(BaseModel):
    task_name: str
    description: Optional[str] = ""
    items: Optional[List[Dict[str, Any]]] = None

class AddTaskItemRequest(BaseModel):
    title: str
    category: Optional[str] = "Unreal Engine"

class DeleteTaskItemRequest(BaseModel):
    item_id: str

class MiniBotAskRequest(BaseModel):
    question: str

@router.get("/status")
async def get_status():
    provider = llm_manager.get_provider()
    is_online = await provider.is_available()
    return {
        "status": "online",
        "app_name": settings.app_name,
        "assistant_name": "Thangan",
        "version": settings.version,
        "active_provider": llm_manager.active_provider_name,
        "provider_available": is_online,
        "context": context_store.project_context.model_dump(),
        "developer": profile_manager.profile.name
    }

@router.get("/task/active")
def get_active_task():
    t = context_store.assigned_task
    return {
        "task_name": t.task_name,
        "description": t.description,
        "overall_progress": t.overall_progress,
        "topic_breakdown": t.topic_breakdown,
        "items": [item.model_dump() for item in t.items]
    }

@router.post("/task/toggle")
def toggle_task(req: ToggleTaskRequest):
    t = context_store.toggle_task_item(req.item_id)
    return {
        "status": "success",
        "overall_progress": t.overall_progress,
        "topic_breakdown": t.topic_breakdown,
        "items": [item.model_dump() for item in t.items]
    }

@router.post("/task/item/add")
def add_task_item(req: AddTaskItemRequest):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Task title cannot be empty")
    t = context_store.add_task_item(req.title.strip(), req.category or "Unreal Engine")
    return {
        "status": "success",
        "overall_progress": t.overall_progress,
        "topic_breakdown": t.topic_breakdown,
        "items": [item.model_dump() for item in t.items]
    }

@router.post("/task/item/delete")
def delete_task_item(req: DeleteTaskItemRequest):
    t = context_store.delete_task_item(req.item_id)
    return {
        "status": "success",
        "overall_progress": t.overall_progress,
        "topic_breakdown": t.topic_breakdown,
        "items": [item.model_dump() for item in t.items]
    }

@router.post("/task/assign")
def assign_task(req: AssignTaskRequest):
    from app.memory.context_store import TaskItem
    if req.items:
        items = [TaskItem(**item) for item in req.items]
    else:
        # Default intelligent multi-topic breakdown
        name_lower = req.task_name.lower()
        if "inventory" in name_lower:
            items = [
                TaskItem(id="1", title="Define FItemStruct in C++", category="C++", completed=False),
                TaskItem(id="2", title="Create UInventoryComponent", category="C++", completed=False),
                TaskItem(id="3", title="Model 3D Item Pickups in Blender", category="Blender", completed=False),
                TaskItem(id="4", title="Setup Item Textures & UVs in Blender", category="Blender", completed=False),
                TaskItem(id="5", title="Build Inventory UI Widget in Blueprints", category="Blueprints", completed=False),
                TaskItem(id="6", title="Implement Drag-and-Drop Slot Logic", category="Blueprints", completed=False),
                TaskItem(id="7", title="Line Trace Item Interaction in UE5", category="Unreal Engine", completed=False),
            ]
        elif "character" in name_lower or "model" in name_lower or "rig" in name_lower:
            items = [
                TaskItem(id="1", title="Model Base Mesh & Retopology", category="Blender", completed=False),
                TaskItem(id="2", title="High-to-Low Normal Map Baking", category="Blender", completed=False),
                TaskItem(id="3", title="Rig Armature with Root Bone in Blender", category="Blender", completed=False),
                TaskItem(id="4", title="Export FBX (Z-Up, 0.01 Scale)", category="Blender", completed=False),
                TaskItem(id="5", title="Import Skeletal Mesh & Physics Asset", category="Unreal Engine", completed=False),
                TaskItem(id="6", title="Create Animation Blueprint & State Machine", category="Animation", completed=False),
                TaskItem(id="7", title="Hook Enhanced Input in Character BP", category="Blueprints", completed=False),
            ]
        else:
            items = [
                TaskItem(id="1", title="Core C++ Architecture & Interfaces", category="C++", completed=False),
                TaskItem(id="2", title="Create Blueprint Derived Classes", category="Blueprints", completed=False),
                TaskItem(id="3", title="3D Assets & Socket Prep in Blender", category="Blender", completed=False),
                TaskItem(id="4", title="Collision & Physics Setup in UE5", category="Unreal Engine", completed=False),
                TaskItem(id="5", title="Animation & Control Rig Hookup", category="Animation", completed=False),
            ]
            
    t = context_store.assign_new_task(
        task_name=req.task_name,
        description=req.description or f"Development roadmap for {req.task_name}",
        items=items
    )
    return {
        "status": "assigned",
        "task_name": t.task_name,
        "overall_progress": t.overall_progress,
        "topic_breakdown": t.topic_breakdown,
        "items": [item.model_dump() for item in t.items]
    }

@router.post("/minibot/suggest")
async def minibot_suggest():
    ctx = context_store.project_context
    file_name = ctx.current_file
    tips = []
    if "component" in file_name.lower():
        tips = [
            {"icon": "fa-shield-halved", "title": "Memory Safety", "tip": "Use TObjectPtr<UMeshComponent> in UE5.4 instead of raw pointers."},
            {"icon": "fa-diagram-project", "title": "Blueprint Hook", "tip": "Expose events using UFUNCTION(BlueprintCallable, Category='Combat')."},
            {"icon": "fa-cube", "title": "Blender Socket", "tip": "Name socket 'SOCKET_WeaponMuzzle' in Blender FBX to auto-import in UE5."},
        ]
    elif "character" in file_name.lower():
        tips = [
            {"icon": "fa-person-running", "title": "Enhanced Input", "tip": "Bind actions in SetupPlayerInputComponent using FEnhancedInputComponentBinder."},
            {"icon": "fa-network-wired", "title": "Blueprint Interface", "tip": "Use BPI_Interaction instead of direct casting to avoid hard references."},
            {"icon": "fa-gauge-high", "title": "Tick Optimization", "tip": "Disable PrimaryActorTick.bCanEverTick if polling is not strictly needed."},
        ]
    else:
        tips = [
            {"icon": "fa-code", "title": "C++ IWYU", "tip": "Include minimal headers in .h and full implementations in .cpp."},
            {"icon": "fa-cubes", "title": "Blender Scale", "tip": "Set Scene Units to Metric (0.01) before exporting FBX for Unreal."},
            {"icon": "fa-circle-nodes", "title": "Blueprint Purity", "tip": "Mark getter functions as BlueprintPure to avoid execution wiring."},
        ]
    return {"file": file_name, "task": ctx.current_task, "tips": tips}

@router.post("/minibot/ask")
async def minibot_ask(req: MiniBotAskRequest):
    q = req.question.strip()
    if not q:
        return {"answer": "Ask me any quick question or syntax lookup!"}
    
    q_lower = q.lower()
    if "cast" in q_lower or "blueprint" in q_lower:
        return {"answer": "💡 *Thangan's Tip*: Casting checks class type at runtime. For decoupling, create a **Blueprint Interface** with an execute message so any actor can react without hard casting dependencies!"}
    elif "blender" in q_lower or "fbx" in q_lower or "scale" in q_lower:
        return {"answer": "💡 *Thangan's Tip*: In Blender, apply Transform (`Ctrl+A` -> All Transforms) and set Export FBX Scale to `0.01` (Unit Scale) with Forward: `-Z Forward` and Up: `Y Up` for UE5."}
    elif "uproperty" in q_lower or "macro" in q_lower:
        return {"answer": "💡 *Thangan's Tip*: Use `UPROPERTY(EditAnywhere, BlueprintReadWrite, Category='Weapon')` for tunable assets, and `VisibleAnywhere, BlueprintReadOnly` for components instantiated in constructor."}
    else:
        return {"answer": f"💡 *Thangan's Quick Note*: For '{q}', make sure to verify execution flow and memory boundaries in UE5. Let's dig deeper in the main chat if needed!"}


@router.get("/profile")
def get_profile():
    return profile_manager.get_profile()

@router.post("/profile")
def update_profile(profile: UserProfile):
    profile_manager.save_profile(profile)
    return {"status": "success", "profile": profile_manager.get_profile()}

@router.get("/context")
def get_context():
    return context_store.project_context

@router.post("/context")
def update_context(context_data: Dict[str, Any]):
    updated = context_store.update_context(**context_data)
    return {"status": "success", "context": updated}

@router.get("/history")
def get_history():
    return context_store.get_recent_history(50)

@router.delete("/history")
def clear_history():
    context_store.clear_history()
    return {"status": "cleared"}

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    profile = profile_manager.get_profile()
    ctx = context_store.project_context
    
    # Build prompt & determine mode
    system_prompt, mode = prompt_engine.build_prompt(
        user_message=user_msg,
        profile=profile,
        context=ctx,
        override_mode=req.mode
    )
    
    # Store user message
    now = datetime.datetime.now().isoformat()
    msg_id = str(uuid.uuid4())
    context_store.add_message(ChatMessage(
        id=msg_id,
        role="user",
        content=user_msg,
        mode=mode,
        timestamp=now
    ))
    
    # Prepare message payload
    history_messages = [
        {"role": m.role, "content": m.content}
        for m in context_store.get_recent_history(10)
    ]
    
    provider = llm_manager.get_provider()
    
    # Check if primary provider is available, fallback to mock gracefully if offline
    if not await provider.is_available():
        provider = llm_manager.providers["mock"]
        
    try:
        reply = await provider.generate(system_prompt, history_messages)
    except Exception as e:
        reply = f"[Provider Notice: Falling back to local offline mentor engine due to: {e}]\n\n" + \
                await llm_manager.providers["mock"].generate(system_prompt, history_messages)

    # Store assistant message
    context_store.add_message(ChatMessage(
        id=str(uuid.uuid4()),
        role="assistant",
        content=reply,
        mode=mode,
        timestamp=datetime.datetime.now().isoformat()
    ))
    
    return {
        "reply": reply,
        "mode": mode,
        "context": ctx.model_dump(),
        "provider": llm_manager.active_provider_name
    }

@router.post("/plan")
async def generate_plan(req: PlanRequest):
    profile = profile_manager.get_profile()
    ctx = context_store.project_context
    prompt_msg = f"I want to build: {req.goal}. Break this down into a structured {req.timeframe_days}-day learning and development roadmap with milestones and resources."
    
    system_prompt, mode = prompt_engine.build_prompt(
        user_message=prompt_msg,
        profile=profile,
        context=ctx,
        override_mode="planning"
    )
    
    provider = llm_manager.get_provider()
    if not await provider.is_available():
        provider = llm_manager.providers["mock"]
        
    reply = await provider.generate(system_prompt, [{"role": "user", "content": prompt_msg}])
    return {"goal": req.goal, "plan": reply, "mode": "planning"}

@router.post("/settings")
def update_settings(req: SettingsUpdateRequest):
    if req.active_provider:
        llm_manager.set_provider(
            req.active_provider,
            base_url=req.ollama_base_url,
            model=req.ollama_model
        )
    return {
        "status": "updated",
        "active_provider": llm_manager.active_provider_name
    }

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            user_msg = data.get("message", "").strip()
            mode_override = data.get("mode", "auto")
            
            if not user_msg:
                continue
                
            profile = profile_manager.get_profile()
            ctx = context_store.project_context
            
            system_prompt, mode = prompt_engine.build_prompt(
                user_message=user_msg,
                profile=profile,
                context=ctx,
                override_mode=mode_override
            )
            
            # Send mode event
            await websocket.send_json({"type": "start", "mode": mode})
            
            history_messages = [
                {"role": m.role, "content": m.content}
                for m in context_store.get_recent_history(10)
            ] + [{"role": "user", "content": user_msg}]
            
            provider = llm_manager.get_provider()
            if not await provider.is_available():
                provider = llm_manager.providers["mock"]
                
            full_response = ""
            async for chunk in provider.stream(system_prompt, history_messages):
                full_response += chunk
                await websocket.send_json({"type": "token", "content": chunk})
                
            # Complete
            await websocket.send_json({"type": "done", "full_content": full_response})
            
            # Save to history
            context_store.add_message(ChatMessage(
                id=str(uuid.uuid4()),
                role="user",
                content=user_msg,
                mode=mode,
                timestamp=datetime.datetime.now().isoformat()
            ))
            context_store.add_message(ChatMessage(
                id=str(uuid.uuid4()),
                role="assistant",
                content=full_response,
                mode=mode,
                timestamp=datetime.datetime.now().isoformat()
            ))
            
    except WebSocketDisconnect:
        pass


# --- PHASE 2: RAG KNOWLEDGE SYSTEM ---
class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    category: Optional[str] = None

@router.post("/knowledge/search")
def search_knowledge(req: KnowledgeSearchRequest):
    from app.knowledge.rag_service import rag_service
    results = rag_service.search(req.query, top_k=req.top_k, category_filter=req.category)
    return {"query": req.query, "results": results, "count": len(results)}


# --- PHASE 3 & 4: SCREEN VISION & ERROR DIAGNOSTICS ---
class ScreenInspectRequest(BaseModel):
    image_base64: str
    prompt: Optional[str] = "What's wrong here?"

@router.post("/screen/inspect")
async def inspect_screen(req: ScreenInspectRequest):
    from app.vision.vision_service import vision_service
    result = await vision_service.inspect_screen(
        image_base64=req.image_base64,
        user_prompt=req.prompt
    )
    return result


# --- PHASE 5: PROJECT AWARENESS SCANNER ---
class ProjectScanRequest(BaseModel):
    project_path: str

class ProjectQueryRequest(BaseModel):
    query: str

@router.post("/project/scan")
def scan_project_endpoint(req: ProjectScanRequest):
    from app.project.project_scanner import project_scanner
    try:
        scan_result = project_scanner.scan_project(req.project_path)
        # Also automatically update project context
        context_store.update_context(
            project_name=scan_result.project_name,
            engine=scan_result.engine_version or "Unreal Engine 5.4"
        )
        return {"status": "scanned", "project": scan_result.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/project/query")
def query_project_endpoint(req: ProjectQueryRequest):
    from app.project.project_scanner import project_scanner
    result = project_scanner.query_project(req.query)
    return result


# --- PHASE 6 & 7: STUDY ENGINE & VIDEO DISCOVERY ---
class ResourceRecommendRequest(BaseModel):
    topic: str

class RoadmapGenerateRequest(BaseModel):
    goal: str
    days: Optional[int] = 7

@router.post("/resources/recommend")
def recommend_resources(req: ResourceRecommendRequest):
    from app.study.resource_discovery import resource_discovery
    recommendations = resource_discovery.recommend(req.topic)
    return {"topic": req.topic, "resources": recommendations}

@router.get("/study/dashboard")
def get_study_dashboard():
    from app.study.study_engine import study_engine
    dashboard = study_engine.get_learning_dashboard()
    return dashboard.model_dump()

@router.post("/study/roadmap")
def generate_study_roadmap(req: RoadmapGenerateRequest):
    from app.study.study_engine import study_engine
    roadmap = study_engine.generate_task_roadmap(req.goal, days_count=req.days or 7)
    return roadmap.model_dump()

