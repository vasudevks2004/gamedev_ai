import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.core.config import settings

class SkillCategory(BaseModel):
    category_name: str
    overall_mastery: int = 50  # 0 to 100 percentage
    completed_topics: List[str] = Field(default_factory=list)
    in_progress_topics: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    name: str = "Ashwin"
    role: str = "Game Developer & Student"
    primary_engine: str = "Unreal Engine 5"
    core_tools: List[str] = Field(default_factory=lambda: [
        "Unreal Engine 5", "C++", "Blender", "Visual Studio / Rider", "Git"
    ])
    preferred_learning_style: str = "Pedagogical (Concept -> Unreal Engine -> Code -> Pitfalls -> Practice)"
    skills: Dict[str, SkillCategory] = Field(default_factory=lambda: {
        "Unreal Engine": SkillCategory(
            category_name="Unreal Engine",
            overall_mastery=65,
            completed_topics=[
                "Actor Architecture", "Components", "Enhanced Input", "GameMode & PlayerController",
                "Character Movement Component", "Blueprint Scripting", "Line Traces"
            ],
            in_progress_topics=["Multiplayer Replication", "Animation Blueprints & Control Rig"],
            weak_areas=["Network Replication / RPCs", "Nanite & Lumen Optimization"]
        ),
        "C++": SkillCategory(
            category_name="C++",
            overall_mastery=60,
            completed_topics=[
                "Modern C++ Basics", "OOP & Inheritance", "Pointers & References",
                "UCLASS & UPROPERTY Reflection", "UFUNCTION Specifiers", "Actor Lifecycle"
            ],
            in_progress_topics=["Smart Pointers vs Garbage Collection", "Delegates & Events"],
            weak_areas=["Dynamic Multicast Delegates", "Memory Profiling"]
        ),
        "Blender": SkillCategory(
            category_name="Blender",
            overall_mastery=55,
            completed_topics=[
                "Low-Poly Hard Surface Modeling", "Basic UV Unwrapping", "PBR Texture Setup",
                "FBX Export Scale & Coordinate Conventions"
            ],
            in_progress_topics=["Character Rigging & Weight Painting", "High-to-Low Normal Baking"],
            weak_areas=["Weight Painting Complex Deformations", "Root Motion Export for Unreal"]
        )
    })
    notes: List[str] = Field(default_factory=lambda: [
        "Ashwin prefers deep conceptual explanations before seeing code.",
        "Always highlight common beginner/intermediate pitfalls when explaining Unreal C++.",
        "Connect Blender techniques directly to Unreal Engine asset import requirements."
    ])

class ProfileManager:
    def __init__(self, profile_path: Path = None):
        self.profile_path = profile_path or (settings.profiles_dir / "ashwin_profile.json")
        self.profile = self.load_profile()

    def load_profile(self) -> UserProfile:
        if self.profile_path.exists():
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                print(f"[ProfileManager] Failed to load profile: {e}. Generating default.")
        
        default_profile = UserProfile()
        self.save_profile(default_profile)
        return default_profile

    def save_profile(self, profile: UserProfile = None):
        if profile:
            self.profile = profile
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile.model_dump(), f, indent=2)

    def get_profile(self) -> UserProfile:
        return self.profile

    def update_skill(self, category: str, topic: str, status: str):
        """status: 'completed', 'in_progress', or 'weak'"""
        if category in self.profile.skills:
            cat = self.profile.skills[category]
            # Remove from other lists first
            cat.completed_topics = [t for t in cat.completed_topics if t != topic]
            cat.in_progress_topics = [t for t in cat.in_progress_topics if t != topic]
            cat.weak_areas = [t for t in cat.weak_areas if t != topic]
            
            if status == "completed":
                cat.completed_topics.append(topic)
            elif status == "in_progress":
                cat.in_progress_topics.append(topic)
            elif status == "weak":
                cat.weak_areas.append(topic)
            self.save_profile()

profile_manager = ProfileManager()
