"""Chat service - business logic for chat"""
from typing import TYPE_CHECKING
from uuid import UUID
from typing import List

from app.repositories.interfaces.chat_repo import ChatRepositoryInterface
from app.models.chat import Conversation, Message
from app.schemas.chat import ConversationListItem, MessageResponse

if TYPE_CHECKING:
    from app.repositories.interfaces.trip_repo import ITripRepository
    from app.repositories.interfaces.user_repo import IUserRepository
    from app.db.models.trip import Trip
    from app.db.models.user import User


class ChatService:
    """Service for managing conversations and messages"""
    
    def __init__(self, chat_repo: ChatRepositoryInterface):
        self.chat_repo = chat_repo
    
    async def get_or_create_conversation(
        self,
        trip_id: UUID,
        driver_id: UUID,
        passenger_id: UUID
    ) -> Conversation:
        """Get existing conversation or create new one"""
        existing = await self.chat_repo.get_conversation_by_trip_and_users(
            trip_id, driver_id, passenger_id
        )
        if existing:
            return existing
        
        return await self.chat_repo.create_conversation(
            trip_id, driver_id, passenger_id
        )
    
    async def get_user_conversations(
        self,
        user_id: UUID,
        trip_repo: "ITripRepository",
        user_repo: "IUserRepository"
    ) -> List[ConversationListItem]:
        """Get all conversations for a user with metadata"""
        conversations = await self.chat_repo.get_user_conversations(user_id)
        
        result = []
        for conv in conversations:
            # Determine the other user
            other_user_id = conv.passenger_id if conv.driver_id == user_id else conv.driver_id
            other_user = await user_repo.get_by_id(other_user_id)
            
            # Get trip info
            trip = await trip_repo.get_by_id(conv.trip_id)
            
            # Get last message and unread count
            messages = await self.chat_repo.get_messages(conv.id, skip=0, limit=1)
            last_message = messages[0] if messages else None
            unread_count = await self.chat_repo.get_unread_count(conv.id, user_id)
            
            result.append(ConversationListItem(
                id=conv.id,
                trip_id=conv.trip_id,
                other_user_id=other_user_id,
                other_user_name=other_user.name if other_user else "Unknown",
                trip_from_city=trip.from_city if trip else "",
                trip_to_city=trip.to_city if trip else "",
                last_message=last_message.content if last_message else None,
                last_message_time=last_message.created_at if last_message else None,
                unread_count=unread_count
            ))
        
        # Sort by last message time
        result.sort(key=lambda x: x.last_message_time or x.created_at, reverse=True)
        return result
    
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[MessageResponse]:
        """Get messages in a conversation"""
        messages = await self.chat_repo.get_messages(conversation_id, skip, limit)
        
        # Mark messages as read
        await self.chat_repo.mark_messages_as_read(conversation_id, user_id)
        
        return [
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_id=m.sender_id,
                content=m.content,
                is_read=m.is_read,
                created_at=m.created_at
            )
            for m in messages
        ]
    
    async def send_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str
    ) -> MessageResponse:
        """Send a message in a conversation"""
        message = await self.chat_repo.create_message(
            conversation_id, sender_id, content
        )
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at
        )
