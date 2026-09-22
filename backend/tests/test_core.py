import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.prompt_engine import prompt_engine
from app.memory.user_profile import profile_manager, UserProfile
from app.memory.context_store import context_store, ActiveProjectContext
from app.core.llm_adapter import MockGameDevProvider

client = TestClient(app)

def test_user_profile():
    profile = profile_manager.get_profile()
    assert profile.name == "Ashwin"
    assert "Unreal Engine" in profile.skills
    assert "C++" in profile.skills
    assert "Blender" in profile.skills
    assert profile.skills["Unreal Engine"].overall_mastery >= 50

def test_context_store():
    context_store.update_context(
        project_name="TestShooter",
        current_file="TestCharacter.cpp",
        current_task="Movement Logic"
    )
    ctx = context_store.project_context
    assert ctx.project_name == "TestShooter"
    assert ctx.current_file == "TestCharacter.cpp"
    assert ctx.current_task == "Movement Logic"

def test_prompt_engine_classification():
    # Teaching mode classification
    mode = prompt_engine.classify_mode("What is inheritance and why is it used in Unreal Engine?")
    assert mode == "teaching"

    # Debugging mode classification
    mode = prompt_engine.classify_mode("Fatal error C2065: 'UStaticMeshComponent' undeclared identifier")
    assert mode == "debugging"

    # Planning mode classification
    mode = prompt_engine.classify_mode("I want to build a complete third person combat system roadmap")
    assert mode == "planning"

    # Coding mode classification
    mode = prompt_engine.classify_mode("Write code for a basic weapon trace function")
    assert mode == "coding"

def test_prompt_construction():
    profile = profile_manager.get_profile()
    ctx = context_store.project_context
    system_prompt, mode = prompt_engine.build_prompt(
        user_message="Explain Blueprint Interfaces and how they compare to casting in Unreal Engine 5",
        profile=profile,
        context=ctx
    )
    assert mode == "teaching"
    assert "Thangan" in system_prompt
    assert "Unreal Engine" in system_prompt
    assert "UNREAL ENGINE BLUEPRINT EXPERTISE" in system_prompt
    assert "Blueprint Interfaces" in system_prompt
    assert "Common Mistakes & Pitfalls" in system_prompt

def test_mock_provider():
    import asyncio
    provider = MockGameDevProvider()
    assert asyncio.run(provider.is_available()) is True
    
    reply = asyncio.run(provider.generate(
        system_prompt="Test Prompt",
        messages=[{"role": "user", "content": "What is inheritance?"}]
    ))
    assert "Mode: Teaching" in reply
    assert "Hands-on Practice Challenge" in reply

def test_api_endpoints():
    # Status
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["assistant_name"] == "Thangan"
    assert data["developer"] == "Ashwin"

    # Task tracking endpoint
    res = client.get("/api/task/active")
    assert res.status_code == 200
    task_data = res.json()
    assert "task_name" in task_data
    assert "overall_progress" in task_data
    assert "topic_breakdown" in task_data
    assert len(task_data["items"]) > 0

    # Toggle task item
    first_item_id = task_data["items"][0]["id"]
    prev_status = task_data["items"][0]["completed"]
    res = client.post("/api/task/toggle", json={"item_id": first_item_id})
    assert res.status_code == 200
    updated_items = res.json()["items"]
    assert updated_items[0]["completed"] != prev_status

    # Add task item
    res = client.post("/api/task/item/add", json={"title": "Test Niagara Particle Impact", "category": "Unreal Engine"})
    assert res.status_code == 200
    items_after_add = res.json()["items"]
    added_item = items_after_add[-1]
    assert added_item["title"] == "Test Niagara Particle Impact"
    assert added_item["category"] == "Unreal Engine"
    assert added_item["completed"] is False

    # Delete task item
    res = client.post("/api/task/item/delete", json={"item_id": added_item["id"]})
    assert res.status_code == 200
    items_after_del = res.json()["items"]
    assert all(i["id"] != added_item["id"] for i in items_after_del)

    # MiniBot endpoints
    res = client.post("/api/minibot/suggest")
    assert res.status_code == 200
    assert "tips" in res.json()
    assert len(res.json()["tips"]) > 0

    res = client.post("/api/minibot/ask", json={"question": "What is pure vs impure in Blueprint?"})
    assert res.status_code == 200
    assert "answer" in res.json()
    assert "Thangan" in res.json()["answer"]

