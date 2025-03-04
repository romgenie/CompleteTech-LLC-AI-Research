"""
Celery configuration for the Paper Processing Pipeline.

This module defines the Celery application configuration for asynchronous
paper processing tasks. This is part of the Phase 3.5 implementation as
outlined in CODING_PROMPT.md.
"""

import os
from celery import Celery


# Celery configuration
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

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
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    
    # Result settings
    result_expires=86400,  # 1 day
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Error handling
    task_routes={
        'paper_processing.tasks.processing_tasks.*': {'queue': 'processing'},
        'paper_processing.tasks.extraction_tasks.*': {'queue': 'extraction'},
        'paper_processing.tasks.integration_tasks.*': {'queue': 'integration'},
    },
    
    # Logging
    worker_redirect_stdouts=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    
    # Concurrency
    worker_concurrency=os.cpu_count(),
    
    # Monitoring
    task_send_sent_event=True,
    worker_send_task_events=True,
)


if __name__ == '__main__':
    app.start()