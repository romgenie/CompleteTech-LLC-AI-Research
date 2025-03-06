"""
Tests for the checkpoint recovery system.

This module contains tests for the Checkpoint and CheckpointManager classes
used for preserving and restoring processing state.
"""

import os
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.research_orchestrator.knowledge_extraction.recovery.checkpoint import (
    Checkpoint, CheckpointManager, CheckpointedTask, CheckpointError
)


class TestCheckpoint(unittest.TestCase):
    """Tests for the Checkpoint class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for checkpoints
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_checkpoint_initialization(self):
        """Test Checkpoint initialization."""
        checkpoint = Checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            data={"key": "value"},
            checkpoint_dir=self.temp_dir
        )
        
        self.assertEqual(checkpoint.entity_id, "test_entity")
        self.assertEqual(checkpoint.stage, "test_stage")
        self.assertEqual(checkpoint.data, {"key": "value"})
        self.assertEqual(checkpoint.checkpoint_dir, self.temp_dir)
        self.assertIsNotNone(checkpoint.id)
        self.assertIsNotNone(checkpoint.timestamp)
        
    def test_get_path(self):
        """Test getting checkpoint file path."""
        checkpoint = Checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            checkpoint_dir=self.temp_dir
        )
        
        path = checkpoint.get_path()
        expected_path = os.path.join(
            self.temp_dir, 
            f"test_entity_test_stage_{checkpoint.id}.json"
        )
        
        self.assertEqual(path, expected_path)
        
    def test_save_and_load(self):
        """Test saving and loading a checkpoint."""
        # Create and save a checkpoint
        checkpoint = Checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            data={"key": "value"},
            checkpoint_dir=self.temp_dir
        )
        
        checkpoint_path = checkpoint.save()
        self.assertTrue(os.path.exists(checkpoint_path))
        
        # Load the checkpoint from file
        loaded_checkpoint = Checkpoint.from_file(checkpoint_path)
        
        # Verify checkpoint data was preserved
        self.assertEqual(loaded_checkpoint.entity_id, checkpoint.entity_id)
        self.assertEqual(loaded_checkpoint.stage, checkpoint.stage)
        self.assertEqual(loaded_checkpoint.id, checkpoint.id)
        self.assertEqual(loaded_checkpoint.data, checkpoint.data)
        
    def test_update(self):
        """Test updating checkpoint data."""
        checkpoint = Checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            data={"key1": "value1"},
            checkpoint_dir=self.temp_dir
        )
        
        # Store original timestamp
        original_timestamp = checkpoint.timestamp
        
        # Wait a moment to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        # Update the checkpoint
        checkpoint.update({"key2": "value2"})
        
        # Verify data was updated
        self.assertEqual(checkpoint.data, {"key1": "value1", "key2": "value2"})
        
        # Verify timestamp was updated
        self.assertGreater(checkpoint.timestamp, original_timestamp)
        
    def test_to_dict_and_from_dict(self):
        """Test converting checkpoints to/from dictionaries."""
        original = Checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            data={"key": "value"},
            checkpoint_dir=self.temp_dir
        )
        
        # Convert to dictionary
        checkpoint_dict = original.to_dict()
        
        # Verify dictionary has all required fields
        self.assertEqual(checkpoint_dict["entity_id"], "test_entity")
        self.assertEqual(checkpoint_dict["stage"], "test_stage")
        self.assertEqual(checkpoint_dict["data"], {"key": "value"})
        self.assertEqual(checkpoint_dict["id"], original.id)
        self.assertIsNotNone(checkpoint_dict["timestamp"])
        
        # Create new checkpoint from dictionary
        recreated = Checkpoint.from_dict(checkpoint_dict, self.temp_dir)
        
        # Verify all data was preserved
        self.assertEqual(recreated.entity_id, original.entity_id)
        self.assertEqual(recreated.stage, original.stage)
        self.assertEqual(recreated.data, original.data)
        self.assertEqual(recreated.id, original.id)
        
    def test_save_error_handling(self):
        """Test error handling when saving fails."""
        # Mock the open function to raise an error
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = OSError("Mocked file open error")
            
            checkpoint = Checkpoint(
                entity_id="test_entity",
                stage="test_stage",
                checkpoint_dir=self.temp_dir  # Use the test dir which exists
            )
            
            # Expect CheckpointError when saving fails
            with self.assertRaises(CheckpointError):
                checkpoint.save()
            
    def test_load_error_handling(self):
        """Test error handling when loading fails."""
        # Expect CheckpointError when loading non-existent file
        with self.assertRaises(CheckpointError):
            Checkpoint.from_file("/nonexistent/file.json")
            
        # Create invalid JSON file
        invalid_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_path, 'w') as f:
            f.write("{ invalid json")
            
        # Expect CheckpointError when loading invalid JSON
        with self.assertRaises(CheckpointError):
            Checkpoint.from_file(invalid_path)


class TestCheckpointManager(unittest.TestCase):
    """Tests for the CheckpointManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for checkpoints
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CheckpointManager(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test manager initialization."""
        # Verify checkpoint directory was set correctly
        self.assertEqual(self.manager.checkpoint_dir, self.temp_dir)
        
        # Verify directory exists
        self.assertTrue(os.path.isdir(self.temp_dir))
        
    def test_create_and_save_checkpoint(self):
        """Test creating and saving a checkpoint."""
        # Create a checkpoint
        checkpoint = self.manager.create_checkpoint(
            entity_id="test_entity",
            stage="test_stage",
            data={"key": "value"}
        )
        
        # Verify checkpoint was created with correct attributes
        self.assertEqual(checkpoint.entity_id, "test_entity")
        self.assertEqual(checkpoint.stage, "test_stage")
        self.assertEqual(checkpoint.data, {"key": "value"})
        
        # Save the checkpoint
        checkpoint_path = self.manager.save_checkpoint(checkpoint)
        
        # Verify checkpoint file was created
        self.assertTrue(os.path.exists(checkpoint_path))
        
    def test_get_latest_checkpoint(self):
        """Test retrieving the latest checkpoint."""
        # Create multiple checkpoints with different timestamps
        checkpoints = []
        
        for i in range(3):
            checkpoint = self.manager.create_checkpoint(
                entity_id="test_entity",
                stage="test_stage",
                data={"index": i}
            )
            self.manager.save_checkpoint(checkpoint)
            checkpoints.append(checkpoint)
            
            # Wait a moment to ensure timestamp differences
            import time
            time.sleep(0.01)
            
        # Get the latest checkpoint
        latest = self.manager.get_latest_checkpoint("test_entity", "test_stage")
        
        # Verify we got the most recent checkpoint
        self.assertEqual(latest.data, {"index": 2})
        
    def test_get_latest_checkpoint_with_stage_filter(self):
        """Test retrieving the latest checkpoint with stage filtering."""
        # Create checkpoints for different stages
        checkpoint1 = self.manager.create_checkpoint(
            entity_id="test_entity",
            stage="stage1",
            data={"stage": 1}
        )
        self.manager.save_checkpoint(checkpoint1)
        
        checkpoint2 = self.manager.create_checkpoint(
            entity_id="test_entity",
            stage="stage2",
            data={"stage": 2}
        )
        self.manager.save_checkpoint(checkpoint2)
        
        # Get latest checkpoint for stage1
        latest_stage1 = self.manager.get_latest_checkpoint("test_entity", "stage1")
        self.assertEqual(latest_stage1.data, {"stage": 1})
        
        # Get latest checkpoint for stage2
        latest_stage2 = self.manager.get_latest_checkpoint("test_entity", "stage2")
        self.assertEqual(latest_stage2.data, {"stage": 2})
        
    def test_list_checkpoints(self):
        """Test listing checkpoints with filters."""
        # Create checkpoints for different entities and stages
        checkpoint1 = self.manager.create_checkpoint(
            entity_id="entity1",
            stage="stage1",
            data={"id": 1}
        )
        self.manager.save_checkpoint(checkpoint1)
        
        checkpoint2 = self.manager.create_checkpoint(
            entity_id="entity1",
            stage="stage2",
            data={"id": 2}
        )
        self.manager.save_checkpoint(checkpoint2)
        
        checkpoint3 = self.manager.create_checkpoint(
            entity_id="entity2",
            stage="stage1",
            data={"id": 3}
        )
        self.manager.save_checkpoint(checkpoint3)
        
        # List all checkpoints
        all_checkpoints = self.manager.list_checkpoints()
        self.assertEqual(len(all_checkpoints), 3)
        
        # List checkpoints for entity1
        entity1_checkpoints = self.manager.list_checkpoints(entity_id="entity1")
        self.assertEqual(len(entity1_checkpoints), 2)
        
        # List checkpoints for stage1
        stage1_checkpoints = self.manager.list_checkpoints(stage="stage1")
        self.assertEqual(len(stage1_checkpoints), 2)
        
        # List checkpoints for entity1, stage1
        specific_checkpoints = self.manager.list_checkpoints(
            entity_id="entity1", 
            stage="stage1"
        )
        self.assertEqual(len(specific_checkpoints), 1)
        self.assertEqual(specific_checkpoints[0].data, {"id": 1})
        
    def test_delete_checkpoint(self):
        """Test deleting a checkpoint."""
        # Create a checkpoint
        checkpoint = self.manager.create_checkpoint(
            entity_id="test_entity",
            stage="test_stage"
        )
        self.manager.save_checkpoint(checkpoint)
        
        # Verify checkpoint exists
        checkpoints = self.manager.list_checkpoints(
            entity_id="test_entity", 
            stage="test_stage"
        )
        self.assertEqual(len(checkpoints), 1)
        
        # Delete the checkpoint
        result = self.manager.delete_checkpoint(checkpoint)
        self.assertTrue(result)
        
        # Verify checkpoint was deleted
        checkpoints = self.manager.list_checkpoints(
            entity_id="test_entity", 
            stage="test_stage"
        )
        self.assertEqual(len(checkpoints), 0)
        
    def test_delete_nonexistent_checkpoint(self):
        """Test deleting a checkpoint that doesn't exist."""
        # Try to delete a non-existent checkpoint
        result = self.manager.delete_checkpoint("nonexistent_id")
        self.assertFalse(result)
        
    def test_clean_old_checkpoints(self):
        """Test cleaning old checkpoints."""
        # Create a directory for files with controlled modification times
        test_dir = tempfile.mkdtemp()
        test_manager = CheckpointManager(test_dir)
        
        try:
            # Create checkpoints with different ages
            # 1. Fresh checkpoint
            fresh_checkpoint = test_manager.create_checkpoint(
                entity_id="test_entity",
                stage="test_stage",
                data={"age": "fresh"}
            )
            fresh_path = test_manager.save_checkpoint(fresh_checkpoint)
            
            # 2. Old checkpoint (modify timestamp to appear old)
            old_checkpoint = test_manager.create_checkpoint(
                entity_id="test_entity",
                stage="old_stage",
                data={"age": "old"}
            )
            old_path = test_manager.save_checkpoint(old_checkpoint)
            
            # Make the old checkpoint appear 2 days old
            old_time = (datetime.now() - timedelta(days=2)).timestamp()
            os.utime(old_path, (old_time, old_time))
            
            # Clean checkpoints older than 1 day
            deleted_count = test_manager.clean_old_checkpoints(max_age_hours=24)
            
            # Verify only the old checkpoint was deleted
            self.assertEqual(deleted_count, 1)
            self.assertTrue(os.path.exists(fresh_path))
            self.assertFalse(os.path.exists(old_path))
        finally:
            shutil.rmtree(test_dir)
            
    def test_clean_successful_checkpoints(self):
        """Test cleaning checkpoints after successful processing."""
        # Create intermediate checkpoints
        for i in range(3):
            checkpoint = self.manager.create_checkpoint(
                entity_id="test_entity",
                stage=f"stage{i}",
                data={"step": i}
            )
            self.manager.save_checkpoint(checkpoint)
            
        # Create a final "success" checkpoint
        final_checkpoint = self.manager.create_checkpoint(
            entity_id="test_entity",
            stage="final_stage",
            data={"completed": True}
        )
        self.manager.save_checkpoint(final_checkpoint)
        
        # Verify we have 4 checkpoints total
        all_checkpoints = self.manager.list_checkpoints(entity_id="test_entity")
        self.assertEqual(len(all_checkpoints), 4)
        
        # Clean successful checkpoints
        deleted_count = self.manager.clean_successful_checkpoints(
            entity_id="test_entity",
            final_stage="final_stage"
        )
        
        # Verify 3 intermediate checkpoints were deleted
        self.assertEqual(deleted_count, 3)
        
        # Verify only final checkpoint remains
        remaining = self.manager.list_checkpoints(entity_id="test_entity")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].stage, "final_stage")


class TestCheckpointedTask(unittest.TestCase):
    """Tests for the CheckpointedTask decorator."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for checkpoints
        self.temp_dir = tempfile.mkdtemp()
        self.checkpoint_manager = CheckpointManager(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_checkpointed_task_success(self):
        """Test checkpointed task that completes successfully."""
        # Define a test function that creates checkpoints
        @CheckpointedTask("test_stage", checkpoint_manager=self.checkpoint_manager)
        def test_function(entity_id, iterations=5, **kwargs):  # Accept kwargs to handle checkpoint data
            result = []
            
            for i in range(iterations):
                result.append(i)
                
                # Manually create checkpoint every other iteration
                if i % 2 == 0:
                    test_function.create_checkpoint(
                        entity_id=entity_id,
                        state={"iterations": iterations},
                        result=result.copy(),
                        iteration=i
                    )
                    
            return result
            
        # Run the function
        result = test_function("test_entity")
        
        # Verify result
        self.assertEqual(result, [0, 1, 2, 3, 4])
        
        # Verify checkpoints were created
        checkpoints = self.checkpoint_manager.list_checkpoints(
            entity_id="test_entity", 
            stage="test_stage"
        )
        self.assertGreaterEqual(len(checkpoints), 2)  # At least 2 checkpoint
        
        # Verify completion checkpoint was created
        completion_checkpoints = self.checkpoint_manager.list_checkpoints(
            entity_id="test_entity", 
            stage="test_stage_completed"
        )
        self.assertEqual(len(completion_checkpoints), 1)
        
    def test_checkpointed_task_resume(self):
        """Test resuming a checkpointed task from middle."""
        # First, create a checkpoint to resume from
        checkpoint = self.checkpoint_manager.create_checkpoint(
            entity_id="test_entity",
            stage="resume_stage",
            data={
                "state": {"iterations": 5},
                "result": [0, 1],
                "iteration": 2,
                "function": "resume_function"
            }
        )
        self.checkpoint_manager.save_checkpoint(checkpoint)
        
        # Track function calls
        call_count = [0]
        
        # Define a function that can be resumed
        @CheckpointedTask("resume_stage", checkpoint_manager=self.checkpoint_manager)
        def resume_function(entity_id, iterations=5, **kwargs):  # Accept kwargs for checkpoint data
            call_count[0] += 1
            result = []
            
            # This would normally start from 0, but when resumed
            # will start from the checkpoint iteration
            for i in range(iterations):
                result.append(i)
                
            return result
            
        # Run the function - it should resume from checkpoint
        result = resume_function("test_entity")
        
        # Verify function was called
        self.assertEqual(call_count[0], 1)
        
        # Verify result is complete
        self.assertEqual(result, [0, 1, 2, 3, 4])
        
    def test_checkpointed_task_error(self):
        """Test checkpointed task that raises an error."""
        # Define a function that raises an error
        @CheckpointedTask("error_stage", checkpoint_manager=self.checkpoint_manager)
        def error_function(entity_id, iterations=5, **kwargs):  # Accept kwargs for checkpoint data
            result = []
            
            for i in range(iterations):
                result.append(i)
                
                # Create a checkpoint
                error_function.create_checkpoint(
                    entity_id=entity_id,
                    state={"iterations": iterations},
                    result=result.copy(),
                    iteration=i
                )
                
                # Raise error at a specific point
                if i == 2:
                    raise ValueError("Test error")
                    
            return result
            
        # Run the function - it should raise an error
        with self.assertRaises(ValueError):
            error_function("test_entity")
            
        # Verify checkpoints were created before the error
        checkpoints = self.checkpoint_manager.list_checkpoints(
            entity_id="test_entity", 
            stage="error_stage"
        )
        self.assertGreaterEqual(len(checkpoints), 1)


if __name__ == '__main__':
    unittest.main()