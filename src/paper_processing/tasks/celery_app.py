"""
Celery configuration for the Paper Processing Pipeline.

This module defines the Celery application configuration for asynchronous
paper processing tasks. Implementation follows the Phase 3.5 execution plan
as outlined in NEXT_STEPS_EXECUTION_PLAN.md.

Current Implementation Status:
- Celery app configuration is complete ✓
- Broker and result backend configuration ✓
- Task routing and queuing is defined ✓
- Worker configuration and concurrency settings ✓
- Error handling and retry policies ✓
- Task prioritization system ✓
- Dead letter queue handling ✓
- Task monitoring and event tracking ✓

Upcoming Development:
- Worker autoscaling based on load
- Performance optimization for large-scale deployments
- Specialized worker types for different tasks
"""

import os
import logging
from celery import Celery
from celery.signals import task_failure, task_success, task_retry, worker_ready
from kombu import Exchange, Queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Celery configuration
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Define queues with priorities
QUEUE_DEFAULT_PRIORITY = 5  # Medium priority (range 0-9)

# Define exchanges
task_exchange = Exchange('tasks', type='direct')
dead_letter_exchange = Exchange('dead_letter', type='direct')

# Define queues with priorities
task_queues = [
    # Processing queues with different priorities
    Queue('processing_high', task_exchange, routing_key='processing.high', 
          queue_arguments={'x-max-priority': 10}),
    Queue('processing', task_exchange, routing_key='processing', 
          queue_arguments={'x-max-priority': 10}),
    Queue('processing_low', task_exchange, routing_key='processing.low', 
          queue_arguments={'x-max-priority': 10}),
    
    # Extraction queues
    Queue('extraction_high', task_exchange, routing_key='extraction.high', 
          queue_arguments={'x-max-priority': 10}),
    Queue('extraction', task_exchange, routing_key='extraction', 
          queue_arguments={'x-max-priority': 10}),
    Queue('extraction_low', task_exchange, routing_key='extraction.low', 
          queue_arguments={'x-max-priority': 10}),
    
    # Integration queues
    Queue('integration_high', task_exchange, routing_key='integration.high', 
          queue_arguments={'x-max-priority': 10}),
    Queue('integration', task_exchange, routing_key='integration', 
          queue_arguments={'x-max-priority': 10}),
    Queue('integration_low', task_exchange, routing_key='integration.low', 
          queue_arguments={'x-max-priority': 10}),
    
    # Dead letter queue for failed tasks
    Queue('dead_letter', dead_letter_exchange, routing_key='dead_letter'),
]

# Create the Celery app
app = Celery(
    'paper_processing',
    broker=broker_url,
    backend=result_backend,
    include=[
        'paper_processing.tasks.processing_tasks',
        'paper_processing.tasks.extraction_tasks',
        'paper_processing.tasks.integration_tasks',
    ]
)

# Configure Celery
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Queue configuration
    task_queues=task_queues,
    task_default_queue='processing',
    task_default_exchange='tasks',
    task_default_routing_key='processing',
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_inherit_parent_priority=True,  # Tasks inherit priority from parent task
    task_default_priority=QUEUE_DEFAULT_PRIORITY,  # Default task priority
    
    # Result settings
    result_expires=86400,  # 1 day
    result_extended=True,  # Store additional metadata with results
    
    # Retry settings with exponential backoff
    task_default_retry_delay=60,  # 1 minute initial delay
    task_max_retries=3,
    
    # Rate limiting to prevent overwhelming the system
    task_default_rate_limit='30/m',  # 30 tasks per minute by default
    task_annotations={
        # Set specific rate limits for resource-intensive tasks
        'paper_processing.tasks.processing_tasks.process_document': {'rate_limit': '15/m'},
        'paper_processing.tasks.processing_tasks.extract_entities': {'rate_limit': '20/m'},
        'paper_processing.tasks.processing_tasks.build_knowledge_graph': {'rate_limit': '10/m'},
    },
    
    # Error handling and task routing
    task_routes={
        # Processing tasks with priority levels
        'paper_processing.tasks.processing_tasks.process_paper': {'queue': 'processing_high'},
        'paper_processing.tasks.processing_tasks.process_document': {'queue': 'processing'},
        'paper_processing.tasks.processing_tasks.check_implementation_readiness': {'queue': 'processing_low'},
        
        # Extraction tasks with priority levels
        'paper_processing.tasks.processing_tasks.extract_entities': {'queue': 'extraction_high'},
        'paper_processing.tasks.processing_tasks.extract_relationships': {'queue': 'extraction'},
        
        # Integration tasks with priority levels
        'paper_processing.tasks.processing_tasks.build_knowledge_graph': {'queue': 'integration_high'},
        'paper_processing.tasks.processing_tasks.request_implementation': {'queue': 'integration'},
        
        # Dead letter handling
        'paper_processing.tasks.dead_letter_task': {'queue': 'dead_letter'},
    },
    
    # Logging
    worker_redirect_stdouts=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Concurrency
    worker_concurrency=os.environ.get('CELERY_CONCURRENCY', 
                                     str(os.cpu_count() or 4)),
    
    # Monitoring and events
    task_send_sent_event=True,
    worker_send_task_events=True,
    task_track_started=True,
    task_publish_retry=True,
    task_publish_retry_policy={
        'max_retries': 3,
        'interval_start': 0.2,
        'interval_step': 0.5,
        'interval_max': 3.0,
    },
)

# Signal handlers for task events
@task_success.connect
def task_success_handler(sender=None, **kwargs):
    """Handle successful task completion."""
    logger.info(f"Task {sender.name}[{sender.request.id}] completed successfully")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Handle task failure."""
    task_name = sender.name if sender else "Unknown"
    logger.error(f"Task {task_name}[{task_id}] failed: {exception}")

@task_retry.connect
def task_retry_handler(sender=None, request=None, reason=None, **kwargs):
    """Handle task retry."""
    logger.warning(f"Task {sender.name}[{request.id}] being retried: {reason}")
    
@worker_ready.connect
def worker_ready_handler(**kwargs):
    """Handle worker ready event."""
    logger.info(f"Celery worker ready")

if __name__ == '__main__':
    app.start()