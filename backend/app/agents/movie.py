<![CDATA["""
Movie Agent
Handles movie search and showtime information.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.agents.base import BaseAgent, Tool, Task


class MovieAgent(BaseAgent):
    """
    Agent specialized in entertainment services.
    
    Capabilities:
    - Search for movies
    - Get now playing movies
    - Find showtimes at nearby theaters
    - Get movie details and reviews
    """
    
    name = "MovieAgent"
    description = "Handles movie search and showtime information"
    
    SUPPORTED_TASKS = [
        "search_movies",
        "get_now_playing",
        "get_showtimes",
        "get_movie_details"
    ]
    
    def _initialize_tools(self):
        """Initialize movie-specific tools."""
        self.tools = [
            Tool(
                name="search_movies",
                description="Search for movies by title or genre",
                parameters={
                    "query": "Search query",
                    "genre": "Optional genre filter",
                    "year": "Optional year filter"
                },
                function=self._search_movies,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="get_now_playing",
                description="Get movies currently in theaters",
                parameters={
                    "region": "Region/country code"
                },
                function=self._get_now_playing,
                requires_confirmation=False,
                timeout_seconds=30
            ),
            Tool(
                name="get_showtimes",
                description="Get showtimes at nearby theaters",
                parameters={
                    "movie_id": "Movie ID",
                    "location": "User location",
                    "date": "Date for showtimes"
                },
                function=self._get_showtimes,
                requires_confirmation=False,
                timeout_seconds=45
            ),
            Tool(
                name="get_movie_details",
                description="Get detailed information about a movie",
                parameters={
                    "movie_id": "Movie ID"
                },
                function=self._get_movie_details,
                requires_confirmation=False,
                timeout_seconds=15
            )
        ]
    
    async def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        return task.type in self.SUPPORTED_TASKS
    
    async def plan(self, task: Task, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan for movie tasks."""
        task_type = task.type
        params = task.parameters
        
        if task_type == "search_movies":
            steps = [{
                "tool": "search_movies",
                "parameters": {
                    "query": params.get("query"),
                    "genre": params.get("genre"),
                    "year": params.get("year")
                }
            }]
            
            # If date is specified, also get showtimes
            if params.get("date"):
                steps.append({
                    "tool": "get_showtimes",
                    "parameters": {
                        "movie_id": "{previous.movies[0].id}",
                        "location": context.get("location", {}),
                        "date": params.get("date")
                    }
                })
            
            return steps
        
        elif task_type == "get_now_playing":
            return [{
                "tool": "get_now_playing",
                "parameters": {
                    "region": params.get("region", "EG")
                }
            }]
        
        elif task_type == "get_showtimes":
            return [{
                "tool": "get_showtimes",
                "parameters": {
                    "movie_id": params.get("movie_id"),
                    "location": context.get("location", {}),
                    "date": params.get("date", datetime.now().strftime("%Y-%m-%d"))
                }
            }]
        
        elif task_type == "get_movie_details":
            return [{
                "tool": "get_movie_details",
                "parameters": {
                    "movie_id": params.get("movie_id")
                }
            }]
        
        return []
    
    async def _search_movies(
        self,
        query: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for movies using TMDB API.
        
        In production, this would call the actual TMDB API.
        """
        # Mock response
        movies = [
            {
                "id": "movie_dune2",
                "title": "Dune: Part Two",
                "overview": "Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen...",
                "release_date": "2024-03-01",
                "rating": 8.5,
                "runtime_minutes": 166,
                "genres": ["Sci-Fi", "Adventure", "Drama"],
                "poster_url": "https://image.tmdb.org/t/p/w500/dune2.jpg",
                "now_playing": True
            },
            {
                "id": "movie_oppenheimer",
                "title": "Oppenheimer",
                "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                "release_date": "2023-07-21",
                "rating": 8.4,
                "runtime_minutes": 180,
                "genres": ["Drama", "History", "Biography"],
                "poster_url": "https://image.tmdb.org/t/p/w500/oppenheimer.jpg",
                "now_playing": True
            },
            {
                "id": "movie_aquaman2",
                "title": "Aquaman and the Lost Kingdom",
                "overview": "Black Manta seeks revenge on Aquaman for his father's death...",
                "release_date": "2023-12-22",
                "rating": 6.5,
                "runtime_minutes": 124,
                "genres": ["Action", "Adventure", "Fantasy"],
                "poster_url": "https://image.tmdb.org/t/p/w500/aquaman2.jpg",
                "now_playing": True
            }
        ]
        
        # Filter by query if provided
        if query:
            query_lower = query.lower()
            movies = [m for m in movies if query_lower in m["title"].lower()]
        
        # Filter by genre if provided
        if genre:
            genre_lower = genre.lower()
            movies = [m for m in movies if any(genre_lower in g.lower() for g in m["genres"])]
        
        return {
            "query": query,
            "genre_filter": genre,
            "movies": movies,
            "total_found": len(movies)
        }
    
    async def _get_now_playing(self, region: str = "EG") -> Dict[str, Any]:
        """Get movies currently in theaters."""
        # Mock response
        movies = [
            {
                "id": "movie_dune2",
                "title": "Dune: Part Two",
                "rating": 8.5,
                "genres": ["Sci-Fi", "Adventure"],
                "poster_url": "https://image.tmdb.org/t/p/w500/dune2.jpg"
            },
            {
                "id": "movie_oppenheimer",
                "title": "Oppenheimer",
                "rating": 8.4,
                "genres": ["Drama", "History"],
                "poster_url": "https://image.tmdb.org/t/p/w500/oppenheimer.jpg"
            },
            {
                "id": "movie_anyone_but_you",
                "title": "Anyone But You",
                "rating": 6.3,
                "genres": ["Romance", "Comedy"],
                "poster_url": "https://image.tmdb.org/t/p/w500/anyonebutyou.jpg"
            }
        ]
        
        return {
            "region": region,
            "movies": movies,
            "total": len(movies),
            "as_of": datetime.now().strftime("%Y-%m-%d")
        }
    
    async def _get_showtimes(
        self,
        movie_id: str,
        location: Dict[str, Any],
        date: str
    ) -> Dict[str, Any]:
        """Get showtimes at nearby theaters."""
        # Mock response
        theaters = [
            {
                "id": "theater_vox_citystars",
                "name": "VOX Cinemas - City Stars",
                "address": "City Stars Mall, Nasr City",
                "distance_km": 5.2,
                "showtimes": [
                    {
                        "time": f"{date}T14:30:00",
                        "format": "IMAX",
                        "language": "English",
                        "subtitles": "Arabic",
                        "available_seats": 45,
                        "price": 250
                    },
                    {
                        "time": f"{date}T18:00:00",
                        "format": "IMAX",
                        "language": "English",
                        "subtitles": "Arabic",
                        "available_seats": 120,
                        "price": 250
                    },
                    {
                        "time": f"{date}T21:30:00",
                        "format": "Standard",
                        "language": "English",
                        "subtitles": "Arabic",
                        "available_seats": 85,
                        "price": 180
                    }
                ]
            },
            {
                "id": "theater_galaxy",
                "name": "Galaxy Cinema - Mall of Arabia",
                "address": "Mall of Arabia, 6th October",
                "distance_km": 12.8,
                "showtimes": [
                    {
                        "time": f"{date}T15:00:00",
                        "format": "4DX",
                        "language": "English",
                        "subtitles": "Arabic",
                        "available_seats": 30,
                        "price": 350
                    },
                    {
                        "time": f"{date}T19:00:00",
                        "format": "Standard",
                        "language": "English",
                        "subtitles": "Arabic",
                        "available_seats": 95,
                        "price": 150
                    }
                ]
            }
        ]
        
        return {
            "movie_id": movie_id,
            "date": date,
            "theaters": theaters,
            "total_theaters": len(theaters),
            "currency": "EGP"
        }
    
    async def _get_movie_details(self, movie_id: str) -> Dict[str, Any]:
        """Get detailed movie information."""
        # Mock response
        return {
            "id": movie_id,
            "title": "Dune: Part Two",
            "original_title": "Dune: Part Two",
            "overview": "Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen while on a warpath of revenge against the conspirators who destroyed his family.",
            "tagline": "Long live the fighters.",
            "release_date": "2024-03-01",
            "runtime_minutes": 166,
            "rating": 8.5,
            "vote_count": 4521,
            "genres": ["Sci-Fi", "Adventure", "Drama"],
            "director": "Denis Villeneuve",
            "cast": [
                {"name": "Timothée Chalamet", "character": "Paul Atreides"},
                {"name": "Zendaya", "character": "Chani"},
                {"name": "Rebecca Ferguson", "character": "Lady Jessica"}
            ],
            "poster_url": "https://image.tmdb.org/t/p/w500/dune2.jpg",
            "backdrop_url": "https://image.tmdb.org/t/p/original/dune2_backdrop.jpg",
            "budget": 190000000,
            "revenue": 494000000,
            "status": "Released"
        }
]]>
