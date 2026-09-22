import pytest
from app.vision.vision_service import vision_service

@pytest.mark.anyio
async def test_vision_inspection_c2065():
    dummy_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    result = await vision_service.inspect_screen(dummy_b64, "What does error C2065 mean?")
    
    assert result["status"] == "success"
    diag = result["diagnosis"]
    assert "Error Identification" in diag
    assert "C2065" in diag or "undeclared identifier" in diag
    assert "Include-What-You-Use" in diag or "IWYU" in diag
    assert "Prevention" in diag

@pytest.mark.anyio
async def test_vision_inspection_blueprint():
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    result = await vision_service.inspect_screen(dummy_b64, "My blueprint cast is failing with accessed none")
    
    assert result["status"] == "success"
    diag = result["diagnosis"]
    assert "Blueprint" in diag
    assert "Interface" in diag or "IsValid" in diag
    assert "Concrete Solution" in diag

@pytest.mark.anyio
async def test_vision_inspection_blender():
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    result = await vision_service.inspect_screen(dummy_b64, "Blender character armature scale is wrong in Unreal")
    
    assert result["status"] == "success"
    diag = result["diagnosis"]
    assert "Unit Scale" in diag or "0.01" in diag
    assert "root" in diag or "Armature" in diag
