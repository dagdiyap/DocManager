"""Message handler for WhatsApp bot - Routes incoming messages."""

import re
from typing import Optional

import requests
from sqlalchemy.orm import Session

from .bot_state import BotStateManager
from .document_service import DocumentService
from .templates import (
    document_sending_message,
    document_sent_message,
    document_type_menu,
    error_message,
    goodbye_message,
    invalid_input_message,
    manual_mode_message,
    no_documents_found_message,
    unregistered_message,
    upload_confirmation,
    upload_prompt,
    welcome_message,
    year_menu,
)


class MessageHandler:
    """Routes incoming WhatsApp messages to appropriate handlers."""
    
    def __init__(self, db: Session, whatsapp_server_url: str = "http://localhost:3002"):
        self.db = db
        self.doc_service = DocumentService(db)
        self.bot_state = BotStateManager(db)
        self.whatsapp_url = whatsapp_server_url
        
        # Simple in-memory context for multi-step flows
        # Format: {phone: {'step': 'selecting_year', 'year': '2024-25', ...}}
        self.context = {}
    
    async def handle_message(self, phone: str, message: str):
        """Main message routing logic."""
        try:
            # Normalize phone number
            clean_phone = phone.replace('+91', '').replace('+', '')
            
            # Check if bot is enabled for this chat
            if not self.bot_state.is_bot_enabled(clean_phone):
                # CA is manually chatting, don't respond
                return
            
            # Check if client exists
            client = self.doc_service.get_client_by_phone(clean_phone)
            if not client:
                await self.send_message(clean_phone, unregistered_message())
                return
            
            # Update last interaction
            self.bot_state.update_last_interaction(clean_phone)
            
            # Get current context
            ctx = self.context.get(clean_phone, {})
            
            # Route based on message content and context
            message_lower = message.lower().strip()
            
            # Handle initial greetings
            if message_lower in ['hi', 'hello', 'start', 'hey']:
                await self.handle_welcome(clean_phone, client.name)
            
            # Handle main menu options
            elif message == '1' and not ctx:
                await self.handle_download_start(clean_phone)
            elif message == '2' and not ctx:
                await self.handle_upload_start(clean_phone)
            elif message == '3' and not ctx:
                await self.handle_manual_mode(clean_phone)
            
            # Handle download flow
            elif ctx.get('flow') == 'download':
                await self.handle_download_flow(clean_phone, message, ctx)
            
            # Handle upload flow
            elif ctx.get('flow') == 'upload':
                await self.handle_upload_flow(clean_phone, message, ctx)
            
            # Handle post-action menu
            elif message == '1' and ctx.get('step') == 'post_action':
                # Download more documents
                await self.handle_download_start(clean_phone)
            elif message == '2' and ctx.get('step') == 'post_action':
                # Back to main menu
                await self.handle_welcome(clean_phone, client.name)
            elif message == '3' and ctx.get('step') == 'post_action':
                # Exit
                await self.send_message(clean_phone, goodbye_message())
                self.context.pop(clean_phone, None)
            
            # Invalid input
            else:
                await self.send_message(clean_phone, invalid_input_message())
        
        except Exception as e:
            print(f"[Handler] Error handling message from {phone}: {e}")
            await self.send_message(clean_phone, error_message())
    
    async def handle_welcome(self, phone: str, client_name: str):
        """Send welcome message with main menu."""
        self.context[phone] = {}  # Clear context
        await self.send_message(phone, welcome_message(client_name))
    
    async def handle_download_start(self, phone: str):
        """Start document download flow."""
        # Get available years
        years = self.doc_service.get_available_years(phone)
        
        if not years:
            await self.send_message(phone, no_documents_found_message())
            return
        
        # Set context
        self.context[phone] = {
            'flow': 'download',
            'step': 'selecting_year',
            'years': years
        }
        
        # Send year menu
        await self.send_message(phone, year_menu(years))
    
    async def handle_download_flow(self, phone: str, message: str, ctx: dict):
        """Handle multi-step download flow."""
        step = ctx.get('step')
        
        if step == 'selecting_year':
            # User selected year
            try:
                choice = int(message)
                years = ctx['years']
                
                if 1 <= choice <= len(years):
                    selected_year = years[choice - 1]
                    
                    # Get document types for this year
                    doc_types = self.doc_service.get_document_types(phone, selected_year)
                    
                    if not doc_types:
                        await self.send_message(phone, no_documents_found_message(year=selected_year))
                        self.context.pop(phone, None)
                        return
                    
                    # Update context
                    ctx['step'] = 'selecting_type'
                    ctx['selected_year'] = selected_year
                    ctx['doc_types'] = doc_types
                    
                    # Send document type menu
                    await self.send_message(phone, document_type_menu(doc_types))
                else:
                    await self.send_message(phone, invalid_input_message())
            except ValueError:
                await self.send_message(phone, invalid_input_message())
        
        elif step == 'selecting_type':
            # User selected document type
            try:
                choice = int(message)
                doc_types = ctx['doc_types']
                selected_year = ctx['selected_year']
                
                # Check if "All Documents" option
                if choice == len(doc_types) + 1:
                    # Send all documents
                    file_paths = self.doc_service.get_all_documents_for_year(phone, selected_year)
                    
                    if not file_paths:
                        await self.send_message(phone, no_documents_found_message(year=selected_year))
                        self.context.pop(phone, None)
                        return
                    
                    await self.send_message(phone, document_sending_message("All Documents"))
                    
                    for file_path in file_paths:
                        await self.send_document(phone, file_path)
                    
                    await self.send_message(phone, document_sent_message())
                    
                    # Set post-action context
                    self.context[phone] = {'step': 'post_action'}
                
                elif 1 <= choice <= len(doc_types):
                    selected_type = doc_types[choice - 1]
                    
                    # Get document path
                    file_path = self.doc_service.get_document_path(phone, selected_year, selected_type)
                    
                    if not file_path:
                        await self.send_message(phone, no_documents_found_message(year=selected_year, doc_type=selected_type))
                        self.context.pop(phone, None)
                        return
                    
                    # Send document
                    await self.send_message(phone, document_sending_message(selected_type))
                    await self.send_document(phone, file_path)
                    await self.send_message(phone, document_sent_message())
                    
                    # Set post-action context
                    self.context[phone] = {'step': 'post_action'}
                else:
                    await self.send_message(phone, invalid_input_message())
            except ValueError:
                await self.send_message(phone, invalid_input_message())
    
    async def handle_upload_start(self, phone: str):
        """Start document upload flow."""
        self.context[phone] = {
            'flow': 'upload',
            'step': 'awaiting_files',
            'files': []
        }
        
        await self.send_message(phone, upload_prompt())
    
    async def handle_upload_flow(self, phone: str, message: str, ctx: dict):
        """Handle document upload flow."""
        if message.upper() == 'DONE':
            # User finished uploading
            uploaded_files = ctx.get('files', [])
            
            if uploaded_files:
                await self.send_message(
                    phone,
                    upload_confirmation(len(uploaded_files), uploaded_files)
                )
            
            # Clear context
            self.context.pop(phone, None)
        else:
            await self.send_message(phone, "Please send your documents or reply DONE when finished.")
    
    async def handle_manual_mode(self, phone: str):
        """Switch to manual CA chat mode."""
        self.bot_state.disable_bot(phone)
        self.context.pop(phone, None)
        await self.send_message(phone, manual_mode_message())
    
    async def handle_media_upload(self, phone: str, file_data: bytes, file_name: str, mime_type: str):
        """Handle uploaded media file."""
        ctx = self.context.get(phone, {})
        
        if ctx.get('flow') == 'upload':
            # Save file
            file_path = self.doc_service.save_uploaded_file(phone, file_data, file_name, mime_type)
            
            # Track uploaded file
            if 'files' not in ctx:
                ctx['files'] = []
            ctx['files'].append(file_name)
            
            print(f"[Handler] File uploaded: {file_path}")
    
    async def send_message(self, phone: str, text: str):
        """Send text message via WhatsApp server."""
        try:
            response = requests.post(
                f"{self.whatsapp_url}/send-message",
                json={"phone": phone, "message": text},
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            print(f"[Handler] Error sending message to {phone}: {e}")
            raise
    
    async def send_document(self, phone: str, file_path: str, caption: str = ""):
        """Send document via WhatsApp server."""
        try:
            response = requests.post(
                f"{self.whatsapp_url}/send-document",
                json={"phone": phone, "file_path": file_path, "caption": caption},
                timeout=30
            )
            response.raise_for_status()
        except Exception as e:
            print(f"[Handler] Error sending document to {phone}: {e}")
            raise
