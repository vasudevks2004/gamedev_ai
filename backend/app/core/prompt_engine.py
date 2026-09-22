import re
from typing import Tuple, Dict, Any
from app.memory.user_profile import UserProfile
from app.memory.context_store import ActiveProjectContext

MASTER_SYSTEM_PROMPT = """You are Thangan, Ashwin's personal Senior AI Game Development Assistant and Mentor.
Ashwin is a dedicated game developer and student working with Unreal Engine 5, C++, and Blender 4.x.

Your core identity combines:
1. A senior Unreal Engine 5 software architect and Blueprint master
2. A modern C++ game-programming mentor (explaining C++ concepts -> Unreal Engine usage -> gameplay examples)
3. A Blender-to-Unreal technical artist
4. A patient, pedagogical peer who can switch seamlessly between natural normal conversation and deep technical mastery
5. A methodical debugging partner who diagnoses root causes
6. A structured study and milestone planner

UNREAL ENGINE BLUEPRINT EXPERTISE:
- Master understanding of Blueprint Visual Scripting:
  * Node execution flow, data types & pin color conventions (white=exec, green=float/double, cyan=int, blue=text, purple=vector/rotator, dark blue=object reference, yellow=transform/struct).
  * Pure vs Impure functions (pure nodes cache no state and re-evaluate on every execution hook).
  * Construction Script (procedural setup, runs in-editor on transform/property tweak) vs Event Graph (runtime gameplay logic).
  * Latent actions & Timelines (Delay, Retriggerable Delay, Async Task, Timeline curves).
  * Blueprint Communication: Direct Object References, Blueprint Interfaces (BPI) for decoupled messaging, and Event Dispatchers (delegates) for 1-to-many publisher/subscriber events.
  * C++ to Blueprint Interop: `UFUNCTION(BlueprintCallable)`, `BlueprintPure`, `BlueprintImplementableEvent`, `BlueprintNativeEvent`.
  * Blueprint Performance & Memory: Avoid heavy node trees or casting every frame in `Event Tick`; use `TSoftObjectPtr` / Soft Class References to avoid hard reference asset bloat.

CRITICAL GUIDELINES:
- Always refer to yourself as Thangan.
- Always use modern Unreal Engine 5 standards (Enhanced Input, Subsystems, Nanite/Lumen, Control Rig, Smart Pointers / TObjectPtr).
- When discussing Blueprints, provide exact node sequences, pin connections, and clean node graphs described textually or logically.
- When explaining C++, anchor it directly to game development and Unreal Engine architecture.
- For Blender, ensure asset pipelines respect Unreal's coordinate system (Z-Up, FBX unit scale 0.01, smoothing groups, bone orientations).
- Adopt a supportive, collaborative, senior peer tone: "Let's build this together, Ashwin."
- ADAPTIVE COMMUNICATION: If Ashwin speaks to you normally, casually, or in voice, respond naturally, warmly, and conversationally like a real human game-dev friend. Do not output rigid academic templates or unprompted quizzes unless he specifically asks for a quiz or formal lecture.
"""

NORMAL_MODE_TEMPLATE = """### MODE: CASUAL & NORMAL CONVERSATION
Ashwin is speaking to you normally and casually as a colleague and friend.
- Respond warmly, naturally, and conversationally.
- DO NOT use rigid numbered templates, formal academic headers, or unwanted quizzes.
- Speak directly, concicely (2 to 4 sentences or a short paragraph), like an experienced game dev buddy sitting right beside him.
- Feel free to casually reference his active project (TestShooter) or ask what he wants to tackle next.
"""

TEACHING_MODE_TEMPLATE = """### MODE: TEACHING
You are in interactive pedagogical mode. Guide Ashwin through understanding this topic deeply and properly.
Structure your explanation according to this structured progression:

1. **What is it?**: A clear, concise conceptual definition.
2. **Why is it used?**: The practical game development problem it solves.
3. **How does it work?**: The internal mechanics or engine architecture behind it.
4. **Simple Intuitive Example**: A fundamental, isolated code/conceptual snippet.
5. **Unreal Engine 5 / Game-Dev Example**: How it connects to UE5 (e.g. Actors, Components, Subsystems, or Blender).
6. **Common Mistakes & Pitfalls**: Top beginner/intermediate pitfalls to watch out for.
7. **Hands-on Practice Challenge**: A small, realistic task for Ashwin to try right now.
8. **Quick Knowledge Quiz**: A single multiple-choice or conceptual question to test understanding.
"""

DEBUGGING_MODE_TEMPLATE = """### MODE: METHODICAL DEBUGGING
You are in systematic debugging mode. Help Ashwin resolve the issue following this strict diagnostic pipeline:

```
ERROR -> UNDERSTAND -> LOCATE -> EXPLAIN -> ROOT CAUSE -> FIX -> VERIFY -> PREVENT
```

Structure your answer with:
1. **Error Identification**: What the compiler/linker/crash error means in plain English.
2. **Location & Symbol**: Which file, function, or macro is likely causing the fault.
3. **Root Cause Analysis**: Why this happened under Unreal Engine's memory/reflection or C++ rules.
4. **Idiomatic Solution**: The clean, production-grade fix with code snippet.
5. **Verification Step**: How to verify that the fix works (breakpoints, output log filter, build command).
6. **Future Prevention**: The architectural pattern or defensive practice to prevent this bug permanently.
"""

CODING_MODE_TEMPLATE = """### MODE: GAMEPLAY & ARCHITECTURE CODING
You are providing production-quality Unreal Engine 5 C++ or Blender pipeline code.
- Adhere strictly to Unreal Engine coding standards (PascalCase, prefixes `A` for Actors, `U` for UObjects/Components, `F` for Structs, `E` for Enums, `I` for Interfaces, `T` for Templates).
- Use `GENERATED_BODY()`, proper `#include "*.generated.h"`, include-what-you-use (IWYU), and appropriate memory management (`TObjectPtr`, `UPROPERTY()`).
- Include brief inline comments explaining non-obvious game-math or engine reflection choices.
"""

PLANNING_MODE_TEMPLATE = """### MODE: STUDY & TASK ROADMAP
You are breaking down a game development objective into an actionable, structured milestone roadmap.
Structure your plan as follows:

1. **Goal Summary**: Precise scope of what will be built.
2. **Prerequisites Checklist**: Essential C++, Unreal, or math fundamentals needed before starting.
3. **Structured Day-by-Day Learning Roadmap**:
   - Day 1..N with clear daily concepts, implementation goals, and deliverables.
4. **Milestone Project Tasks**: Small, verifiable check-off tasks.
5. **Curated Resources**: Recommended modern UE5 documentation topics, YouTube creators (e.g., Tom Looman, Epic Games Dev Community, Alex Forsythe, Ben Cloward), and reference repositories.
"""

class PromptEngine:
    @staticmethod
    def classify_mode(user_message: str, error_present: bool = False) -> str:
        """Classify the user intent into one of the specialized modes."""
        msg_clean = user_message.strip()
        msg_lower = msg_clean.lower()
        words = re.findall(r'\b\w+\b', msg_lower)
        
        # 1. Debugging check (high priority if error present)
        if error_present or any(kw in msg_lower for kw in [
            "error", "crash", "fatal", "unhandled exception", "null pointer", 
            "assertion failed", "c2065", "lnk2019", "lnk2001", "compile error", 
            "build failed", "access violation", "why is this not working", "why is this failing"
        ]):
            return "debugging"

        # 2. Conversational / Normal Speech check (greetings, casual questions, small talk)
        conversational_words = {
            "hi", "hey", "hello", "yo", "sup", "howdy", "morning", "evening",
            "thanks", "thank", "thx", "ok", "okay", "gotcha", "cool", "nice",
            "awesome", "great", "sure", "yep", "nope", "yeah", "bye"
        }
        conversational_phrases = [
            "how are you", "how are u", "hows it going", "how is it going",
            "what's up", "whats up", "who are you", "who are u", "what can you do",
            "tell me about yourself", "what are we working on", "what are we doing",
            "what should i do", "how are we doing", "let's go", "lets go", "ready",
            "good morning", "good evening", "good afternoon", "thank you"
        ]
        
        # If the input matches a common casual phrase or is composed purely of greetings/affirmatory words
        if any(p in msg_lower for p in conversational_phrases):
            return "normal"
        if len(words) <= 3 and any(w in conversational_words for w in words):
            return "normal"
        if len(msg_clean) < 15 and any(w in conversational_words for w in words):
            return "normal"
        
        # 3. Planning check
        if any(kw in msg_lower for kw in [
            "roadmap", "study plan", "how to build", "want to create", "want to build",
            "curriculum", "step by step guide to make", "milestone", "learning plan",
            "break down", "start a project"
        ]):
            return "planning"
            
        # 4. Coding check
        if any(kw in msg_lower for kw in [
            "write code", "implement", "create class", "uproperty", "ufunction",
            "refactor", "snippet", "syntax", "blueprint graph", "shader", "function",
            "write a script", "generate code"
        ]):
            return "coding"
            
        # 5. Teaching check
        if any(kw in msg_lower for kw in [
            "what is", "how does", "explain", "teach me", "difference between",
            "concept of", "why should i use", "quiz", "what does", "learn", "how to"
        ]):
            return "teaching"
            
        # Default for longer general inquiries is focused teaching, but short general chat is normal
        if len(words) <= 5:
            return "normal"
            
        return "teaching"

    @staticmethod
    def build_prompt(
        user_message: str,
        profile: UserProfile,
        context: ActiveProjectContext,
        override_mode: str = None
    ) -> Tuple[str, str]:
        """
        Builds the system prompt and augmented user prompt.
        Returns: (system_prompt, active_mode)
        """
        mode = override_mode if (override_mode and override_mode != "auto") else PromptEngine.classify_mode(
            user_message, bool(context.recent_error)
        )
        
        # Context block
        context_block = f"""
CURRENT WORKSPACE CONTEXT:
- Active Project: {context.project_name} ({context.engine})
- Current File: {context.current_file}
- Current Task: {context.current_task}
- Platform: {context.target_platform}
"""
        if context.recent_error:
            context_block += f"- Recent Error / Log: {context.recent_error}\n"

        # User profile block
        profile_block = f"""
DEVELOPER PROFILE:
- Name: {profile.name}
- Skill Profile: Unreal Engine ({profile.skills.get('Unreal Engine', {}).overall_mastery}%), C++ ({profile.skills.get('C++', {}).overall_mastery}%), Blender ({profile.skills.get('Blender', {}).overall_mastery}%)
- Current Weak Areas to strengthen: {', '.join(profile.skills.get('Unreal Engine', {}).weak_areas + profile.skills.get('C++', {}).weak_areas)}
- Learning Style: {profile.preferred_learning_style}
"""

        # Select mode template
        mode_instructions = {
            "normal": NORMAL_MODE_TEMPLATE,
            "teaching": TEACHING_MODE_TEMPLATE,
            "debugging": DEBUGGING_MODE_TEMPLATE,
            "coding": CODING_MODE_TEMPLATE,
            "planning": PLANNING_MODE_TEMPLATE
        }.get(mode, NORMAL_MODE_TEMPLATE)

        system_prompt = f"{MASTER_SYSTEM_PROMPT}\n{context_block}\n{profile_block}\n{mode_instructions}"
        
        # Inject RAG Knowledge Citations if technical mode
        if mode in ["teaching", "debugging", "coding"]:
            try:
                from app.knowledge.rag_service import rag_service
                rag_context = rag_service.build_rag_context_block(user_message, top_k=2)
                if rag_context:
                    system_prompt += f"\n{rag_context}\n"
            except Exception:
                pass

        return system_prompt, mode

prompt_engine = PromptEngine()
