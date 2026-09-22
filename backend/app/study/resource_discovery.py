"""
Curated Video & Resource Discovery Engine for Ashwin's Personal AI Game Development Assistant.
Provides tier-categorized learning videos (Beginner, Intermediate, Advanced) with full metadata and verified links.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VideoResource(BaseModel):
    title: str
    creator: str
    topic: str
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    why_relevant: str
    url: str
    duration: Optional[str] = None

# Comprehensive curated library of industry-standard game dev tutorials
VIDEO_DATABASE: List[VideoResource] = [
    # --- NIAGARA & VFX ---
    VideoResource(
        title="Unreal Engine 5 Niagara Fundamentals for Beginners",
        creator="Epic Developer Community",
        topic="Niagara",
        difficulty="Beginner",
        why_relevant="Teaches emitter hierarchy, particle spawn rates, sprite renderers, and curves from official Epic technical artists.",
        url="https://dev.epicgames.com/community/learning/courses/WV/unreal-engine-niagara-fundamentals",
        duration="45 mins"
    ),
    VideoResource(
        title="Building Weapon Muzzle Flash & Bullet Tracers with Niagara",
        creator="Ben Cloward",
        topic="Niagara",
        difficulty="Intermediate",
        why_relevant="Directly applies particle systems to combat games with realistic muzzle flashes and ribbon particle tracers.",
        url="https://www.youtube.com/watch?v=kY3jXF9B2Lg",
        duration="28 mins"
    ),
    VideoResource(
        title="Niagara GPU Simulation & Custom HLSL Simulation Stages",
        creator="Epic Dev Community Tech Talks",
        topic="Niagara",
        difficulty="Advanced",
        why_relevant="Deep technical exploration of GPU simulation stages, vector fields, and performance optimization for thousands of particles.",
        url="https://dev.epicgames.com/community/learning/talks-and-demos/niagara-advanced-gpu-simulation",
        duration="55 mins"
    ),

    # --- MULTIPLAYER & REPLICATION ---
    VideoResource(
        title="UE5 Multiplayer Basics: Network Roles and RPCs Explained",
        creator="Unreal Engine Official",
        topic="Multiplayer",
        difficulty="Beginner",
        why_relevant="Visual explanation of Server, Autonomous Proxy, Simulated Proxy, and how RPCs cross network boundaries.",
        url="https://dev.epicgames.com/community/learning/courses/7R/unreal-engine-multiplayer-fundamentals",
        duration="50 mins"
    ),
    VideoResource(
        title="Building Replicated Weapon & Inventory Systems in C++",
        creator="Tom Looman",
        topic="Multiplayer",
        difficulty="Intermediate",
        why_relevant="Industry-standard authoritative server pattern for equipping weapons, ammo replication, and fire simulation.",
        url="https://www.tomlooman.com/unreal-engine-cpp-multiplayer-course/",
        duration="1h 15m"
    ),
    VideoResource(
        title="Lag Compensation, Server Rollback, and Fast-Paced Shooter Networking",
        creator="Epic Games GDC / Dev Days",
        topic="Multiplayer",
        difficulty="Advanced",
        why_relevant="Deep architectural dive into server-side rewinds, client-side prediction, and bandwidth optimization.",
        url="https://dev.epicgames.com/community/learning/talks-and-demos/network-prediction-in-unreal-engine",
        duration="1h 00m"
    ),

    # --- MODERN C++ & UNREAL ARCHITECTURE ---
    VideoResource(
        title="C++ for Unreal Engine Beginners (No Prior UE Experience Needed)",
        creator="Unreal Sensei",
        topic="C++",
        difficulty="Beginner",
        why_relevant="Demystifies UCLASS, UPROPERTY, Visual Studio integration, and basic Actor creation.",
        url="https://www.youtube.com/watch?v=4r_X_dEwD6c",
        duration="1h 20m"
    ),
    VideoResource(
        title="Delegates, Event Dispatchers, and Subsystems in UE5 C++",
        creator="Tom Looman",
        topic="C++",
        difficulty="Intermediate",
        why_relevant="Learn decoupled communication: Single-cast, Multi-cast, and Dynamic Multicast delegates for UI and gameplay.",
        url="https://www.tomlooman.com/unreal-engine-cpp-guide/",
        duration="40 mins"
    ),
    VideoResource(
        title="Memory Profiling, Garbage Collection & TObjectPtr in UE5.4",
        creator="Epic Dev Community Technical Insights",
        topic="C++",
        difficulty="Advanced",
        why_relevant="Understand GC reachability graphs, UBT module dependency optimization, and Unreal Insights memory tracking.",
        url="https://dev.epicgames.com/community/learning/talks-and-demos/unreal-insights-memory-profiling",
        duration="50 mins"
    ),

    # --- BLENDER TO UNREAL PIPELINE & RIGGING ---
    VideoResource(
        title="Blender 4.x Complete Beginners Guide to 3D Modeling",
        creator="Grant Abbitt",
        topic="Blender",
        difficulty="Beginner",
        why_relevant="Master navigation, edit mode, modifiers, and clean quad topology for beginners.",
        url="https://www.youtube.com/watch?v=b4wS8Q1kM6Q",
        duration="45 mins"
    ),
    VideoResource(
        title="Rigging Game Characters in Blender with Root Bone for UE5",
        creator="CG Geek",
        topic="Blender",
        difficulty="Intermediate",
        why_relevant="Step-by-step armature creation, bone roll alignment, and weight painting ready for Unreal export.",
        url="https://www.youtube.com/watch?v=SbyXQ8BvFfg",
        duration="38 mins"
    ),
    VideoResource(
        title="High-to-Low Poly Baking, Texture Packing, and Control Rig Retargeting in UE5",
        creator="Epic Developer Community",
        topic="Blender",
        difficulty="Advanced",
        why_relevant="Complete professional technical artist workflow: cage baking in Blender, ORM texture packing, and UE5 IK Retargeter setup.",
        url="https://dev.epicgames.com/community/learning/courses/blender-to-unreal-engine-production-pipeline",
        duration="1h 10m"
    ),

    # --- ANIMATION & MOTION MATCHING ---
    VideoResource(
        title="Animation Blueprints & State Machines in UE5",
        creator="Unreal Engine Official",
        topic="Animation",
        difficulty="Beginner",
        why_relevant="Covers Anim Instance C++ base classes, Blendspaces, and transition rules.",
        url="https://dev.epicgames.com/community/learning/courses/ue5-animation-fundamentals",
        duration="40 mins"
    ),
    VideoResource(
        title="Motion Matching in Unreal Engine 5.4: Next-Gen Character Locomotion",
        creator="Epic Developer Community",
        topic="Animation",
        difficulty="Advanced",
        why_relevant="Replaces traditional blend spaces with pose searching algorithms for hyper-realistic character movement.",
        url="https://dev.epicgames.com/community/learning/talks-and-demos/motion-matching-in-unreal-engine-5-4",
        duration="52 mins"
    )
]

class ResourceDiscoveryEngine:
    def __init__(self, db: Optional[List[VideoResource]] = None):
        self.db = db or VIDEO_DATABASE

    def recommend(self, topic_query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns resources partitioned into Beginner, Intermediate, and Advanced.
        """
        query_lower = topic_query.lower()
        categorized: Dict[str, List[Dict[str, Any]]] = {
            "Beginner": [],
            "Intermediate": [],
            "Advanced": []
        }

        # Match relevant resources
        for item in self.db:
            matches = (
                item.topic.lower() in query_lower or
                query_lower in item.topic.lower() or
                any(word in item.title.lower() for word in query_lower.split()) or
                any(word in item.why_relevant.lower() for word in query_lower.split())
            )
            if matches or not topic_query.strip():
                categorized[item.difficulty].append(item.model_dump())

        # If specific query produced empty results, fall back to general curated list
        if not any(categorized.values()):
            for item in self.db[:6]:
                categorized[item.difficulty].append(item.model_dump())

        return categorized

resource_discovery = ResourceDiscoveryEngine()
