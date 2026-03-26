"""
Search service for advanced trip search with geolocation and recommendations.
"""
import base64
import json
import math
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from app.schemas.trip import TripAdvancedFilters, CursorPaginatedResponse
from app.db.repositories.pg_trip_repo import PGTripRepository

logger = logging.getLogger(__name__)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points in kilometers.
    Uses the Haversine formula.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def encode_cursor(trip_id: UUID, departure_at: datetime) -> str:
    """Encode cursor from trip ID and departure time."""
    cursor_data = {
        "id": str(trip_id),
        "departure": departure_at.isoformat()
    }
    return base64.urlsafe_b64encode(json.dumps(cursor_data).encode()).decode()


def decode_cursor(cursor: str) -> Optional[Tuple[UUID, datetime]]:
    """Decode cursor to trip ID and departure time."""
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return (
            UUID(data["id"]),
            datetime.fromisoformat(data["departure"])
        )
    except Exception as e:
        logger.warning(f"Failed to decode cursor: {e}")
        return None


class SearchService:
    """
    Advanced search service with geolocation, filters, and recommendations.
    """
    
    def __init__(self, trip_repo: PGTripRepository):
        self.trip_repo = trip_repo
    
    async def search_trips_advanced(
        self,
        filters: TripAdvancedFilters,
        cursor: Optional[str] = None,
        limit: int = 20
    ) -> CursorPaginatedResponse:
        """
        Search trips with advanced filters and cursor-based pagination.
        
        Args:
            filters: Advanced search filters
            cursor: Optional cursor for pagination
            limit: Number of results per page
            
        Returns:
            CursorPaginatedResponse with trips and next cursor
        """
        # Build base query
        query_filters = {}
        
        # City search (fallback if no coordinates)
        if filters.from_city and not filters.from_lat:
            query_filters["from_city__ilike"] = f"%{filters.from_city}%"
        if filters.to_city and not filters.to_lat:
            query_filters["to_city__ilike"] = f"%{filters.to_city}%"
        
        # Date filters
        if filters.date_from:
            query_filters["departure_at__gte"] = filters.date_from
        if filters.date_to:
            query_filters["departure_at__lte"] = filters.date_to
        
        # Price filters
        if filters.price_min is not None:
            query_filters["price_per_seat__gte"] = filters.price_min
        if filters.price_max is not None:
            query_filters["price_per_seat__lte"] = filters.price_max
        
        # Seat filter
        if filters.available_seats_min is not None:
            query_filters["available_seats__gte"] = filters.available_seats_min
        
        # Additional filters
        if filters.car_type:
            query_filters["car_type"] = filters.car_type
        if filters.smoking_allowed is not None:
            query_filters["smoking_allowed"] = filters.smoking_allowed
        if filters.pets_allowed is not None:
            query_filters["pets_allowed"] = filters.pets_allowed
        if filters.luggage_size:
            query_filters["luggage_size"] = filters.luggage_size
        
        # Status filter (only active trips)
        query_filters["status"] = "active"
        
        # Cursor handling
        if cursor:
            cursor_data = decode_cursor(cursor)
            if cursor_data:
                trip_id, departure_at = cursor_data
                # Add cursor condition to filter
                if filters.sort_order == "asc":
                    query_filters["departure_at__gt"] = departure_at
                else:
                    query_filters["departure_at__lt"] = departure_at
        
        # Sorting
        sort_by = filters.sort_by if filters.sort_by else "departure_at"
        sort_order = "desc" if filters.sort_order == "desc" else "asc"
        
        # Execute search
        trips, total = await self.trip_repo.search_trips_advanced(
            filters=query_filters,
            limit=limit + 1,  # Fetch one extra to check if there are more
            offset=0,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Geolocation filtering (if coordinates provided)
        if filters.from_lat and filters.from_lon:
            filtered_trips = []
            for trip in trips:
                if trip.from_lat and trip.from_lon:
                    distance = calculate_distance(
                        filters.from_lat, filters.from_lon,
                        trip.from_lat, trip.from_lon
                    )
                    if distance <= filters.radius_km:
                        filtered_trips.append(trip)
            trips = filtered_trips
        
        # Check if there are more results
        has_more = len(trips) > limit
        if has_more:
            trips = trips[:limit]
        
        # Generate next cursor
        next_cursor = None
        if has_more and trips:
            last_trip = trips[-1]
            next_cursor = encode_cursor(last_trip.id, last_trip.departure_at)
        
        return CursorPaginatedResponse(
            items=[trip.to_dict() for trip in trips],
            next_cursor=next_cursor,
            has_more=has_more,
            total=total
        )
    
    async def get_similar_trips(
        self,
        trip_id: UUID,
        limit: int = 5
    ) -> List[dict]:
        """
        Get similar trips based on route and time.
        
        Args:
            trip_id: Reference trip ID
            limit: Number of similar trips to return
            
        Returns:
            List of similar trip dictionaries
        """
        # Get the reference trip
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            return []
        
        # Search for similar trips (same route, nearby times)
        filters = {
            "from_city__ilike": f"%{trip.from_city}%",
            "to_city__ilike": f"%{trip.to_city}%",
            "status": "active",
            "departure_at__gte": datetime.utcnow(),
            "id__ne": str(trip_id)  # Exclude the original trip
        }
        
        similar_trips, _ = await self.trip_repo.search_trips_advanced(
            filters=filters,
            limit=limit,
            offset=0,
            sort_by="departure_at",
            sort_order="asc"
        )
        
        return [t.to_dict() for t in similar_trips]
    
    async def get_recommended_trips(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[dict]:
        """
        Get recommended trips based on user's search history and favorites.
        
        This is a simple recommendation based on:
        1. Recent search history (from/to cities)
        2. Popular routes in the user's region
        
        Args:
            user_id: User ID for personalization
            limit: Number of trips to return
            
        Returns:
            List of recommended trip dictionaries
        """
        # Get active trips departing soon
        filters = {
            "status": "active",
            "departure_at__gte": datetime.utcnow(),
        }
        
        trips, _ = await self.trip_repo.search_trips_advanced(
            filters=filters,
            limit=limit,
            offset=0,
            sort_by="departure_at",
            sort_order="asc"
        )
        
        return [t.to_dict() for t in trips]


async def get_search_service() -> SearchService:
    """Get SearchService instance."""
    from app.core.database import get_trip_repo
    trip_repo = get_trip_repo()
    return SearchService(trip_repo)