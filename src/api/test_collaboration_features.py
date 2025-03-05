#!/usr/bin/env python3
"""
Test script to demonstrate collaborative features.

This script shows how the shared workspaces, comments/annotations,
and version control features work together.
"""

import json
import logging
from datetime import datetime
from uuid import uuid4

from src.api.services.workspace_service import WorkspaceService
from src.api.services.comment_service import CommentService
from src.api.services.version_service import VersionService

from src.api.models.workspace import WorkspaceCreate, WorkspaceVisibility
from src.api.models.comments import CommentCreate, CommentType, TextRange
from src.api.models.versioning import (
    VersionCreate, BranchCreate, MergeRequestCreate, 
    ContentChange, ChangeType
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the collaborative features test."""
    print("\n=== TESTING COLLABORATIVE FEATURES ===\n")
    
    # Create service instances
    workspace_service = WorkspaceService()
    comment_service = CommentService()
    version_service = VersionService()
    
    # Create test users
    users = {
        "alice": str(uuid4()),
        "bob": str(uuid4()),
        "charlie": str(uuid4()),
        "diana": str(uuid4())
    }
    
    print(f"Created test users: {', '.join(users.keys())}")
    
    # === TEST WORKSPACE SHARING ===
    print("\n--- Testing Workspace Sharing ---\n")
    
    # Alice creates a team
    team = workspace_service.create_team(
        name="AI Research Team",
        description="Team for AI research collaboration",
        created_by=users["alice"]
    )
    print(f"Alice created team: {team.name} (ID: {team.id})")
    
    # Alice creates a workspace
    workspace_data = WorkspaceCreate(
        name="Transformer Architecture Analysis",
        description="Research on transformer neural network architectures",
        team_id=team.id,
        visibility=WorkspaceVisibility.PRIVATE,
        tags=["transformers", "attention", "nlp"],
        metadata={"priority": "high"}
    )
    
    workspace = workspace_service.create_workspace(
        workspace_data=workspace_data,
        created_by=users["alice"]
    )
    print(f"Alice created workspace: {workspace.name} (ID: {workspace.id})")
    
    # Alice adds Bob to the workspace
    bob_member = workspace_service.add_workspace_member(
        workspace_id=workspace.id,
        user_id=users["bob"],
        role="member",
        invited_by=users["alice"]
    )
    print(f"Alice added Bob to workspace with role: {bob_member.role}")
    
    # Alice invites Charlie by email
    charlie_invite = workspace_service.create_workspace_invitation(
        workspace_id=workspace.id,
        email="charlie@example.com",
        role="reviewer",
        invited_by=users["alice"]
    )
    print(f"Alice invited Charlie to workspace with role: {charlie_invite.role}")
    
    # List workspace members
    members = workspace_service.list_workspace_members(workspace.id)
    print(f"Workspace has {len(members)} members:")
    for member in members:
        print(f"- {member.user_id} (role: {member.role})")
    
    # === TEST COMMENTS AND ANNOTATIONS ===
    print("\n--- Testing Comments and Annotations ---\n")
    
    # Create a mock research report
    report_id = str(uuid4())
    print(f"Created mock research report with ID: {report_id}")
    
    # Alice adds a general comment
    alice_comment = comment_service.create_comment(
        comment_data=CommentCreate(
            content="This report needs more experimental results to support the claims.",
            type=CommentType.GENERAL,
            target_type="report",
            target_id=report_id
        ),
        author_id=users["alice"]
    )
    print(f"Alice added a general comment: '{alice_comment.content}'")
    
    # Bob adds a specific annotation
    bob_annotation = comment_service.create_comment(
        comment_data=CommentCreate(
            content="This claim contradicts the results in Figure 3.",
            type=CommentType.ANNOTATION,
            target_type="report",
            target_id=report_id,
            text_range=TextRange(
                start_offset=1250,
                end_offset=1390,
                section_id="results"
            )
        ),
        author_id=users["bob"]
    )
    print(f"Bob added an annotation: '{bob_annotation.content}'")
    
    # Bob replies to Alice's comment
    bob_reply = comment_service.create_comment(
        comment_data=CommentCreate(
            content="I agree. I've started working on additional experiments.",
            type=CommentType.ANSWER,
            target_type="report",
            target_id=report_id,
            parent_id=alice_comment.id
        ),
        author_id=users["bob"]
    )
    print(f"Bob replied to Alice's comment: '{bob_reply.content}'")
    
    # Charlie adds a suggestion
    charlie_suggestion = comment_service.create_comment(
        comment_data=CommentCreate(
            content="We should cite Smith et al. (2022) here for comparison.",
            type=CommentType.SUGGESTION,
            target_type="report",
            target_id=report_id,
            text_range=TextRange(
                start_offset=2500,
                end_offset=2550,
                section_id="related_work"
            )
        ),
        author_id=users["charlie"]
    )
    print(f"Charlie added a suggestion: '{charlie_suggestion.content}'")
    
    # Alice resolves Charlie's suggestion
    resolved_comment = comment_service.resolve_comment(
        charlie_suggestion.id,
        resolved_by=users["alice"]
    )
    print(f"Alice resolved Charlie's suggestion (status: {resolved_comment.status})")
    
    # List all comments for the report
    comments = comment_service.list_comments(
        target_type="report",
        target_id=report_id
    )
    print(f"The report has {len(comments)} comments/annotations")
    
    # === TEST VERSION CONTROL ===
    print("\n--- Testing Version Control ---\n")
    
    # Create a mock project
    project_id = str(uuid4())
    print(f"Created mock project with ID: {project_id}")
    
    # Alice creates the initial version
    initial_version_data = VersionCreate(
        project_id=project_id,
        name="Initial draft",
        description="First draft of the research report",
        branch_name="main",
        changes=[
            ContentChange(
                path="introduction",
                type=ChangeType.ADDITION,
                after="This is the introduction section."
            ),
            ContentChange(
                path="method",
                type=ChangeType.ADDITION,
                after="This is the method section."
            )
        ]
    )
    
    initial_version = version_service.create_version(
        version_data=initial_version_data,
        created_by=users["alice"]
    )
    print(f"Alice created initial version {initial_version.version_number}: '{initial_version.name}'")
    
    # Bob creates a feature branch
    feature_branch_data = BranchCreate(
        project_id=project_id,
        name="improved-method",
        description="Adding improvements to the method section",
        created_from_version_id=initial_version.id
    )
    
    feature_branch = version_service.create_branch(
        branch_data=feature_branch_data,
        created_by=users["bob"]
    )
    print(f"Bob created branch: '{feature_branch.name}'")
    
    # Bob adds a version on his branch
    bob_version_data = VersionCreate(
        project_id=project_id,
        name="Improved method",
        description="Enhanced the method section with additional details",
        parent_version_id=initial_version.id,
        branch_name=feature_branch.name,
        changes=[
            ContentChange(
                path="method",
                type=ChangeType.MODIFICATION,
                before="This is the method section.",
                after="This is the improved method section with more details."
            ),
            ContentChange(
                path="results",
                type=ChangeType.ADDITION,
                after="Initial results of the improved method."
            )
        ]
    )
    
    bob_version = version_service.create_version(
        version_data=bob_version_data,
        created_by=users["bob"]
    )
    print(f"Bob added version {bob_version.version_number} on branch '{bob_version.branch_name}'")
    
    # Bob creates a merge request
    merge_request_data = MergeRequestCreate(
        project_id=project_id,
        title="Merge improved method",
        description="Adding the improved method to the main branch",
        source_branch=feature_branch.name,
        target_branch="main",
        reviewers=[users["alice"], users["charlie"]]
    )
    
    merge_request = version_service.create_merge_request(
        merge_request_data=merge_request_data,
        created_by=users["bob"]
    )
    print(f"Bob created merge request: '{merge_request.title}'")
    
    # Alice approves the merge request
    approved_mr = version_service.approve_merge_request(
        merge_request_id=merge_request.id,
        user_id=users["alice"]
    )
    print(f"Alice approved the merge request")
    
    # Bob merges the changes
    merged_mr = version_service.merge_merge_request(
        merge_request_id=merge_request.id,
        merged_by=users["bob"]
    )
    print(f"Bob merged the improved method (status: {merged_mr.status})")
    
    # List versions of the project
    versions = version_service.list_project_versions(project_id)
    print(f"Project has {len(versions)} versions:")
    for version in versions:
        print(f"- {version.version_number}: '{version.name}' on branch '{version.branch_name}'")
    
    # Compare versions
    diff = version_service.get_version_diff(bob_version.id, initial_version.id)
    print(f"Diff between versions: {json.dumps(diff, default=str)}")
    
    print("\nCollaborative features test completed successfully!")


if __name__ == "__main__":
    main()