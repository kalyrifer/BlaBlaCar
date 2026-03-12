"""Request Service - бизнес-логика заявок"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.repositories.interfaces import (
    IRequestRepository, 
    ITripRepository, 
    INotificationRepository,
    IUserRepository
)
from app.models.request import RequestStatus


class RequestCreate(BaseModel):
    """Схема для создания заявки"""
    trip_id: UUID
    seats_requested: int = 1
    message: Optional[str] = None


class RequestStatusUpdate(BaseModel):
    """Схема для обновления статуса заявки"""
    status: str


class TripRequestResponse(BaseModel):
    """Схема ответа заявки"""
    id: str
    trip_id: str
    passenger_id: str
    passenger: Optional[dict] = None
    seats_requested: int
    message: Optional[str] = None
    status: str
    created_at: str
    updated_at: Optional[str] = None


class RequestNotFoundError(Exception):
    """Заявка не найдена"""
    pass


class TripNotFoundError(Exception):
    """Поездка не найдена"""
    pass


class ForbiddenError(Exception):
    """Доступ запрещен"""
    pass


class NotEnoughSeatsError(Exception):
    """Недостаточно мест"""
    pass


class RequestAlreadyExistsError(Exception):
    """Заявка уже существует"""
    pass


class RequestService:
    """Сервис для работы с заявками"""
    
    def __init__(
        self, 
        request_repo: IRequestRepository,
        trip_repo: ITripRepository,
        notification_repo: INotificationRepository,
        user_repo: IUserRepository
    ):
        self._request_repo = request_repo
        self._trip_repo = trip_repo
        self._notification_repo = notification_repo
        self._user_repo = user_repo
    
    async def create_request(
        self, 
        passenger_id: UUID, 
        trip_id: UUID, 
        seats: int, 
        message: Optional[str] = None
    ) -> TripRequestResponse:
        """Создание новой заявки на поездку"""
        # Проверка существования поездки
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        # Нельзя отправлять заявку на свою поездку
        if trip.driver_id == passenger_id:
            raise ValueError("Cannot request your own trip")
        
        # Проверка, что заявка уже не отправлена
        exists = await self._request_repo.exists(trip_id, passenger_id)
        if exists:
            raise RequestAlreadyExistsError("Request already sent")
        
        # Проверка доступности мест
        if trip.available_seats < seats:
            raise NotEnoughSeatsError("Not enough available seats")
        
        # Создание заявки
        request = await self._request_repo.create({
            "trip_id": trip_id,
            "passenger_id": passenger_id,
            "seats_requested": seats,
            "message": message,
            "status": RequestStatus.PENDING
        })
        
        # Получение информации о пассажире
        passenger = await self._user_repo.get_by_id(passenger_id)
        
        # Создание уведомления для водителя
        await self._notification_repo.create({
            "user_id": trip.driver_id,
            "type": "request_received",
            "title": "Новая заявка",
            "message": f"Пользователь {passenger.name} отправил заявку на вашу поездку" if passenger else "Новая заявка на вашу поездку",
            "related_trip_id": trip_id,
            "related_request_id": request.id
        })
        
        return TripRequestResponse(
            id=str(request.id),
            trip_id=str(request.trip_id),
            passenger_id=str(request.passenger_id),
            passenger={
                "id": str(passenger.id),
                "name": passenger.name,
                "avatar_url": passenger.avatar_url,
                "rating": passenger.rating,
                "phone": passenger.phone
            } if passenger else None,
            seats_requested=request.seats_requested,
            message=request.message,
            status=request.status,
            created_at=request.created_at.isoformat(),
            updated_at=request.updated_at.isoformat() if request.updated_at else None
        )
    
    async def update_request_status(
        self, 
        driver_id: UUID, 
        request_id: UUID, 
        new_status: str
    ) -> TripRequestResponse:
        """Обновление статуса заявки (только водитель)"""
        # Получение заявки
        request = await self._request_repo.get_by_id(request_id)
        if not request:
            raise RequestNotFoundError("Request not found")
        
        # Получение поездки
        trip = await self._trip_repo.get_by_id(request.trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        # Проверка прав (только водитель может обновлять статус)
        if trip.driver_id != driver_id:
            raise ForbiddenError("Not authorized to update this request")
        
        # При подтверждении проверяем доступность мест
        if new_status == RequestStatus.CONFIRMED:
            if trip.available_seats < request.seats_requested:
                raise NotEnoughSeatsError("Not enough available seats")
        
        # Обновление статуса заявки
        updated_request = await self._request_repo.update_status(request_id, new_status)
        
        # Создание уведомления для пассажира
        if new_status == RequestStatus.CONFIRMED:
            notification_type = "request_confirmed"
            notification_title = "Заявка подтверждена"
            notification_message = "Водитель подтвердил вашу заявку на поездку"
        else:
            notification_type = "request_rejected"
            notification_title = "Заявка отклонена"
            notification_message = "Водитель отклонил вашу заявку на поездку"
        
        await self._notification_repo.create({
            "user_id": request.passenger_id,
            "type": notification_type,
            "title": notification_title,
            "message": notification_message,
            "related_trip_id": request.trip_id,
            "related_request_id": request.id
        })
        
        # Уменьшение доступных мест при подтверждении
        if new_status == RequestStatus.CONFIRMED:
            await self._trip_repo.update_seats(request.trip_id, -request.seats_requested)
        
        # Получение информации о пассажире
        passenger = await self._user_repo.get_by_id(request.passenger_id)
        
        return TripRequestResponse(
            id=str(updated_request.id),
            trip_id=str(updated_request.trip_id),
            passenger_id=str(updated_request.passenger_id),
            passenger={
                "id": str(passenger.id),
                "name": passenger.name,
                "avatar_url": passenger.avatar_url,
                "rating": passenger.rating,
                "phone": passenger.phone
            } if passenger else None,
            seats_requested=updated_request.seats_requested,
            message=updated_request.message,
            status=updated_request.status,
            created_at=updated_request.created_at.isoformat(),
            updated_at=updated_request.updated_at.isoformat() if updated_request.updated_at else None
        )
    
    async def get_requests_by_trip(self, trip_id: UUID, driver_id: UUID) -> list:
        """Получение всех заявок для поездки (только водитель)"""
        # Проверка прав
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        if trip.driver_id != driver_id:
            raise ForbiddenError("Not the owner of this trip")
        
        requests = await self._request_repo.get_by_trip(trip_id)
        result = []
        
        for req in requests:
            passenger = await self._user_repo.get_by_id(req.passenger_id)
            result.append({
                "id": str(req.id),
                "passenger_id": str(req.passenger_id),
                "passenger": {
                    "id": str(passenger.id),
                    "name": passenger.name,
                    "avatar_url": passenger.avatar_url,
                    "rating": passenger.rating,
                    "phone": passenger.phone
                } if passenger else None,
                "seats_requested": req.seats_requested,
                "message": req.message,
                "status": req.status,
                "created_at": req.created_at.isoformat()
            })
        
        return result
    
    async def get_my_requests(self, passenger_id: UUID, status_filter: Optional[str] = None) -> list:
        """Получение моих заявок как пассажира"""
        requests = await self._request_repo.get_by_passenger(passenger_id)
        
        # Фильтрация по статусу
        if status_filter:
            requests = [r for r in requests if r.status == status_filter]
        
        result = []
        for req in requests:
            trip = await self._trip_repo.get_by_id(req.trip_id)
            driver = await self._user_repo.get_by_id(trip.driver_id) if trip else None
            
            result.append({
                "id": str(req.id),
                "trip_id": str(req.trip_id),
                "trip": {
                    "id": str(trip.id),
                    "from_city": trip.from_city,
                    "to_city": trip.to_city,
                    "departure_date": trip.departure_date,
                    "departure_time": trip.departure_time,
                    "driver_name": driver.name if driver else None
                } if trip else None,
                "seats_requested": req.seats_requested,
                "status": req.status,
                "created_at": req.created_at.isoformat()
            })
        
        return result