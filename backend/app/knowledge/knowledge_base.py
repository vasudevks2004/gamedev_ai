"""
Curated Knowledge Base for Ashwin's Personal AI Game Development Assistant.
Covers Unreal Engine 5.4, Modern C++ Game Programming, and Blender 4.x to UE5 pipelines.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class KnowledgeEntry(BaseModel):
    id: str
    title: str
    category: str  # "Unreal Engine", "C++", "Blender"
    tags: List[str]
    summary: str
    content: str
    source_citation: str
    doc_url: Optional[str] = None

# Comprehensive foundational game dev corpus
GAME_DEV_KNOWLEDGE_CORPUS: List[KnowledgeEntry] = [
    # --- UNREAL ENGINE 5.4 ---
    KnowledgeEntry(
        id="ue5-actor-lifecycle",
        title="Unreal Engine Actor Lifecycle & Initialization",
        category="Unreal Engine",
        tags=["actor", "lifecycle", "beginplay", "constructor", "tick", "uobject"],
        summary="Understanding when PostInitializeComponents, BeginPlay, Tick, and EndPlay run.",
        content="""The Actor lifecycle in Unreal Engine follows a strict deterministic flow:
1. Constructor (`AYourActor::AYourActor()`): Called when the CDO (Class Default Object) is created, and when spawning in editor or runtime. Setup default component hierarchies (`CreateDefaultSubobject`) here. NEVER access World or other actors here.
2. `PostInitializeComponents()`: All components have been initialized and registered. Good place to initialize component-dependent data.
3. `BeginPlay()`: Called when the game starts or actor is spawned into a running level. Safe to access `GetWorld()`, spawn other actors, register delegates, and interact with gameplay systems.
4. `Tick(float DeltaTime)`: Executed every frame if `PrimaryActorTick.bCanEverTick = true` and `bStartWithTickEnabled = true`. Optimize by disabling ticks when idle.
5. `EndPlay(const EEndPlayReason::Type EndPlayReason)`: Clean up timers, unbind delegates, and free dynamic non-UObject memory.""",
        source_citation="Unreal Engine 5 Official Documentation — Programming and Architecture > Actor Lifecycle",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-lifecycle-in-unreal-engine"
    ),
    KnowledgeEntry(
        id="ue5-enhanced-input",
        title="Enhanced Input System (UE 5.1+)",
        category="Unreal Engine",
        tags=["input", "enhanced input", "input action", "mapping context", "gameplay"],
        summary="Configuring UInputAction, UInputMappingContext, and binding in C++ with FEnhancedInputComponentBinder.",
        content="""Enhanced Input replaces the legacy input system with contextual, rebindable, and chorded actions:
1. Assets:
   - `UInputAction` (IA): Represents what happened (e.g. `IA_Move`, `IA_Fire`, `IA_Jump`). Set Value Type to `Axis2D (Vector2D)` for movement/look, or `Digital (bool)` for buttons.
   - `UInputMappingContext` (IMC): Maps physical keys to Input Actions and applies Modifiers (Negate, Swizzle) and Triggers (Hold, Pulse, Pressed).
2. Priority & Swapping: Add or remove IMCs at runtime using `UEnhancedInputLocalPlayerSubsystem::AddMappingContext(IMC, Priority)`.
3. C++ Binding in Character:
```cpp
#include \"EnhancedInputComponent.h\"
#include \"EnhancedInputSubsystems.h\"

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
    }
}
```""",
        source_citation="Epic Developer Community — Enhanced Input Architecture in UE5",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine"
    ),
    KnowledgeEntry(
        id="ue5-line-trace-collision",
        title="Unreal Engine Line Traces, Raycasting & Hit Results",
        category="Unreal Engine",
        tags=["line trace", "raycast", "collision", "hit result", "weapon", "interaction", "trace"],
        summary="Performing single and multi-channel raycasts, processing FHitResult, and collision channels.",
        content="""Line traces (raycasts) detect geometry and actors along a vector in 3D space:
1. Basic Single Line Trace by Channel in C++:
```cpp
#include "CollisionQueryParams.h"
#include "Engine/World.h"

FHitResult HitResult;
FVector StartLocation = CameraLocation;
FVector EndLocation = StartLocation + (CameraForwardVector * 5000.0f); // 50 meters

FCollisionQueryParams QueryParams;
QueryParams.AddIgnoredActor(this); // Ignore self
QueryParams.bTraceComplex = true;

bool bHit = GetWorld()->LineTraceSingleByChannel(
    HitResult,
    StartLocation,
    EndLocation,
    ECC_Visibility, // or ECC_GameTraceChannel1 for Weapons
    QueryParams
);

if (bHit && HitResult.GetActor())
{
    AActor* HitActor = HitResult.GetActor();
    FVector HitPoint = HitResult.ImpactPoint;
    FVector HitNormal = HitResult.ImpactNormal;
    // Apply damage or trigger interaction
}
```
2. Debug Line: Draw debug lines using `DrawDebugLine(GetWorld(), StartLocation, EndLocation, FColor::Red, false, 2.0f);`.
3. Collision Channels: Always configure custom Object Channels (e.g. `Projectile`, `Interactable`) in Project Settings -> Collision for high-performance filtering.""",
        source_citation="Unreal Engine 5 Official Documentation — Traces with Raycasts",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/traces-with-raycasts-in-unreal-engine"
    ),
    KnowledgeEntry(
        id="ue5-character-movement-jump",
        title="Character Movement, Jumping & Variable Jump Height",
        category="Unreal Engine",
        tags=["character", "movement", "jump", "charactermovement", "jumping", "locomotion"],
        summary="Configuring UCharacterMovementComponent, Enhanced Input binding, and variable jump height.",
        content="""Character movement in UE5 utilizes `UCharacterMovementComponent`:
1. Enhanced Input Movement Binding:
```cpp
void AMyCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D MovementVector = Value.Get<FVector2D>();
    if (Controller != nullptr)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
        AddMovementInput(ForwardDirection, MovementVector.Y);
        AddMovementInput(RightDirection, MovementVector.X);
    }
}
```
2. Variable Jump Height:
   - Bind `JumpAction` to `ETriggerEvent::Started` calling `ACharacter::Jump()`.
   - Bind `JumpAction` to `ETriggerEvent::Completed` calling `ACharacter::StopJumping()`.
   - In Character Blueprint or C++ constructor: set `JumpMaxHoldTime = 0.35f;` to allow players to jump higher by holding the button!
3. Air Control & Speeds:
   `GetCharacterMovement()->AirControl = 0.35f;`
   `GetCharacterMovement()->MaxWalkSpeed = 600.0f;`""",
        source_citation="Epic Dev Community — Unreal Engine 5 Character Movement Architecture",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/character-movement-component-in-unreal-engine"
    ),
    KnowledgeEntry(
        id="ue5-uproperty-specifiers",
        title="Unreal Engine Reflection & UPROPERTY Specifiers",
        category="Unreal Engine",
        tags=["uproperty", "reflection", "garbage collection", "memory", "blueprints"],
        summary="Best practice specifiers for properties, memory management, and Blueprint exposure.",
        content="""The Unreal Reflection system enables Garbage Collection, Serialization, Networking, and Blueprint visual editing:
- Asset References & Tunables: `UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = \"Combat\")`
- Defaults Only: `UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = \"Config\")`
- Components created in Constructor: `UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = \"Components\")`
- Replicated variables: `UPROPERTY(ReplicatedUsing = OnRep_Health)`
- Memory Protection: Any `UObject*` or `TObjectPtr<T>` MUST have a `UPROPERTY()` macro above it. Without it, Unreal's Garbage Collector cannot see the reference, causing premature deletion and dangling pointer crashes!""",
        source_citation="Unreal Engine 5 Official Documentation — Gameplay Architecture > Properties",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-uproperties"
    ),
    KnowledgeEntry(
        id="ue5-blueprints-vs-cpp",
        title="Blueprints vs C++ Architecture & Hybrid Best Practices",
        category="Unreal Engine",
        tags=["blueprints", "c++", "architecture", "performance", "interfaces"],
        summary="When to use C++ vs Blueprints, Blueprint Interfaces, and interop macros.",
        content="""The industry-standard Unreal Engine paradigm is Hybrid Architecture:
- Core Systems in C++: Math, complex state machines, data structures, networking, high-frequency tick calculations, and base actor classes.
- Tunable & Visual Layer in Blueprints: Sound FX cues, particle emitters, camera shake tweaks, UI design, and designer data balancing.
- Blueprint Function Interop:
  * `UFUNCTION(BlueprintCallable)`: Executable node with exec pins.
  * `UFUNCTION(BlueprintPure)`: No exec pins; executes on demand when output pin is queried. Must not alter internal state!
  * `UFUNCTION(BlueprintImplementableEvent)`: Declared in C++, implemented purely in Blueprint event graph.
  * `UFUNCTION(BlueprintNativeEvent)`: Declared in C++, has default C++ `_Implementation(..)`, overridable in Blueprint.
- Blueprint Interfaces (BPI):
  * Use BPIs for decoupled messaging between actors (e.g. `BPI_Damageable`, `BPI_Interactable`).
  * Direct casting (`Cast<AMyCharacter>`) creates hard references that load full asset trees into memory at startup.""",
        source_citation="Epic Dev Community — C++ and Blueprint Architectural Guidelines",
        doc_url="https://dev.epicgames.com/community/learning/guidelines/architecture"
    ),
    KnowledgeEntry(
        id="ue5-networking-replication",
        title="Multiplayer Replication, Authority, and RPCs",
        category="Unreal Engine",
        tags=["multiplayer", "replication", "rpc", "server", "client", "networking"],
        summary="Server-authoritative networking model, DOREPLIFETIME, and Remote Procedure Calls.",
        content="""Unreal Engine uses a Server-Authoritative client/server networking model:
1. Authority: Only the server (`HasAuthority() == true`) modifies true gameplay state (health, inventory, scoring).
2. Variable Replication:
```cpp
void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyCharacter, Health);
}
```
3. RPC Types:
   - Server RPC: `UFUNCTION(Server, Reliable, WithValidation)` — Client requests server to take an action (e.g. `Server_FireWeapon()`).
   - Client RPC: `UFUNCTION(Client, Reliable)` — Server sends private event to a specific client controller.
   - Multicast RPC: `UFUNCTION(NetMulticast, Unreliable)` — Server broadcasts visual/audio cosmetic events to all connected clients (e.g. muzzle flash, explosion).""",
        source_citation="Unreal Engine 5 Official Documentation — Network Overview",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine"
    ),

    # --- MODERN C++ IN GAME DEV ---
    KnowledgeEntry(
        id="cpp-pointers-and-smart-pointers",
        title="Modern C++ Pointers, TObjectPtr, and Memory Ownership",
        category="C++",
        tags=["c++", "pointers", "smart pointers", "tobjectptr", "memory", "raii"],
        summary="Raw pointers vs UE5 TObjectPtr vs TSharedPtr/TWeakPtr and RAII.",
        content="""In Game Development C++, understanding pointer ownership is essential to prevent memory leaks and crashes:
1. UE5 Member Pointers: In UE 5.0+, engine class members use `TObjectPtr<UStaticMeshComponent>` instead of `UStaticMeshComponent*`. It provides access tracking and editor debugging while remaining equivalent to raw pointers at runtime.
2. Non-UObject Smart Pointers:
   - `TSharedPtr<T>`: Reference-counted ownership for custom C++ classes not inheriting from `UObject`.
   - `TSharedRef<T>`: Non-nullable shared pointer.
   - `TWeakPtr<T>`: Non-owning observer that does not prevent destruction; use `.Pin()` before access.
   - `TUniquePtr<T>`: Single strict owner; moves only (`MoveTemp`).
3. RAII (Resource Acquisition Is Initialization): Resources are acquired in constructors and freed in destructors automatically when leaving scope.""",
        source_citation="Modern C++ for Game Developers & Unreal Engine Architecture",
        doc_url="https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines"
    ),
    KnowledgeEntry(
        id="cpp-inheritance-polymorphism",
        title="C++ Object-Oriented Programming & Game Architecture",
        category="C++",
        tags=["c++", "inheritance", "polymorphism", "virtual", "composition", "oop"],
        summary="Inheritance vs Composition in games, virtual dispatch, and Unreal Engine hierarchy.",
        content="""Object-Oriented Programming in Game Engines:
1. Inheritance: Enables base classes to share core interface and properties (`AActor -> APawn -> ACharacter`).
2. Virtual Functions: `virtual void TakeDamage(...)` allows polymorphic behavior, resolved via the Virtual Method Table (vtable) at runtime. Always mark overrides with `override`.
3. Virtual Destructor: Any base class with virtual methods MUST have `virtual ~Base() = default;` to avoid undefined behavior during deletion.
4. Composition over Inheritance:
   - Prefer Actor Components (`UActorComponent`, `USceneComponent`) for modular capabilities (e.g., `UHealthComponent`, `UInventoryComponent`, `UWeaponComponent`).
   - Deep inheritance trees (e.g., 6+ levels) create brittle, tightly coupled code; components allow any actor to gain abilities dynamically.""",
        source_citation="Game Programming Patterns by Robert Nystrom",
        doc_url="https://gameprogrammingpatterns.com/component.html"
    ),

    # --- BLENDER 4.X TO UNREAL ENGINE PIPELINE ---
    KnowledgeEntry(
        id="blender-to-ue5-export-workflow",
        title="Blender 4.x to Unreal Engine 5 FBX Pipeline",
        category="Blender",
        tags=["blender", "fbx", "scale", "units", "pipeline", "export"],
        summary="Correct Scene Units, Scale, Transform, and FBX export settings for seamless UE5 import.",
        content="""The flawless Blender 4.x to Unreal Engine FBX pipeline:
1. Blender Scene Setup:
   - Units: Metric
   - Unit Scale: `0.01` (Unreal operates in centimeters, Blender default is meters).
2. Transforms:
   - ALWAYS select object and hit `Ctrl + A` -> `Apply All Transforms` (Location, Rotation, Scale must be (0,0,0) and (1,1,1)).
3. FBX Export Settings:
   - Path Mode: `Copy` (check embed textures if needed)
   - Transform: Scale `1.0`, Forward: `-Z Forward`, Up: `Y Up` (or leave default and enable `Apply Scalings: FBX All`).
   - Geometry: Smoothing: `Face` (avoids UE5 'No smoothing group found' warning).
   - Armature: Uncheck `Add Leaf Bones` (prevents useless extra tip bones in UE5 skeletal tree).
4. Sockets: Add an Empty object parented to the mesh and prefix it with `SOCKET_Muzzle` or `SOCKET_Hand_R` to auto-convert to Unreal Sockets on import!""",
        source_citation="Epic Developer Community & Blender Game Asset Creation",
        doc_url="https://dev.epicgames.com/community/learning/tutorials/blender-to-unreal-engine"
    ),
    KnowledgeEntry(
        id="blender-rigging-root-motion",
        title="Blender Armature Rigging & Root Bone for UE5 Root Motion",
        category="Blender",
        tags=["blender", "rigging", "armature", "root motion", "animation", "ue5"],
        summary="Setting up root bone at (0,0,0) and bone orientation conventions for UE5 Mannequin compatibility.",
        content="""Configuring character armatures in Blender for Unreal Engine Character Movement & Root Motion:
1. Root Bone Rule:
   - The absolute top-level parent bone MUST be named `root` (or `Root`), placed exactly at world origin `(0, 0, 0)` with no rotation.
   - The `pelvis` / `hips` bone is parented directly to `root`.
2. Root Motion Mechanics:
   - When animating movement (dashes, rolls, attack lunges), keyframe the `root` bone along the ground plane.
   - In UE5 Animation Asset, check `EnableRootMotion`. The movement will drive the `UCharacterMovementComponent` collision capsule directly!
3. Bone Axis Alignment:
   - Blender bones point along the Y axis, whereas Unreal skeletal meshes expect X-along-bone or Z-Up. When importing into UE5, choose either the UE5 Skeleton or use the Control Rig IK Retargeter.""",
        source_citation="Blender Foundation & Epic Dev Community — Rigging for Games",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine"
    ),
    KnowledgeEntry(
        id="blender-high-to-low-baking",
        title="High-to-Low Poly Baking & Normal Maps (DirectX vs OpenGL)",
        category="Blender",
        tags=["blender", "baking", "normal maps", "high-poly", "low-poly", "pbr"],
        summary="Baking normal maps, cage extrusion, and flipping green channel for Unreal Engine.",
        content="""Creating optimized game-ready 3D assets:
1. High Poly: Sculpted or subdivided geometry with micro-details, bevels, and cloth wrinkles.
2. Low Poly: Optimized topology targeting game budget (e.g. 5k-25k tris for props, 30k-80k for main characters).
3. UV Unwrapping:
   - Keep UV islands within 0-1 UV space.
   - Hard geometric edges MUST be UV seams to prevent shading smoothing artifacts.
   - Leave adequate margin (16px for 2K texture, 32px for 4K texture) to prevent mipmap bleeding.
4. Normal Map Format:
   - Unreal Engine uses **DirectX** normal maps (Y- / Green inverted).
   - Blender viewport displays **OpenGL** normal maps (Y+).
   - In Unreal Engine Material Editor, you can double-click the normal texture and check `Flip Green Channel` if shading appears inverted/concave!""",
        source_citation="PBR Game Asset Production Handbook",
        doc_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/textures-in-unreal-engine"
    )
]
