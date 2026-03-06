# backend/routers/__init__.py
# Router initialization module

from .score import router as score_router
from .simulation import router as simulation_router
from .actions import router as actions_router
from .benchmark import router as benchmark_router

__all__ = [
    'score_router',
    'simulation_router', 
    'actions_router',
    'benchmark_router'
]