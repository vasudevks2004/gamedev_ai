import json
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

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=0.8) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        payload_messages = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": payload_messages, "stream": False}
            )
            res.raise_for_status()
            data = res.json()
            return data.get("message", {}).get("content", "")

    async def stream(self, system_prompt: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        payload_messages = [{"role": "system", "content": system_prompt}] + messages
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


class MockGameDevProvider(BaseLLMProvider):
    """High-fidelity local fallback provider for testing and offline scenarios."""
    async def is_available(self) -> bool:
        return True

    def _get_simulated_response(self, system_prompt: str, last_msg: str) -> str:
        last_lower = last_msg.lower()
        if "error" in last_lower or "c2065" in last_lower or "crash" in last_lower:
            return (
                "### Mode: Methodical Debugging\n\n"
                "1. **Error Identification**: The compiler is reporting an undeclared identifier or missing `#include` for an Unreal Engine class.\n"
                "2. **Location & Symbol**: In `WeaponComponent.cpp`, the reference to `UStaticMeshComponent` or weapon fire delegate lacks the corresponding header.\n"
                "3. **Root Cause Analysis**: Unreal Engine 5 uses Include-What-You-Use (IWYU). Engine headers are no longer monolithic in `Engine.h`.\n"
                "4. **Idiomatic Solution**:\n"
                "```cpp\n"
                "#include \"Components/StaticMeshComponent.h\"\n"
                "#include \"Engine/DamageEvents.h\"\n"
                "```\n"
                "5. **Verification**: Recompile via Live Coding (`Ctrl + Alt + F11`) or Visual Studio Build (`Ctrl + Shift + B`).\n"
                "6. **Prevention**: Always check the Unreal Engine documentation for the exact minimal header path required for each `UClass`."
            )
        elif "roadmap" in last_lower or "want to create" in last_lower or "combat" in last_lower:
            return (
                "### Mode: Study & Task Roadmap\n\n"
                "**Goal**: Build a Complete Third-Person Combat & Shooting System in UE5.\n\n"
                "**Prerequisites Checklist**:\n"
                "- [x] Basic Actor & Component architecture\n"
                "- [x] Enhanced Input Action & Mapping Context\n"
                "- [ ] Line Traces & Hit Results\n"
                "- [ ] Gameplay Damage System (`UGameplayStatics::ApplyDamage`)\n\n"
                "**7-Day Milestone Plan**:\n"
                "- **Day 1**: Base Weapon Actor class (`AWeaponBase`) & skeletal mesh socket attachment.\n"
                "- **Day 2**: Enhanced Input integration (Fire, Aim Down Sights, Reload).\n"
                "- **Day 3**: Raycast/LineTrace hit-scan logic and particle muzzle flash.\n"
                "- **Day 4**: Health Component & Damage Pipeline implementation.\n"
                "- **Day 5**: Animation Montages & Upper-body blend spaces in Animation Blueprint.\n"
                "- **Day 6**: Sound FX (Attenuation) & Niagara impact decals.\n"
                "- **Day 7**: Testing, weapon recoil curves, and code cleanup.\n\n"
                "**Recommended Resources**:\n"
                "- *Epic Dev Community*: Enhanced Input & Character Architecture Guide\n"
                "- *Tom Looman*: Professional Unreal Engine C++ Combat Architecture"
            )
        else:
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
                "6. **Common Pitfalls**:\n"
                "- Forgetting `virtual` in base class destructors.\n"
                "- Creating overly deep inheritance trees instead of using Composition (Actor Components).\n\n"
                "7. **Hands-on Practice Challenge**:\n"
                "Create a base class `AInteractableBase` with a virtual function `Interact()`, then derive `AChest` from it.\n\n"
                "8. **Quick Knowledge Quiz**:\n"
                "*Question*: In Unreal Engine C++, why should you prefer Actor Components (`UActorComponent`) over deep 8-level inheritance hierarchies?"
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
