"""Message handler for WhatsApp bot - Routes incoming messages."""

import logging
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


logger = logging.getLogger(__name__)


class MessageHandler:
    """Routes incoming WhatsApp messages to appropriate handlers."""
    
    def __init__(self, db: Session, whatsapp_server_url: str = "http://localhost:3002"):
        self.db = db
        self.doc_service = DocumentService(db)
        self.bot_state = BotStateManager(db)
        self.whatsapp_url = whatsapp_server_url
        
        self.context = {}
        
        logger.info("MessageHandler initialized")
    
    def _format_outbound_phone(self, phone: str) -> str:
        """Format 10-digit phone to WhatsApp format with country code."""
        clean = re.sub(r'[^0-9]', '', phone)
        if len(clean) == 10:
            return f"91{clean}"
        return clean
    
    def _validate_and_normalize_phone(self, phone: str) -> Optional[str]:
        """Validate and normalize phone number."""
        if not phone or not isinstance(phone, str):
            logger.warning(f"Invalid phone number type: {type(phone)}")
            return None
        
        clean = re.sub(r'[^0-9]', '', phone)
        
        if clean.startswith('91'):
            clean = clean[2:]
        
        if len(clean) != 10 or not clean.isdigit():
            logger.warning(f"Invalid phone number format: {phone} -> {clean}")
            return None
        
        return clean
    
    async def handle_message(self, phone: str, message: str):
        """Main message routing logic."""
        clean_phone = None
        try:
            if not message or not isinstance(message, str):
                logger.error(f"Invalid message from {phone}: {type(message)}")
                return
            
            clean_phone = self._validate_and_normalize_phone(phone)
            if not clean_phone:
                logger.error(f"Invalid phone number: {phone}")
                return
            
            logger.info(f"Processing message from {clean_phone}: {message[:50]}")
            
            if not self.bot_state.is_bot_enabled(clean_phone):
                logger.info(f"Bot disabled for {clean_phone}, skipping")
                return
            
            client = self.doc_service.get_client_by_phone(clean_phone)
            if not client:
                logger.warning(f"Unregistered client: {clean_phone}")
                await self.send_message(clean_phone, unregistered_message())
                return
            
            if not client.is_active:
                logger.warning(f"Inactive client: {clean_phone}")
                await self.send_message(clean_phone, "Your account is inactive. Please contact CA.")
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
            
            else:
                logger.warning(f"Invalid input from {clean_phone}: {message}")
                await self.send_message(clean_phone, invalid_input_message())
        
        except Exception as e:
            logger.error(f"Error handling message from {phone}: {e}", exc_info=True)
            if clean_phone:
                try:
                    await self.send_message(clean_phone, error_message())
                except:
                    logger.error(f"Failed to send error message to {clean_phone}")
    
    async def handle_welcome(self, phone: str, client_name: str):
        """Send welcome message with main menu."""
        self.context[phone] = {}  # Clear context
        await self.send_message(phone, welcome_message(client_name))
    
    async def handle_download_start(self, phone: str):
        """Start document download flow."""
        try:
            years = self.doc_service.get_available_years(phone)
            
            if not years:
                logger.info(f"No documents found for {phone}")
                await self.send_message(phone, no_documents_found_message())
                self.context.pop(phone, None)
                return
            
            logger.info(f"Starting download flow for {phone}, {len(years)} years available")
            
            self.context[phone] = {
                'flow': 'download',
                'step': 'selecting_year',
                'years': years
            }
            
            await self.send_message(phone, year_menu(years))
        except Exception as e:
            logger.error(f"Error in download_start for {phone}: {e}", exc_info=True)
            await self.send_message(phone, error_message())
            self.context.pop(phone, None)
    
    async def handle_download_flow(self, phone: str, message: str, ctx: dict):
        """Handle multi-step download flow."""
        step = ctx.get('step')
        
        if step == 'selecting_year':
            try:
                choice = int(message.strip())
                years = ctx.get('years', [])
                
                if not years:
                    logger.error(f"No years in context for {phone}")
                    await self.send_message(phone, error_message())
                    self.context.pop(phone, None)
                    return
                
                if 1 <= choice <= len(years):
                    selected_year = years[choice - 1]
                    logger.info(f"{phone} selected year: {selected_year}")
                    
                    doc_types = self.doc_service.get_document_types(phone, selected_year)
                    
                    if not doc_types:
                        logger.info(f"No documents for {phone} in {selected_year}")
                        await self.send_message(phone, no_documents_found_message(year=selected_year))
                        self.context.pop(phone, None)
                        return
                    
                    ctx['step'] = 'selecting_type'
                    ctx['selected_year'] = selected_year
                    ctx['doc_types'] = doc_types
                    
                    await self.send_message(phone, document_type_menu(doc_types))
                else:
                    logger.warning(f"Invalid year choice from {phone}: {choice}")
                    await self.send_message(phone, invalid_input_message())
            except ValueError:
                logger.warning(f"Non-numeric input from {phone}: {message}")
                await self.send_message(phone, invalid_input_message())
            except Exception as e:
                logger.error(f"Error in year selection for {phone}: {e}", exc_info=True)
                await self.send_message(phone, error_message())
                self.context.pop(phone, None)
        
        elif step == 'selecting_type':
            try:
                choice = int(message.strip())
                doc_types = ctx.get('doc_types', [])
                selected_year = ctx.get('selected_year')
                
                if not doc_types or not selected_year:
                    logger.error(f"Missing context data for {phone}")
                    await self.send_message(phone, error_message())
                    self.context.pop(phone, None)
                    return
                
                if choice == len(doc_types) + 1:
                    logger.info(f"{phone} requested all documents for {selected_year}")
                    file_paths = self.doc_service.get_all_documents_for_year(phone, selected_year)
                    
                    if not file_paths:
                        logger.warning(f"No files found for {phone} in {selected_year}")
                        await self.send_message(phone, no_documents_found_message(year=selected_year))
                        self.context.pop(phone, None)
                        return
                    
                    await self.send_message(phone, document_sending_message("All Documents"))
                    
                    sent_count = 0
                    for file_path in file_paths:
                        try:
                            await self.send_document(phone, file_path)
                            sent_count += 1
                        except Exception as e:
                            logger.error(f"Failed to send {file_path} to {phone}: {e}")
                    
                    if sent_count > 0:
                        await self.send_message(phone, document_sent_message())
                        logger.info(f"Sent {sent_count}/{len(file_paths)} documents to {phone}")
                    else:
                        await self.send_message(phone, "Failed to send documents. Please try again.")
                    
                    self.context[phone] = {'step': 'post_action'}
                
                elif 1 <= choice <= len(doc_types):
                    selected_type = doc_types[choice - 1]
                    logger.info(f"{phone} selected document type: {selected_type}")
                    
                    file_path = self.doc_service.get_document_path(phone, selected_year, selected_type)
                    
                    if not file_path:
                        logger.warning(f"Document not found: {phone}, {selected_year}, {selected_type}")
                        await self.send_message(phone, no_documents_found_message(year=selected_year, doc_type=selected_type))
                        self.context.pop(phone, None)
                        return
                    
                    await self.send_message(phone, document_sending_message(selected_type))
                    try:
                        await self.send_document(phone, file_path)
                        await self.send_message(phone, document_sent_message())
                        logger.info(f"Sent {selected_type} to {phone}")
                    except Exception as e:
                        logger.error(f"Failed to send document to {phone}: {e}")
                        await self.send_message(phone, "Failed to send document. Please try again.")
                    
                    self.context[phone] = {'step': 'post_action'}
                else:
                    logger.warning(f"Invalid document type choice from {phone}: {choice}")
                    await self.send_message(phone, invalid_input_message())
            except ValueError:
                logger.warning(f"Non-numeric input from {phone}: {message}")
                await self.send_message(phone, invalid_input_message())
            except Exception as e:
                logger.error(f"Error in document selection for {phone}: {e}", exc_info=True)
                await self.send_message(phone, error_message())
                self.context.pop(phone, None)
    
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
        try:
            clean_phone = self._validate_and_normalize_phone(phone)
            if not clean_phone:
                logger.error(f"Invalid phone for upload: {phone}")
                return
            
            if not file_data or len(file_data) == 0:
                logger.error(f"Empty file data from {clean_phone}")
                return
            
            if len(file_data) > 100 * 1024 * 1024:
                logger.warning(f"File too large from {clean_phone}: {len(file_data)} bytes")
                await self.send_message(clean_phone, "File too large. Maximum 100MB.")
                return
            
            ctx = self.context.get(clean_phone, {})
            
            if ctx.get('flow') == 'upload':
                file_path = self.doc_service.save_uploaded_file(clean_phone, file_data, file_name, mime_type)
                
                if 'files' not in ctx:
                    ctx['files'] = []
                ctx['files'].append(file_name)
                
                logger.info(f"File uploaded from {clean_phone}: {file_name} ({len(file_data)} bytes)")
            else:
                logger.warning(f"File received from {clean_phone} but not in upload flow")
        except Exception as e:
            logger.error(f"Error handling media upload from {phone}: {e}", exc_info=True)
    
    async def send_message(self, phone: str, text: str):
        """Send text message via WhatsApp server."""
        if not text or not isinstance(text, str):
            logger.error(f"Invalid message text: {type(text)}")
            return
        
        try:
            response = requests.post(
                f"{self.whatsapp_url}/send-message",
                json={"phone": self._format_outbound_phone(phone), "message": text},
                timeout=10
            )
            response.raise_for_status()
            logger.debug(f"Message sent to {phone}")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending message to {phone}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error sending message to {phone}")
            raise
        except Exception as e:
            logger.error(f"Error sending message to {phone}: {e}")
            raise
    
    async def send_document(self, phone: str, file_path: str, caption: str = ""):
        """Send document via WhatsApp server."""
        import os
        
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Invalid or missing file: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:
            logger.error(f"File too large: {file_path} ({file_size} bytes)")
            raise ValueError(f"File too large: {file_size} bytes")
        
        try:
            response = requests.post(
                f"{self.whatsapp_url}/send-document",
                json={"phone": self._format_outbound_phone(phone), "file_path": file_path, "caption": caption},
                timeout=30
            )
            response.raise_for_status()
            logger.debug(f"Document sent to {phone}: {file_path}")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending document to {phone}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error sending document to {phone}")
            raise
        except Exception as e:
            logger.error(f"Error sending document to {phone}: {e}")
            raise
