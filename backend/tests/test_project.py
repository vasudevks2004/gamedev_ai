import pytest
from app.project.project_scanner import project_scanner

def test_fallback_project_query():
    ans_movement = project_scanner.query_project("Where is player movement implemented?")
    assert "movement" in ans_movement["answer"].lower() or "character" in ans_movement["answer"].lower()
    
    ans_weapon = project_scanner.query_project("Which class handles weapons?")
    assert "weapon" in ans_weapon["answer"].lower()

def test_project_header_parsing(tmp_path):
    # Create simulated Unreal Engine Source header
    header_content = """
    #pragma once
    #include "CoreMinimal.h"
    #include "GameFramework/Character.h"
    #include "MyCharacter.generated.h"

    UCLASS()
    class SHOOTER_API AMyCharacter : public ACharacter
    {
        GENERATED_BODY()
    public:
        UPROPERTY(EditAnywhere, BlueprintReadWrite)
        float Health;

        UFUNCTION(BlueprintCallable)
        void FireWeapon();
    };
    """
    fake_header = tmp_path / "MyCharacter.h"
    fake_header.write_text(header_content, encoding="utf-8")
    
    classes = project_scanner._parse_header_file(fake_header)
    assert len(classes) == 1
    c = classes[0]
    assert c.name == "AMyCharacter"
    assert c.base_class == "ACharacter"
    assert len(c.properties) >= 1
    assert len(c.functions) >= 1
