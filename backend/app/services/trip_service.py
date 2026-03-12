"""Trip Service - бизнес-логика поездок"""
from uuid import UUID
from typing import Optional, List, Any
from pydantic import BaseModel

from app.repositories.interfaces import ITripRepository, IUserRepository
from app.domain.enums import (
    TripStatus as DomainTripStatus,
    is_valid_trip_status_transition,
)
from app.schemas.trip import (
    TripCreate,
    TripSearchFilters,
    TripResponse,
    PaginatedTripsResponse,
)


class TripNotFoundError(Exception):
    """Поездка не найдена"""
    pass


class ForbiddenError(Exception):
    """Доступ запрещен"""
    pass




class TripService:
    """Сервис для работы с поездками"""
    
    def __init__(self, trip_repo: ITripRepository, user_repo: IUserRepository):
        self._trip_repo = trip_repo
        self._user_repo = user_repo
    
    def is_valid_transition(self, old_status: str, new_status: str) -> bool:
        """Проверка допустимости перехода статуса поездки
        
        Args:
            old_status: Текущий статус поездки
            new_status: Новый статус поездки
            
        Returns:
            True если переход допустим, иначе False
        """
        try:
            old = DomainTripStatus(old_status)
            new = DomainTripStatus(new_status)
            return is_valid_trip_status_transition(old, new)
        except ValueError:
            # Если передан неверный статус
            return False
    
    async def create_trip(self, driver_id: UUID, trip_create: TripCreate) -> TripResponse:
        """Создание новой поездки"""
        trip = await self._trip_repo.create({
            "driver_id": driver_id,
            "from_city": trip_create.from_city,
            "to_city": trip_create.to_city,
            "departure_at": trip_create.departure_at,
            "available_seats": trip_create.available_seats,
            "price_per_seat": trip_create.price_per_seat,
            "description": trip_create.description,
            "status": "active"
        })
        
        return TripResponse(
            id=str(trip.id),
            driver_id=str(trip.driver_id),
            from_city=trip.from_city,
            to_city=trip.to_city,
            departure_at=trip.departure_at.isoformat(),
            available_seats=trip.available_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            status=trip.status,
            created_at=trip.created_at.isoformat()
        )
    
    async def search_trips(
        self, 
        filters: TripSearchFilters, 
        page: int, 
        page_size: int
    ) -> PaginatedTripsResponse:
        """Поиск поездок по фильтрам"""
        trips = await self._trip_repo.search(
            filters.from_city,
            filters.to_city,
            filters.date_from,
            filters.date_to,
            "active"
        )
        
        # Пагинация
        total = len(trips)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_trips = trips[start:end]
        
        # Получение информации о водителях
        result = []
        for trip in paginated_trips:
            driver = await self._user_repo.get_by_id(trip.driver_id)
            result.append({
                "id": str(trip.id),
                "driver_id": str(trip.driver_id),
                "driver": {
                    "id": str(driver.id),
                    "name": driver.name,
                    "avatar_url": driver.avatar_url,
                    "rating": driver.rating
                } if driver else None,
                "from_city": trip.from_city,
                "to_city": trip.to_city,
                "departure_at": trip.departure_at.isoformat() if trip.departure_at else None,
                "available_seats": trip.available_seats,
                "price_per_seat": trip.price_per_seat,
                "status": trip.status
            })
        
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return PaginatedTripsResponse(
            items=result,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
    
    async def delete_or_cancel_trip(
        self, 
        driver_id: UUID, 
        trip_id: UUID
    ) -> None:
        """Удаление/отмена поездки (только водитель)"""
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        if trip.driver_id != driver_id:
            raise ForbiddenError("Not authorized to delete this trip")
        
        await self._trip_repo.delete(trip_id)
