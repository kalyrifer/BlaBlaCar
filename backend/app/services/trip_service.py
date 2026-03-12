"""Trip Service - бизнес-логика поездок"""
from uuid import UUID
from typing import Optional, List, Any
from pydantic import BaseModel

from app.repositories.interfaces import ITripRepository, IUserRepository
from app.domain.enums import (
    TripStatus as DomainTripStatus,
    is_valid_trip_status_transition,
)


class TripCreate(BaseModel):
    """Схема для создания поездки"""
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None


class TripSearchFilters(BaseModel):
    """Фильтры для поиска поездок"""
    from_city: str
    to_city: str
    date: Optional[str] = None


class TripResponse(BaseModel):
    """Схема ответа поездки"""
    id: str
    driver_id: str
    driver: Optional[dict] = None
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str
    created_at: str


class PaginatedTrips(BaseModel):
    """Пагинированный список поездок"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int


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
            "departure_date": trip_create.departure_date,
            "departure_time": trip_create.departure_time,
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
            departure_date=trip.departure_date,
            departure_time=trip.departure_time,
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
    ) -> PaginatedTrips:
        """Поиск поездок по фильтрам"""
        trips = await self._trip_repo.list_by_filters(
            filters.from_city,
            filters.to_city,
            filters.date,
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
                "departure_date": trip.departure_date,
                "departure_time": trip.departure_time,
                "available_seats": trip.available_seats,
                "price_per_seat": trip.price_per_seat,
                "status": trip.status
            })
        
        return PaginatedTrips(
            items=result,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    async def delete_or_cancel_trip(self, driver_id: UUID, trip_id: UUID) -> None:
        """Удаление или отмена поездки (только владелец)"""
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        if trip.driver_id != driver_id:
            raise ForbiddenError("Not the owner of this trip")
        
        await self._trip_repo.delete(trip_id)
    
    async def get_trip_by_id(self, trip_id: UUID) -> Optional[TripResponse]:
        """Получение поездки по ID"""
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            return None
        
        driver = await self._user_repo.get_by_id(trip.driver_id)
        
        return TripResponse(
            id=str(trip.id),
            driver_id=str(trip.driver_id),
            driver={
                "id": str(driver.id),
                "name": driver.name,
                "phone": driver.phone,
                "avatar_url": driver.avatar_url,
                "rating": driver.rating,
                "created_at": driver.created_at.isoformat()
            } if driver else None,
            from_city=trip.from_city,
            to_city=trip.to_city,
            departure_date=trip.departure_date,
            departure_time=trip.departure_time,
            available_seats=trip.available_seats,
            price_per_seat=trip.price_per_seat,
            description=trip.description,
            status=trip.status,
            created_at=trip.created_at.isoformat()
        )
    
    async def update_trip(
        self, 
        driver_id: UUID, 
        trip_id: UUID, 
        update_data: dict
    ) -> TripResponse:
        """Обновление поездки (только владелец)"""
        trip = await self._trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Trip not found")
        
        if trip.driver_id != driver_id:
            raise ForbiddenError("Not the owner of this trip")
        
        updated_trip = await self._trip_repo.update(trip_id, update_data)
        
        return TripResponse(
            id=str(updated_trip.id),
            driver_id=str(updated_trip.driver_id),
            from_city=updated_trip.from_city,
            to_city=updated_trip.to_city,
            departure_date=updated_trip.departure_date,
            departure_time=updated_trip.departure_time,
            available_seats=updated_trip.available_seats,
            price_per_seat=updated_trip.price_per_seat,
            description=updated_trip.description,
            status=updated_trip.status,
            created_at=updated_trip.created_at.isoformat()
        )
    
    async def list_my_trips_as_driver(self, driver_id: UUID) -> List[dict]:
        """Получение списка поездок пользователя как водителя"""
        from app.models.request import RequestStatus
        
        trips = await self._trip_repo.list_by_driver(driver_id)
        result = []
        
        # Need access to requests - we'll handle this in the router
        for trip in trips:
            result.append({
                "id": str(trip.id),
                "from_city": trip.from_city,
                "to_city": trip.to_city,
                "departure_date": trip.departure_date,
                "departure_time": trip.departure_time,
                "available_seats": trip.available_seats,
                "price_per_seat": trip.price_per_seat,
                "status": trip.status,
                "passengers_count": 0  # Will be filled by router with request count
            })
        
        return result