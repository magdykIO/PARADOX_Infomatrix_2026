from fastapi import APIRouter

# Import separate routers using !absolute! paths
from routers.auth_router import auth_router
from routers.main_router import main_router

router_handler = APIRouter()

# Combining routers into one
router_handler.include_router(auth_router)
router_handler.include_router(main_router)
