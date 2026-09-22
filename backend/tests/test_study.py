import pytest
from app.study.study_engine import study_engine
from app.study.resource_discovery import resource_discovery

def test_task_roadmap_generation_combat():
    roadmap = study_engine.generate_task_roadmap("Third Person Combat System", days_count=7)
    assert len(roadmap.days) == 7
    assert len(roadmap.prerequisites) > 0
    assert len(roadmap.milestones) > 0
    assert len(roadmap.recommended_resources) > 0
    assert "Day 1" in roadmap.days[0]["day"]
    assert "Day 7" in roadmap.days[6]["day"]

def test_study_dashboard():
    dashboard = study_engine.get_learning_dashboard()
    assert dashboard.unreal_progress_pct > 0
    assert dashboard.cpp_progress_pct > 0
    assert dashboard.blender_progress_pct > 0
    assert len(dashboard.completed_topics) > 0
    assert len(dashboard.weak_areas) > 0

def test_resource_recommendation_tiers():
    res = resource_discovery.recommend("Niagara")
    assert "Beginner" in res
    assert "Intermediate" in res
    assert "Advanced" in res
    
    # Check that each video item has full metadata
    all_videos = res["Beginner"] + res["Intermediate"] + res["Advanced"]
    assert len(all_videos) > 0
    for v in all_videos:
        assert v["title"]
        assert v["creator"]
        assert v["difficulty"] in ["Beginner", "Intermediate", "Advanced"]
        assert v["url"].startswith("http")
