"""
Rate Limiter Implementation - SAFE version
Fully meets all the requirements
"""

import time
import threading
from collections import defaultdict, deque
from typing import Tuple


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int) -> None:
        """
        Initialize Rate Limiter.
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        Raises:
            ValueError: If max_requests or time_window is not positive
        """
        # True: Validates max_requests (requirement #2)
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than 0")
        
        # True: Validates time_window (requirement #3)
        if time_window <= 0:
            raise ValueError("time_window must be greater than 0")
        
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
        
        # True: Thread safety (requirement #11)
        self.lock = threading.Lock()
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for given identifier.
        Args:
            identifier: User identifier (user_id, IP, API key)
        Returns:
            Tuple of (allowed, retry_after)
                - allowed: True if request is allowed, False otherwise
                - retry_after: Seconds to wait before retry (0 if allowed)
        Raises:
            ValueError: If identifier is None or empty
        """
        # True: Handles None/empty identifier (requirement #9)
        if not identifier:
            raise ValueError("identifier cannot be None or empty")
        
        current_time = time.time()
        
        # True: Thread safety (requirement #11)
        with self.lock:
            # True: Remove expired requests (requirement #8)
            while (self.requests[identifier] and 
                   current_time - self.requests[identifier][0] >= self.time_window):
                self.requests[identifier].popleft()
            
            # Check if limit exceeded
            if len(self.requests[identifier]) >= self.max_requests:
                # True: Returns (False, retry_seconds) (requirement #6)
                oldest = self.requests[identifier][0]
                retry_after = int(self.time_window - (current_time - oldest)) + 1
                return (False, retry_after)
            
            # True: Tracks timestamp (requirement #7)
            self.requests[identifier].append(current_time)
            
            # True: Returns (True, 0) (requirement #5)
            return (True, 0)
    
    def reset(self, identifier: str) -> None:
        """
        Reset rate limit data for given identifier
        Args:
            identifier: User identifier to reset
        """
        # True: Clears data (requirement #10)
        with self.lock:
            if identifier in self.requests:
                del self.requests[identifier]