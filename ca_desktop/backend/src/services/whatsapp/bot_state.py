"""Bot state management for WhatsApp integration."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ...database import get_db


class BotStateManager:
    """Manages bot state for WhatsApp conversations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def is_bot_enabled(self, phone: str) -> bool:
        """Check if bot should respond or CA is manually chatting."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        if not state:
            # First time interaction, bot is enabled by default
            return True
        
        return state.bot_enabled
    
    def disable_bot(self, phone: str):
        """CA takes over chat manually."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        if state:
            state.bot_enabled = False
            state.last_interaction = datetime.now(timezone.utc)
        else:
            state = WhatsAppBotState(
                phone_number=phone,
                bot_enabled=False,
                last_interaction=datetime.now(timezone.utc)
            )
            self.db.add(state)
        
        self.db.commit()
    
    def enable_bot(self, phone: str):
        """Re-enable bot for this chat."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        if state:
            state.bot_enabled = True
            state.last_interaction = datetime.now(timezone.utc)
        else:
            state = WhatsAppBotState(
                phone_number=phone,
                bot_enabled=True,
                last_interaction=datetime.now(timezone.utc)
            )
            self.db.add(state)
        
        self.db.commit()
    
    def set_current_flow(self, phone: str, flow: Optional[str]):
        """Track if user is in download/upload flow."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        if state:
            state.current_flow = flow
            state.last_interaction = datetime.now(timezone.utc)
        else:
            state = WhatsAppBotState(
                phone_number=phone,
                bot_enabled=True,
                current_flow=flow,
                last_interaction=datetime.now(timezone.utc)
            )
            self.db.add(state)
        
        self.db.commit()
    
    def get_current_flow(self, phone: str) -> Optional[str]:
        """Get current flow for user."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        return state.current_flow if state else None
    
    def update_last_interaction(self, phone: str):
        """Update last interaction timestamp."""
        from ...models import WhatsAppBotState
        
        state = self.db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == phone
        ).first()
        
        if state:
            state.last_interaction = datetime.now(timezone.utc)
            self.db.commit()
