"""
Tests for implementation planning API endpoints.

This module contains integration tests for the implementation planning API endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import json
import uuid

from research_implementation.api.planning import router
from research_implementation.implementation_planning.service import PlanningService
from research_implementation.api.models import Plan, PlanList, PlanOptions, TaskUpdate
from src.api.dependencies.auth import get_current_user
from src.api.models.user import User

# Mock data
MOCK_PAPER_UNDERSTANDING = {
    "title": "Vision Transformer Implementation",
    "model": {
        "name": "Vision Transformer",
        "type": "transformer",
        "architecture": {
            "components": [
                {
                    "name": "PatchEmbedding",
                    "type": "embedding",
                    "description": "Splits image into patches and embeds them"
                },
                {
                    "name": "TransformerEncoder",
                    "type": "encoder",
                    "description": "Processes patch embeddings with self-attention"
                }
            ]
        }
    }
}

MOCK_PLAN_OPTIONS = {
    "language": "python",
    "framework": "pytorch",
    "max_tasks": 10
}

# Mock user for testing
MOCK_USER = User(
    id="test_user_id",
    username="test_user",
    email="test@example.com",
    full_name="Test User",
    disabled=False
)

class TestPlanningAPI(unittest.TestCase):
    """Test cases for implementation planning API endpoints."""
    
    def setUp(self):
        """Set up test client and mock services."""
        from fastapi import FastAPI
        app = FastAPI()
        
        # Mock the authentication dependency
        app.dependency_overrides[get_current_user] = lambda: MOCK_USER
        
        # Mock the database dependency
        self.mock_db = MagicMock()
        self.mock_db.get_storage_path.return_value = "/tmp/test_plans"
        
        app.include_router(router)
        self.client = TestClient(app)
        
        # Create a test user token
        self.token = "test_token"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Mock PlanningService
        self.mock_planning_service = MagicMock(spec=PlanningService)
        self.planning_service_patcher = patch(
            'research_implementation.api.planning.PlanningService',
            return_value=self.mock_planning_service
        )
        self.mock_planning_service_class = self.planning_service_patcher.start()
        
        # Setup mock responses
        self.mock_plan_id = str(uuid.uuid4())
        self.mock_plan = {
            "id": self.mock_plan_id,
            "title": "Vision Transformer Implementation",
            "description": "Implementation plan for Vision Transformer",
            "paper_id": "paper_123",
            "components": [],
            "tasks": [
                {
                    "id": "task_1",
                    "name": "Setup Environment",
                    "description": "Initialize development environment",
                    "estimated_hours": 2,
                    "priority": 1,
                    "status": "pending",
                    "dependencies": [],
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            ],
            "requirements": {},
            "estimated_timeline": {},
            "critical_path": [],
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": MOCK_USER.username
        }
        
        self.mock_planning_service.create_implementation_plan.return_value = self.mock_plan
        self.mock_planning_service.get_plan.return_value = self.mock_plan
        self.mock_planning_service.update_plan.return_value = self.mock_plan
        self.mock_planning_service.update_task.return_value = self.mock_plan
        self.mock_planning_service.list_plans.return_value = [self.mock_plan]
        self.mock_planning_service.count_plans.return_value = 1
        self.mock_planning_service.delete_plan.return_value = True
        
    def tearDown(self):
        """Clean up after tests."""
        self.planning_service_patcher.stop()
        
    def test_create_plan(self):
        """Test creating a new implementation plan."""
        response = self.client.post(
            "/plans",
            headers=self.headers,
            json={
                "understanding": MOCK_PAPER_UNDERSTANDING,
                "options": MOCK_PLAN_OPTIONS
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        # Verify response structure
        self.assertIsInstance(data, dict)
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("components", data)
        self.assertIn("tasks", data)
        
        # Verify plan content
        self.assertEqual(data["title"], "Vision Transformer Implementation")
        self.assertTrue(any(c["name"] == "PatchEmbedding" for c in data["components"]))
        self.assertTrue(any(c["name"] == "TransformerEncoder" for c in data["components"]))
        
    def test_get_plan(self):
        """Test retrieving an implementation plan."""
        # First create a plan
        create_response = self.client.post(
            "/plans",
            headers=self.headers,
            json={
                "understanding": MOCK_PAPER_UNDERSTANDING,
                "options": MOCK_PLAN_OPTIONS
            }
        )
        plan_id = create_response.json()["id"]
        
        # Now retrieve it
        response = self.client.get(f"/plans/{plan_id}", headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify it's the same plan
        self.assertEqual(data["id"], plan_id)
        self.assertEqual(data["title"], "Vision Transformer Implementation")
        
    def test_update_plan(self):
        """Test updating an implementation plan."""
        # Create a plan first
        create_response = self.client.post(
            "/plans",
            headers=self.headers,
            json={
                "understanding": MOCK_PAPER_UNDERSTANDING,
                "options": MOCK_PLAN_OPTIONS
            }
        )
        plan_id = create_response.json()["id"]
        
        # Update the plan
        updates = {
            "title": "Updated ViT Implementation",
            "status": "in_progress"
        }
        response = self.client.put(
            f"/plans/{plan_id}",
            headers=self.headers,
            json=updates
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify updates were applied
        self.assertEqual(data["title"], "Updated ViT Implementation")
        self.assertEqual(data["status"], "in_progress")
        
    def test_update_task(self):
        """Test updating a task in an implementation plan."""
        # Create a plan first
        create_response = self.client.post(
            "/plans",
            headers=self.headers,
            json={
                "understanding": MOCK_PAPER_UNDERSTANDING,
                "options": MOCK_PLAN_OPTIONS
            }
        )
        plan_id = create_response.json()["id"]
        task_id = create_response.json()["tasks"][0]["id"]
        
        # Update a task
        updates = {
            "status": "in_progress",
            "estimated_hours": 4.5
        }
        response = self.client.put(
            f"/plans/{plan_id}/tasks/{task_id}",
            headers=self.headers,
            json=updates
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Find the updated task
        updated_task = next(t for t in data["tasks"] if t["id"] == task_id)
        self.assertEqual(updated_task["status"], "in_progress")
        self.assertEqual(updated_task["estimated_hours"], 4.5)
        
    def test_list_plans(self):
        """Test listing implementation plans with pagination and filtering."""
        # Create a few plans
        for i in range(3):
            self.client.post(
                "/plans",
                headers=self.headers,
                json={
                    "understanding": MOCK_PAPER_UNDERSTANDING,
                    "options": MOCK_PLAN_OPTIONS
                }
            )
            
        # Test pagination
        response = self.client.get(
            "/plans?skip=0&limit=2",
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIsInstance(data, dict)
        self.assertIn("total", data)
        self.assertIn("plans", data)
        self.assertEqual(len(data["plans"]), 2)
        self.assertEqual(data["total"] >= 3, True)
        
        # Test filtering
        response = self.client.get(
            "/plans?status=pending",
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        for plan in data["plans"]:
            self.assertEqual(plan["status"], "pending")
            
    def test_delete_plan(self):
        """Test deleting an implementation plan."""
        # Create a plan first
        create_response = self.client.post(
            "/plans",
            headers=self.headers,
            json={
                "understanding": MOCK_PAPER_UNDERSTANDING,
                "options": MOCK_PLAN_OPTIONS
            }
        )
        plan_id = create_response.json()["id"]
        
        # Delete the plan
        response = self.client.delete(f"/plans/{plan_id}", headers=self.headers)
        
        self.assertEqual(response.status_code, 204)
        
        # Verify plan is deleted
        get_response = self.client.get(f"/plans/{plan_id}", headers=self.headers)
        self.assertEqual(get_response.status_code, 404)
        
    def test_error_handling(self):
        """Test error handling in planning endpoints."""
        # Test invalid plan ID
        response = self.client.get("/plans/invalid_id", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        
        # Test invalid task update
        response = self.client.put(
            "/plans/some_id/tasks/task_id",
            headers=self.headers,
            json={
                "estimated_hours": -1  # Invalid negative hours
            }
        )
        self.assertEqual(response.status_code, 400)
        
        # Test missing auth token
        response = self.client.get("/plans")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()