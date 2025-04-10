from .views import log_activity
import re
from django.urls import resolve

class ActivityLogMiddleware:
    """
    Middleware for automatically logging certain user activities
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # URL patterns to monitor - regex pattern, action_type, content_type
        self.monitored_patterns = [
            (r'^/api/accounts/login/$', 'LOGIN', 'SYSTEM'),
            (r'^/api/accounts/logout/$', 'LOGOUT', 'SYSTEM'),
            (r'^/api/documents/employees/\d+/$', 'VIEW', 'EMPLOYEE'),
            (r'^/api/documents/attestations/\d+/$', 'VIEW', 'ATTESTATION'),
            (r'^/api/documents/missions/\d+/$', 'VIEW', 'MISSION'),
        ]
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only log for authenticated users and successful responses
        if (hasattr(request, 'user') and request.user.is_authenticated 
                and 200 <= response.status_code < 300):
            
            path = request.path
            
            # Check if the path matches any of our monitored patterns
            for pattern, action_type, content_type in self.monitored_patterns:
                if re.match(pattern, path):
                    # Extract content_id from URL if present
                    content_id = None
                    match = re.search(r'/(\d+)/', path)
                    if match:
                        content_id = int(match.group(1))
                    
                    # Log the activity
                    description = f"{action_type} {content_type}"
                    if content_id:
                        description += f" ID: {content_id}"
                    
                    log_activity(
                        user=request.user,
                        action_type=action_type,
                        content_type=content_type,
                        content_id=content_id,
                        description=description,
                        request=request
                    )
                    break
        
        return response
