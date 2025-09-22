"""
Learning Agent for Browser-Use RPA

A wrapper system that adds learning and experience-replay capabilities to browser-use.
This agent can learn from successful task executions and replay learned workflows efficiently.
"""

from .agent import LearningAgent
from .knowledge_base import KnowledgeBase
from .workflow import Workflow, WorkflowStep

__all__ = ['LearningAgent', 'KnowledgeBase', 'Workflow', 'WorkflowStep']
