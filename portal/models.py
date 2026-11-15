from django.contrib.auth.models import User

class MentorshipRequest(models.Model):
    STATUS = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    alumnus = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)