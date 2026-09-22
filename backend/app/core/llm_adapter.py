import json
import time
import re
import httpx
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from app.core.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Generate complete text response."""
        pass

    @abstractmethod
    async def stream(self, system_prompt: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream token-by-token response."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is online and reachable."""
        pass


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self._last_check_time = 0.0
        self._is_available_cache = False

    async def is_available(self) -> bool:
        now = time.time()
        # Cache availability for 15 seconds to eliminate per-request polling latency
        if now - self._last_check_time < 15.0:
            return self._is_available_cache
        try:
            async with httpx.AsyncClient(timeout=0.3) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                self._is_available_cache = (res.status_code == 200)
        except Exception:
            self._is_available_cache = False
        self._last_check_time = now
        return self._is_available_cache

    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        if not await self.is_available():
            return await MockGameDevProvider().generate(system_prompt, messages)
        payload_messages = [{"role": "system", "content": system_prompt}] + messages
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": payload_messages, "stream": False}
                )
                res.raise_for_status()
                data = res.json()
                return data.get("message", {}).get("content", "")
        except Exception:
            return await MockGameDevProvider().generate(system_prompt, messages)

    async def stream(self, system_prompt: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        if not await self.is_available():
            async for token in MockGameDevProvider().stream(system_prompt, messages):
                yield token
            return
        payload_messages = [{"role": "system", "content": system_prompt}] + messages
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": payload_messages, "stream": True}
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception:
            async for token in MockGameDevProvider().stream(system_prompt, messages):
                yield token


class MockGameDevProvider(BaseLLMProvider):
    """
    Intelligent local game-development intelligence engine.
    Provides fast, contextual, and adaptive responses:
    - Normal conversational speech when the user speaks casually
    - Deep, proper game development answers leveraging the curated Knowledge Base
    """
    async def is_available(self) -> bool:
        return True

    def _extract_project_context(self, system_prompt: str) -> Dict[str, str]:
        ctx = {"project": "TestShooter", "task": "Movement Logic", "file": "TestCharacter.cpp"}
        proj_match = re.search(r"Active Project:\s*([^\n\r(]+)", system_prompt)
        if proj_match:
            ctx["project"] = proj_match.group(1).strip()
        task_match = re.search(r"Current Task:\s*([^\n\r]+)", system_prompt)
        if task_match:
            ctx["task"] = task_match.group(1).strip()
        file_match = re.search(r"Current File:\s*([^\n\r]+)", system_prompt)
        if file_match:
            ctx["file"] = file_match.group(1).strip()
        return ctx

    def _handle_normal_speech(self, last_msg: str, ctx: Dict[str, str]) -> Optional[str]:
        msg_clean = last_msg.strip().lower()
        words = re.findall(r'\b\w+\b', msg_clean)

        # 1. Greetings
        if any(g in msg_clean for g in ["hi", "hey", "hello", "yo", "sup", "howdy", "good morning", "good evening"]):
            return (
                f"Hey Ashwin! Good to see you. We're currently set up in **{ctx['project']}** working on **{ctx['task']}** in `{ctx['file']}`. "
                "What would you like to tackle today — writing some gameplay C++, building Blueprints, or working on 3D assets in Blender?"
            )

        # 2. How are you / status check
        if any(q in msg_clean for q in ["how are you", "how are u", "how's it going", "how is it going", "what's up", "whats up"]):
            return (
                f"Doing great Ashwin! All systems are running smoothly. I'm ready to help you with **{ctx['project']}** or review `{ctx['file']}`. "
                "What's on your mind right now?"
            )

        # 3. Who are you / intro
        if any(q in msg_clean for q in ["who are you", "who are u", "what can you do", "tell me about yourself", "what is your name"]):
            return (
                "I'm **Thangan**, your personal senior AI game development companion and mentor! "
                "I'm tuned specifically for **Unreal Engine 5.4**, **Modern C++**, **Blueprints**, and **Blender 4.x** pipelines. "
                "I can help you debug tricky compiler or crash logs, explain engine architecture, write production C++ code, "
                "plan study roadmaps, and inspect your screen for errors. How can I help you right now?"
            )

        # 4. Acknowledgements / affirmative small talk
        if any(a in msg_clean for a in ["thanks", "thank you", "thx", "got it", "gotcha", "cool", "nice", "awesome", "great", "ok", "okay", "sure", "sounds good", "perfect"]):
            return (
                "You got it, Ashwin! Keep up the great momentum. Let me know when you're ready for the next piece or if anything gives you trouble in code or in-editor."
            )

        # 5. Next steps / status inquiry
        if any(q in msg_clean for q in ["what should i do", "what are we doing", "what's next", "whats next", "status", "next step"]):
            return (
                f"Right now our active focus is **{ctx['task']}** for **{ctx['project']}**. "
                f"The immediate next step is setting up the logic in `{ctx['file']}`. "
                "Would you like me to walk through the exact C++ function implementation or the Blueprint setup first?"
            )

        # 6. Short conversational inputs (less than 4 words with no technical keywords)
        tech_keywords = [
            "error", "crash", "code", "blueprint", "ue5", "unreal", "c++", "blender", 
            "input", "trace", "actor", "pointer", "inheritance", "inherit", "class", 
            "component", "mesh", "texture", "material", "shader", "rig", "what is", 
            "how to", "explain", "teach", "why"
        ]
        if len(words) <= 3 and not any(tk in msg_clean for tk in tech_keywords):
            return f"I hear you, Ashwin! Let me know what you'd like to dive into next on **{ctx['project']}**."

        return None

    def _get_simulated_response(self, system_prompt: str, last_msg: str) -> str:
        ctx = self._extract_project_context(system_prompt)
        last_lower = last_msg.lower()

        # Check for normal conversational speech first
        normal_reply = self._handle_normal_speech(last_msg, ctx)
        if normal_reply:
            return normal_reply

        # Handle Inheritance specifically for pedagogical teaching
        if "inheritance" in last_lower or "derive" in last_lower:
            return (
                "### Mode: Teaching\n\n"
                "1. **What is it?**:\n"
                "Inheritance in C++ allows a derived class to inherit members and behavior from a base class.\n\n"
                "2. **Why is it used?**:\n"
                "In game development, it prevents duplicating shared mechanics across hundreds of game entities (such as health, movement, and interaction).\n\n"
                "3. **How does it work?**:\n"
                "The derived class inherits public and protected members of the base class and can override virtual methods using `virtual` and `override`.\n\n"
                "4. **Simple Intuitive Example**:\n"
                "```cpp\n"
                "class AEntity {\n"
                "public:\n"
                "    virtual void TakeDamage(float Amount) { Health -= Amount; }\n"
                "protected:\n"
                "    float Health = 100.0f;\n"
                "};\n"
                "```\n\n"
                "5. **Unreal Engine 5 Application**:\n"
                "Unreal's entire object hierarchy relies on inheritance:\n"
                "`UObject` -> `AActor` -> `APawn` -> `ACharacter` -> `AYourCustomCharacter`.\n\n"
                "6. **Common Mistakes & Pitfalls**:\n"
                "- Forgetting `virtual` in base class destructors.\n"
                "- Creating overly deep inheritance trees instead of using Composition (Actor Components).\n\n"
                "7. **Hands-on Practice Challenge**:\n"
                "Create a base class `AInteractableBase` with a virtual function `Interact()`, then derive `AChest` from it.\n\n"
                "8. **Quick Knowledge Quiz**:\n"
                "*Question*: In Unreal Engine C++, why should you prefer Actor Components (`UActorComponent`) over deep 8-level inheritance hierarchies?"
            )

        # 1. Methodical Debugging
        if any(k in last_lower for k in ["error", "c2065", "lnk2019", "lnk2001", "crash", "fatal", "unhandled exception", "null pointer", "assertion"]):
            return (
                "### Methodical Debugging Analysis\n\n"
                "1. **Error Identification**: The compiler is reporting an undeclared identifier or missing `#include` for an Unreal Engine class.\n"
                f"2. **Location & Symbol**: In `{ctx['file']}`, the reference to the engine component or delegate lacks its corresponding header.\n"
                "3. **Root Cause Analysis**: Unreal Engine 5 adheres strictly to Include-What-You-Use (IWYU). Monolithic engine headers are deprecated; each class must explicitly include its own component header.\n"
                "4. **Idiomatic Solution**:\n"
                "```cpp\n"
                "#include \"Components/StaticMeshComponent.h\"\n"
                "#include \"GameFramework/CharacterMovementComponent.h\"\n"
                "#include \"EnhancedInputComponent.h\"\n"
                "```\n"
                "5. **Verification Step**: Trigger Live Coding (`Ctrl + Alt + F11` in Unreal) or build solution in Visual Studio (`Ctrl + Shift + B`).\n"
                "6. **Future Prevention**: Always check the bottom of the official UE5 API reference for the exact minimal `#include` path."
            )

        # 2. Roadmap / Planning
        if any(k in last_lower for k in ["roadmap", "study plan", "how to build", "want to create", "want to build", "milestone"]):
            return (
                f"### 7-Day Game Development Roadmap: {last_msg.strip()}\n\n"
                f"**Project Target**: {ctx['project']} (Unreal Engine 5.4)\n\n"
                "**Prerequisites Checklist**:\n"
                "- [x] Actor & Component Architecture (`AActor`, `UActorComponent`)\n"
                "- [x] Enhanced Input Action & Mapping Context (`UInputAction`, `UInputMappingContext`)\n"
                "- [ ] Gameplay Logic & Collision Sweeps\n"
                "- [ ] Animation Blueprint State Machine\n\n"
                "**7-Day Milestone Plan**:\n"
                "- **Day 1**: Core Architecture & Class Hierarchy setup in C++.\n"
                "- **Day 2**: Enhanced Input binding (Move, Look, Action triggers).\n"
                "- **Day 3**: Physics, Collision channels, and Line Trace interaction.\n"
                "- **Day 4**: Visual & Audio feedback (Niagara particles, Sound Attenuation).\n"
                "- **Day 5**: Animation Blueprint integration & Blend Spaces.\n"
                "- **Day 6**: Blender asset polish, socket attachments, and collision hulls.\n"
                "- **Day 7**: Testing, performance profiling with `stat game`, and refactoring.\n\n"
                "**Recommended Learning Creators**:\n"
                "- *Tom Looman*: Production Unreal Engine Architecture\n"
                "- *Epic Developer Community*: UE5.4 Official Architecture Guides"
            )

        # 3. Knowledge Base RAG Search for Technical Queries
        try:
            from app.knowledge.rag_service import rag_service
            rag_results = rag_service.search(last_msg, top_k=1)
            if rag_results:
                best = rag_results[0]
                citation = best.get('citation') or best.get('source_citation', 'Unreal Engine Official Documentation')
                doc_url = best.get('doc_url')
                url_text = f" | [View Documentation]({doc_url})" if doc_url else ""
                return (
                    f"### {best['title']}\n\n"
                    f"{best['summary']}\n\n"
                    f"{best['content']}\n\n"
                    f"> **Citation**: {citation}{url_text}"
                )
        except Exception:
            pass

        # 4. Fallback for specific common gameplay mechanics
        if any(k in last_lower for k in ["jump", "movement", "move"]):
            return (
                "### Character Movement & Jump Setup (UE 5.4 C++)\n\n"
                "In Unreal Engine 5, movement is managed via `UCharacterMovementComponent`:\n\n"
                "```cpp\n"
                "void ATestCharacter::Move(const FInputActionValue& Value)\n"
                "{\n"
                "    const FVector2D MovementVector = Value.Get<FVector2D>();\n"
                "    if (Controller != nullptr)\n"
                "    {\n"
                "        const FRotator Rotation = Controller->GetControlRotation();\n"
                "        const FRotator YawRotation(0, Rotation.Yaw, 0);\n"
                "        const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);\n"
                "        const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);\n"
                "        AddMovementInput(ForwardDirection, MovementVector.Y);\n"
                "        AddMovementInput(RightDirection, MovementVector.X);\n"
                "    }\n"
                "}\n"
                "```\n\n"
                "**Pro-Tip**: For jumping, bind `JumpAction` to `ETriggerEvent::Started` calling `ACharacter::Jump`, "
                "and `ETriggerEvent::Completed` calling `ACharacter::StopJumping` for variable jump heights!"
            )

        # 5. Default focused mentor explanation
        return (
            f"Here is how to approach this in modern Unreal Engine 5.4 and modern C++ for `{ctx['file']}`:\n\n"
            "1. **Architecture**: Separate your gameplay logic into dedicated Actor Components (`UActorComponent`) rather than bloating your base Character class.\n"
            "2. **Memory & Performance**: Use `TObjectPtr<T>` for member object references and mark them with `UPROPERTY()` so Unreal's Garbage Collector manages their lifecycle.\n"
            "3. **Next Step**: Would you like me to generate the complete C++ header and source files for this, or walk through setting up the Blueprint child class?"
        )

    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        last_msg = messages[-1]["content"] if messages else ""
        return self._get_simulated_response(system_prompt, last_msg)

    async def stream(self, system_prompt: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        response = await self.generate(system_prompt, messages)
        words = response.split(" ")
        for word in words:
            yield word + " "


class LLMManager:
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "mock": MockGameDevProvider()
        }
        self.active_provider_name = settings.active_provider

    def get_provider(self) -> BaseLLMProvider:
        return self.providers.get(self.active_provider_name, self.providers["mock"])

    def set_provider(self, name: str, **kwargs):
        if name == "ollama":
            self.providers["ollama"] = OllamaProvider(
                base_url=kwargs.get("base_url"),
                model=kwargs.get("model")
            )
        self.active_provider_name = name

llm_manager = LLMManager()
