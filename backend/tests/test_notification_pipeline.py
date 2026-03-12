"""Integration tests for the notification pipeline with background worker"""
import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timedelta

from app.background.worker import get_notification_queue
from app.background.adapters import InProcessAdapter
from app.repositories.inmemory import InMemoryNotificationRepository


@pytest.fixture
def notification_repo():
    """Create a fresh notification repository for each test"""
    return InMemoryNotificationRepository()


class TestNotificationQueue:
    """Test the notification queue functionality"""
    
    def test_get_notification_queue_returns_queue(self):
        """Test that get_notification_queue returns a queue"""
        queue = get_notification_queue()
        assert queue is not None
        assert isinstance(queue, asyncio.Queue)


class TestInProcessAdapter:
    """Test the in-process notification adapter"""
    
    @pytest.mark.asyncio
    async def test_adapter_sends_and_saves_notification(self, notification_repo):
        """Test adapter sends and saves notification"""
        adapter = InProcessAdapter(notification_repo)
        await adapter.initialize()
        
        user_id = uuid4()
        result = await adapter.send_notification(
            user_id=user_id,
            title="Test Notification",
            message="Test message content",
            notification_type="test"
        )
        
        assert result is True
        
        # Check notification was saved
        notifications = await notification_repo.get_by_user(user_id)
        assert len(notifications) == 1
        assert notifications[0].title == "Test Notification"
        assert notifications[0].message == "Test message content"
        
        await adapter.shutdown()
    
    @pytest.mark.asyncio
    async def test_adapter_handles_multiple_notifications(self, notification_repo):
        """Test adapter handles multiple notifications for same user"""
        adapter = InProcessAdapter(notification_repo)
        await adapter.initialize()
        
        user_id = uuid4()
        
        # Send multiple notifications
        for i in range(3):
            await adapter.send_notification(
                user_id=user_id,
                title=f"Notification {i}",
                message=f"Message {i}",
                notification_type="test"
            )
        
        # Check all notifications were saved
        notifications = await notification_repo.get_by_user(user_id)
        assert len(notifications) == 3
        
        await adapter.shutdown()
    
    @pytest.mark.asyncio
    async def test_adapter_initialization(self, notification_repo):
        """Test adapter can be initialized and shutdown"""
        adapter = InProcessAdapter(notification_repo)
        
        await adapter.initialize()
        # After initialize, the adapter should be ready to use
        # We verify this by successfully sending a notification
        user_id = uuid4()
        result = await adapter.send_notification(
            user_id=user_id,
            title="Test",
            message="Test",
            notification_type="test"
        )
        assert result is True
        
        await adapter.shutdown()
        # After shutdown, verify we can't send notifications
        # (implementation specific - may just return False or raise)


class TestNotificationIntegration:
    """Integration tests for notification flow"""
    
    @pytest.mark.asyncio
    async def test_notification_flow_create_to_driver(self):
        """Test the full notification flow - creating request notifies driver"""
        # Create repos
        notification_repo = InMemoryNotificationRepository()
        adapter = InProcessAdapter(notification_repo)
        await adapter.initialize()
        
        user_id = uuid4()
        
        # Simulate notification that would be sent when a passenger creates a request
        await adapter.send_notification(
            user_id=user_id,
            title="Новая заявка на поездку",
            message="Пассажир подал заявку на вашу поездку",
            notification_type="new_request",
            metadata={"trip_id": str(uuid4()), "passenger_id": str(uuid4())}
        )
        
        # Verify notification was saved
        notifications = await notification_repo.get_by_user(user_id)
        assert len(notifications) == 1
        assert "заявка" in notifications[0].title.lower()
        
        await adapter.shutdown()
    
    @pytest.mark.asyncio
    async def test_notification_flow_status_update(self):
        """Test the full notification flow - status update notifies passenger"""
        # Create repos
        notification_repo = InMemoryNotificationRepository()
        adapter = InProcessAdapter(notification_repo)
        await adapter.initialize()
        
        user_id = uuid4()
        
        # Simulate notification that would be sent when driver accepts request
        await adapter.send_notification(
            user_id=user_id,
            title="Request Accepted",
            message="Your request was accepted by the driver",
            notification_type="request_accepted",
            metadata={"trip_id": str(uuid4()), "seats": 2}
        )
        
        # Verify notification was saved
        notifications = await notification_repo.get_by_user(user_id)
        assert len(notifications) == 1
        assert "accepted" in notifications[0].message.lower()
        
        await adapter.shutdown()
    
    @pytest.mark.asyncio
    async def test_notification_types(self, notification_repo):
        """Test different notification types"""
        adapter = InProcessAdapter(notification_repo)
        await adapter.initialize()
        
        user_id = uuid4()
        
        notification_types = [
            ("new_request", "Новая заявка"),
            ("request_accepted", "Заявка подтверждена"),
            ("request_rejected", "Заявка отклонена"),
            ("trip_cancelled", "Поездка отменена"),
        ]
        
        for notif_type, title in notification_types:
            await adapter.send_notification(
                user_id=user_id,
                title=title,
                message=f"Test message for {notif_type}",
                notification_type=notif_type
            )
        
        # Check all notifications were saved
        notifications = await notification_repo.get_by_user(user_id)
        assert len(notifications) == len(notification_types)
        
        await adapter.shutdown()
