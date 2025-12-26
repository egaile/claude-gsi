"""
Utility for saving and loading API responses for debugging integration tests.

This module provides functions to:
- Save Claude API responses to files for later analysis
- Load previously saved responses for comparison
- Track response changes over time
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from app.models import (
    CloudPlatform,
    DataClassification,
    IntegrationPattern,
    ScaleTier,
    UseCase,
)
from tests.fixtures.mock_responses import ArchitectureResponseDict, StreamingResponseDict


class ResponseMetadata(TypedDict):
    """Metadata saved with each response."""
    combination_id: str
    use_case: str
    cloud_platform: str
    integration_pattern: str
    data_classification: str
    scale_tier: str
    timestamp: str
    error: str | None


class SavedResponse(TypedDict):
    """Structure of a saved response file."""
    metadata: ResponseMetadata
    response: ArchitectureResponseDict | StreamingResponseDict | dict[str, str]  # dict for error case


class ResponseListItem(TypedDict):
    """Item returned by list_saved_responses."""
    filepath: str
    metadata: ResponseMetadata


# Base directory for saved responses
RESPONSES_DIR = Path(__file__).parent / "responses"


def get_combination_id(
    use_case: UseCase,
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    data_classification: DataClassification,
    scale_tier: ScaleTier,
) -> str:
    """Generate a unique ID for a scenario combination."""
    return f"{use_case.value}_{cloud_platform.value}_{integration_pattern.value}_{data_classification.value}_{scale_tier.value}"


def save_response(
    response_data: ArchitectureResponseDict | StreamingResponseDict | dict[str, str],
    use_case: UseCase,
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    data_classification: DataClassification,
    scale_tier: ScaleTier,
    error: str | None = None,
) -> Path:
    """
    Save an API response to a file for debugging.

    Args:
        response_data: The parsed JSON response from Claude
        use_case: The use case enum value
        cloud_platform: The cloud platform enum value
        integration_pattern: The integration pattern enum value
        data_classification: The data classification enum value
        scale_tier: The scale tier enum value
        error: Optional error message if the response failed validation

    Returns:
        Path to the saved response file
    """
    # Ensure responses directory exists
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    combination_id = get_combination_id(
        use_case, cloud_platform, integration_pattern, data_classification, scale_tier
    )

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{combination_id}_{timestamp}.json"
    filepath = RESPONSES_DIR / filename

    # Wrap response with metadata
    saved_data = {
        "metadata": {
            "combination_id": combination_id,
            "use_case": use_case.value,
            "cloud_platform": cloud_platform.value,
            "integration_pattern": integration_pattern.value,
            "data_classification": data_classification.value,
            "scale_tier": scale_tier.value,
            "timestamp": timestamp,
            "error": error,
        },
        "response": response_data,
    }

    with open(filepath, "w") as f:
        json.dump(saved_data, f, indent=2)

    return filepath


def load_latest_response(
    use_case: UseCase,
    cloud_platform: CloudPlatform,
    integration_pattern: IntegrationPattern,
    data_classification: DataClassification,
    scale_tier: ScaleTier,
) -> SavedResponse | None:
    """
    Load the most recent saved response for a combination.

    Returns None if no saved response exists.
    """
    combination_id = get_combination_id(
        use_case, cloud_platform, integration_pattern, data_classification, scale_tier
    )

    # Find all files matching this combination
    pattern = f"{combination_id}_*.json"
    matching_files = sorted(RESPONSES_DIR.glob(pattern), reverse=True)

    if not matching_files:
        return None

    # Load the most recent one
    with open(matching_files[0]) as f:
        return json.load(f)


def list_saved_responses() -> list[ResponseListItem]:
    """
    List all saved responses with their metadata.

    Returns a list of metadata dictionaries sorted by timestamp (newest first).
    """
    results: list[ResponseListItem] = []

    if not RESPONSES_DIR.exists():
        return results

    for filepath in RESPONSES_DIR.glob("*.json"):
        if filepath.name == ".gitkeep":
            continue
        try:
            with open(filepath) as f:
                data: SavedResponse = json.load(f)
                results.append(
                    ResponseListItem(
                        filepath=str(filepath),
                        metadata=data.get("metadata", {}),  # type: ignore[typeddict-item]
                    )
                )
        except (json.JSONDecodeError, KeyError):
            continue

    # Sort by timestamp (newest first)
    results.sort(
        key=lambda x: x.get("metadata", {}).get("timestamp", ""),
        reverse=True,
    )

    return results


def get_failed_responses() -> list[ResponseListItem]:
    """
    Get all saved responses that had errors.

    Returns list of response metadata for responses that failed validation.
    """
    all_responses = list_saved_responses()
    return [r for r in all_responses if r.get("metadata", {}).get("error")]


def cleanup_old_responses(keep_latest: int = 5) -> int:
    """
    Remove old response files, keeping only the latest N for each combination.

    Args:
        keep_latest: Number of latest responses to keep per combination

    Returns:
        Number of files deleted
    """
    if not RESPONSES_DIR.exists():
        return 0

    # Group files by combination ID
    files_by_combination: dict[str, list[Path]] = defaultdict(list)

    for filepath in RESPONSES_DIR.glob("*.json"):
        if filepath.name == ".gitkeep":
            continue
        # Extract combination ID from filename
        parts = filepath.stem.rsplit("_", 2)
        if len(parts) >= 2:
            # Reconstruct combination ID (everything before last two parts which are timestamp)
            combination_id = "_".join(parts[:-2]) if len(parts) > 2 else parts[0]
            files_by_combination[combination_id].append(filepath)

    deleted = 0
    for combination_id, files in files_by_combination.items():
        # Sort by name (which includes timestamp)
        sorted_files = sorted(files, reverse=True)
        # Delete files beyond keep_latest
        for filepath in sorted_files[keep_latest:]:
            filepath.unlink()
            deleted += 1

    return deleted


def validate_response_structure(
    response_data: ArchitectureResponseDict | StreamingResponseDict | dict[str, object]
) -> list[str]:
    """
    Validate a response has all required fields.

    Returns a list of validation errors (empty if valid).
    """
    errors: list[str] = []

    # Check top-level sections
    required_sections = ["architecture", "compliance", "deployment"]
    for section in required_sections:
        if section not in response_data:
            errors.append(f"Missing required section: {section}")

    # Validate architecture section
    if "architecture" in response_data:
        arch = response_data["architecture"]
        if isinstance(arch, dict):
            if "mermaidDiagram" not in arch:
                errors.append("architecture.mermaidDiagram is missing")
            if "components" not in arch or not isinstance(arch.get("components"), list):
                errors.append("architecture.components is missing or not a list")
            if "dataFlows" not in arch or not isinstance(arch.get("dataFlows"), list):
                errors.append("architecture.dataFlows is missing or not a list")

    # Validate compliance section
    if "compliance" in response_data:
        comp = response_data["compliance"]
        if isinstance(comp, dict):
            if "checklist" not in comp or not isinstance(comp.get("checklist"), list):
                errors.append("compliance.checklist is missing or not a list")
            if "baaRequirements" not in comp:
                errors.append("compliance.baaRequirements is missing")

    # Validate deployment section
    if "deployment" in response_data:
        dep = response_data["deployment"]
        if isinstance(dep, dict):
            if "steps" not in dep or not isinstance(dep.get("steps"), list):
                errors.append("deployment.steps is missing or not a list")
            if "iamPolicies" not in dep or not isinstance(dep.get("iamPolicies"), list):
                errors.append("deployment.iamPolicies is missing or not a list")
            if "networkConfig" not in dep:
                errors.append("deployment.networkConfig is missing")
            if "monitoringSetup" not in dep:
                errors.append("deployment.monitoringSetup is missing")

    return errors


def validate_mermaid_syntax(diagram: str) -> list[str]:
    """
    Perform basic Mermaid syntax validation.

    Returns a list of syntax errors (empty if valid).
    """
    errors = []

    lines = diagram.strip().split("\n")
    if not lines:
        errors.append("Mermaid diagram is empty")
        return errors

    # Check diagram type
    first_line = lines[0].strip().lower()
    valid_types = ["flowchart", "graph", "sequencediagram", "classDiagram", "statediagram"]
    if not any(first_line.startswith(t.lower()) for t in valid_types):
        errors.append(f"Invalid diagram type: {first_line}")

    # Check for self-referential links
    for line in lines:
        if "-->" in line:
            parts = line.split("-->")
            if len(parts) == 2:
                source = parts[0].strip().split("[")[0].strip()
                target = parts[1].strip().split("[")[0].strip()
                if source and target and source == target:
                    errors.append(f"Self-referential link: {source} --> {source}")

    return errors


def validate_iam_policies(policies: list[str], cloud_platform: CloudPlatform) -> list[str]:
    """
    Validate IAM policy format based on cloud platform.

    Returns a list of validation errors (empty if valid).
    """
    errors = []

    for i, policy_str in enumerate(policies):
        try:
            policy = json.loads(policy_str)
        except json.JSONDecodeError as e:
            errors.append(f"Policy {i} is not valid JSON: {e}")
            continue

        if cloud_platform == CloudPlatform.AWS_BEDROCK:
            if "Version" not in policy:
                errors.append(f"AWS policy {i} missing Version")
            if "Statement" not in policy:
                errors.append(f"AWS policy {i} missing Statement")
            elif not isinstance(policy["Statement"], list):
                errors.append(f"AWS policy {i} Statement is not a list")
        else:
            if "bindings" not in policy:
                errors.append(f"GCP policy {i} missing bindings")
            elif not isinstance(policy["bindings"], list):
                errors.append(f"GCP policy {i} bindings is not a list")

    return errors
