# Celery Task Testing Guide

This guide provides comprehensive information about testing Celery tasks in the paper processing system.

## Test Structure

The Celery task tests are organized into three main categories:

1. **Task Creation and Execution Tests** - Verify that tasks can be created, executed, and handle errors correctly.
2. **Task Monitoring Tests** - Verify that task status can be checked and progress can be reported.
3. **Worker Configuration Tests** - Verify that Celery workers are properly configured.

## Test Fixtures

The test fixtures provide mocks for Celery and Redis components:

```python
@pytest.fixture
def mock_celery_app():
    """Mock Celery application for testing."""
    celery_app = MagicMock()
    celery_app.task.return_value = lambda f: f
    mock_async_result = MagicMock(spec=AsyncResult)
    mock_async_result.id = "test_task_id"
    celery_app.send_task.return_value = mock_async_result
    with patch('celery.Celery', return_value=celery_app):
        yield celery_app

@pytest.fixture
def mock_redis():
    """Mock Redis connection for Celery backend."""
    redis_client = MagicMock()
    redis_client.ping.return_value = True
    with patch('redis.Redis', return_value=redis_client):
        yield redis_client
```

## Task Creation and Execution

### Key Tests

1. **Task Creation** - Verifies that tasks can be created with correct parameters:
   ```python
   @pytest.mark.parametrize("task_name", [
       "process_paper", "extract_entities", "extract_relationships", "build_knowledge_graph"
   ])
   def test_task_creation(mock_celery_app, task_name):
       from paper_processing.tasks.paper_tasks import create_task
       task_result = create_task(task_name, paper_id="test_paper_id")
       assert task_result.id == "test_task_id"
       mock_celery_app.send_task.assert_called_once()
   ```

2. **Task Execution** - Tests successful task execution:
   ```python
   def test_task_execution(mock_celery_app, mock_celery_task, test_paper_file):
       from paper_processing.tasks.paper_tasks import process_paper
       result = process_paper("test_paper_id", file_path=test_paper_file)
       assert result.status == "SUCCESS"
   ```

3. **Error Handling** - Tests task error handling:
   ```python
   def test_task_error_handling(mock_celery_app, mock_celery_task):
       mock_celery_task.delay.return_value.status = "FAILURE"
       mock_celery_task.delay.return_value.failed.return_value = True
       result = extract_entities("test_paper_id")
       assert result.failed() is True
   ```

4. **Task Chains** - Tests creation and execution of task chains:
   ```python
   def test_task_chain(mock_celery_app, test_paper_file):
       result = create_processing_chain("test_paper_id", file_path=test_paper_file)
       assert result.id == "chain_task_id"
   ```

5. **Retry Mechanism** - Tests that tasks properly retry on errors:
   ```python
   def test_retry_mechanism(mock_celery_app, mock_celery_task):
       # Configure mock to raise exception then succeed
       mock_celery_task.side_effect = [Exception("Temporary error"), {"status": "success"}]
       result = extract_relationships("test_paper_id")
       assert result == {"status": "success"}
   ```

## Task Monitoring

### Key Tests

1. **Status Checking** - Verifies that task status can be checked:
   ```python
   def test_task_status_check(mock_task_state):
       status = get_task_status("test_task_id")
       assert status["status"] == "SUCCESS"
   ```

2. **History Tracking** - Tests recording and retrieving task history:
   ```python
   def test_task_monitoring_history(mock_redis, mock_task_state):
       history = get_task_history("test_paper_id")
       assert len(history) > 0
   ```

3. **Progress Tracking** - Tests progress updates for long-running tasks:
   ```python
   def test_progress_tracking(mock_redis):
       update_progress("test_task_id", 75)
       progress = get_progress("test_task_id")
       assert progress == 75
   ```

4. **State Mapping** - Tests mapping between Celery task states and application states:
   ```python
   @pytest.mark.parametrize("task_id,status,expected_state", [
       ("task1", "SUCCESS", "completed"),
       ("task2", "FAILURE", "failed"),
       ("task3", "PENDING", "in_progress")
   ])
   def test_task_state_mapping(mock_celery_app, task_id, status, expected_state):
       # Create a mock result with the specified status
       mock_result = MagicMock()
       mock_result.id = task_id
       mock_result.status = status
       state = map_task_state(mock_result)
       assert state == expected_state
   ```

## Worker Configuration

### Key Tests

1. **App Configuration** - Tests Celery app configuration:
   ```python
   def test_celery_app_configuration(mock_celery_app):
       init_celery(celery_app)
       assert mock_celery_app.conf.task_serializer == 'json'
   ```

2. **Task Routing** - Tests routing tasks to appropriate queues:
   ```python
   def test_task_routing(mock_celery_app):
       queue = get_queue_for_task('paper_processing.tasks.process_paper')
       assert queue == 'paper_processing'
   ```

3. **Worker Concurrency** - Tests worker concurrency configuration:
   ```python
   def test_worker_concurrency(mock_celery_app):
       with patch('multiprocessing.cpu_count', return_value=8):
           concurrency = configure_worker_concurrency()
           assert concurrency == 16
   ```

4. **Error Handling Configuration** - Tests error handling configuration:
   ```python
   def test_error_handling_configuration(mock_celery_app):
       configure_error_handling(mock_celery_app)
       assert mock_celery_app.conf.task_acks_late is True
       assert mock_celery_app.conf.task_max_retries == 3
   ```

## Running Celery Tests

Use the test runner script to run the Celery tests:

```bash
./run_tests.sh -p tests/integration_tests/celery/
```

Or run specific test files:

```bash
./run_tests.sh -f tests/integration_tests/celery/test_tasks.py
```

## Best Practices for Writing Celery Tests

1. **Use Proper Mocking** - Always mock Celery components to avoid actual task execution
2. **Test Task Parameters** - Verify that tasks are created with correct parameters
3. **Test Error Handling** - Ensure tasks properly handle and recover from errors
4. **Use Parameterized Tests** - Test different task types and states with parameterized tests
5. **Test Task Chains** - Verify that task chains and groups are properly created
6. **Import Inside Tests** - Import Celery-related modules inside test functions to ensure mocks are applied first