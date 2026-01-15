# Uber System Design

## 1. Requirements

### Functional Requirements
- **Riders**: Request rides, track driver location
- **Drivers**: Accept/reject rides, navigate to pickup
- **Real-time matching**: Connect nearby drivers with riders
- **Live tracking**: Location updates during trip
- **Dynamic pricing**: Surge pricing based on demand

### Non-Functional Requirements
- **Scale**: 15M daily rides, 1M active drivers
- **Latency**: < 1 second for matching, < 100ms for location updates
- **Availability**: 99.99% uptime

## 2. High-Level Architecture

```
┌─────────────┐    ┌─────────────┐
│   Rider     │    │   Driver    │
│    App      │    │    App      │
└─────────────┘    └─────────────┘
       │                   │
       └───────────────────┼───────────────────┐
                           │                   │
                    ┌─────────────┐            │
                    │ API Gateway │            │
                    └─────────────┘            │
                           │                   │
        ┌──────────────────┼──────────────────┐│
        │                  │                  ││
        ▼                  ▼                  ▼▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Location   │    │  Matching   │    │    Trip     │
│  Service    │    │  Service    │    │  Service    │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌─────────────┐
                    │   Redis     │
                    │ (Location)  │
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │ PostgreSQL  │
                    │ (Trips/Users)│
                    └─────────────┘
```

## 3. Core Uber-Specific APIs

### Location Service APIs

#### Driver Location Updates
```java
// Real-time location streaming (WebSocket)
WS /location/stream
{
    "driver_id": "456",
    "lat": 37.7749,
    "lng": -122.4194,
    "heading": 45,
    "timestamp": 1640995200
}

// Get nearby drivers
GET /location/drivers/nearby?lat=37.7749&lng=-122.4194&radius=5km
Response: {
    "drivers": [
        {
            "driver_id": "456",
            "lat": 37.7750,
            "lng": -122.4195,
            "distance_km": 0.2,
            "eta_minutes": 3
        }
    ]
}
```

### Trip Service APIs

#### Ride Request Flow
```java
// Request ride
POST /trips/request
{
    "rider_id": "123",
    "pickup": {"lat": 37.7749, "lng": -122.4194},
    "destination": {"lat": 37.7849, "lng": -122.4094},
    "ride_type": "uberx"
}
Response: {
    "trip_id": "trip_789",
    "status": "searching",
    "estimated_fare": 15.50
}

// Update trip status
PUT /trips/{trip_id}/status
{
    "status": "driver_assigned|pickup|started|completed",
    "driver_id": "456",
    "location": {"lat": 37.7749, "lng": -122.4194}
}

// Live trip tracking
GET /trips/{trip_id}/live
Response: {
    "driver_location": {"lat": 37.7750, "lng": -122.4195},
    "eta_pickup": 3,
    "eta_destination": 12,
    "route": [...]
}
```

### Matching Service APIs

#### Driver-Rider Matching
```java
// Find and assign driver (Internal API)
POST /matching/assign
{
    "trip_id": "trip_789",
    "pickup_location": {"lat": 37.7749, "lng": -122.4194},
    "max_search_radius": 5,
    "ride_type": "uberx"
}

// Driver response to ride request
POST /matching/respond
{
    "trip_id": "trip_789",
    "driver_id": "456",
    "action": "accept|reject",
    "eta": 3
}
```

### Pricing Service APIs

#### Dynamic Pricing
```java
// Get ride estimate
POST /pricing/estimate
{
    "pickup": {"lat": 37.7749, "lng": -122.4194},
    "destination": {"lat": 37.7849, "lng": -122.4094},
    "ride_type": "uberx"
}
Response: {
    "base_fare": 2.50,
    "per_km": 1.20,
    "per_minute": 0.30,
    "surge_multiplier": 1.8,
    "estimated_total": 18.50
}

// Calculate final fare
POST /pricing/calculate
{
    "trip_id": "trip_789",
    "distance_km": 5.2,
    "duration_minutes": 12,
    "surge_multiplier": 1.8
}
```

## 4. Key Services Implementation

### Location Service
```java
@Service
public class LocationService {
    
    // Store driver locations in Redis with TTL
    public void updateDriverLocation(String driverId, Location location) {
        String key = "driver:location:" + driverId;
        redisTemplate.opsForGeo().add(key, location.getLng(), location.getLat(), driverId);
        redisTemplate.expire(key, Duration.ofMinutes(5)); // TTL for inactive drivers
    }
    
    // Find nearby drivers using Redis GeoSpatial
    public List<Driver> findNearbyDrivers(Location pickup, double radiusKm) {
        return redisTemplate.opsForGeo()
            .radius("drivers:active", pickup.getLng(), pickup.getLat(), 
                   new Distance(radiusKm, Metrics.KILOMETERS));
    }
}
```

### Matching Service
```java
@Service
public class MatchingService {
    
    public void findDriver(Trip trip) {
        List<Driver> nearbyDrivers = locationService.findNearbyDrivers(
            trip.getPickupLocation(), 5.0);
            
        // Sort by distance and rating
        nearbyDrivers.sort((d1, d2) -> 
            Double.compare(d1.getDistance(), d2.getDistance()));
            
        // Send requests to top 3 drivers
        for (Driver driver : nearbyDrivers.subList(0, Math.min(3, nearbyDrivers.size()))) {
            sendRideRequest(trip, driver);
        }
    }
}
```

### Trip Service
```java
@Service
public class TripService {
    
    @Transactional
    public Trip createTrip(TripRequest request) {
        Trip trip = Trip.builder()
            .riderId(request.getRiderId())
            .pickupLocation(request.getPickup())
            .destination(request.getDestination())
            .status(TripStatus.SEARCHING)
            .build();
            
        Trip savedTrip = tripRepository.save(trip);
        
        // Trigger matching asynchronously
        matchingService.findDriver(savedTrip);
        
        return savedTrip;
    }
}
```

## 5. Database Schema

```sql
-- Core tables
CREATE TABLE trips (
    trip_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL,
    driver_id UUID,
    pickup_lat DECIMAL(10,8),
    pickup_lng DECIMAL(11,8),
    dest_lat DECIMAL(10,8),
    dest_lng DECIMAL(11,8),
    status VARCHAR(20),
    fare DECIMAL(8,2),
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE drivers (
    driver_id UUID PRIMARY KEY,
    status VARCHAR(20), -- online, offline, busy
    current_lat DECIMAL(10,8),
    current_lng DECIMAL(11,8),
    rating DECIMAL(3,2),
    last_active TIMESTAMP
);
```

## 6. Scaling Considerations

### Location Data
- **Redis Cluster**: Geospatial data with sharding by city
- **Real-time updates**: WebSocket connections with load balancing
- **Data retention**: 5-minute TTL for inactive drivers

### Matching Algorithm
- **Async processing**: Queue-based matching to handle peak loads
- **Fallback strategy**: Expand search radius if no drivers found
- **Load balancing**: Distribute matching requests across multiple instances

### Database Sharding
```java
// Shard trips by city/region
public int getShardId(Location location) {
    return getCityId(location) % NUM_SHARDS;
}
```

This simplified design focuses on the core ride-sharing functionality that makes Uber unique, removing standard app features like authentication, user management, and basic CRUD operations.
