from datetime import datetime, date
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly
from .services.daily_posters import ensure_daily_posters, run_daily_poster_generation
 

class EventsListView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        # Future events: post_type='event' AND event_date >= now
        return Post.objects.filter(
            post_type='event', 
            event_date__gte=timezone.now()
        ).order_by('event_date')


class NewsListView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        # Trigger daily celebration poster generation if not yet run today
        ensure_daily_posters()

        # News items OR Past events
        now = timezone.now()
        return Post.objects.filter(
            Q(post_type='news') | 
            Q(post_type='event', event_date__lt=now) |
            Q(post_type='event', event_date__isnull=True) # Fallback if no date set
        ).order_by('-created_at')


class CelebrationNotificationsView(APIView):
    """
    Returns auto-generated birthday, wedding anniversary, and remembrance
    celebration notifications for the PWA and in-app notification center.
    Automatically ensures today's celebration posters have been generated.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        ensure_daily_posters()

        target_date_str = request.query_params.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                run_daily_poster_generation(target_date=target_date)
            except ValueError:
                pass

        limit = int(request.query_params.get('limit', 12))
        auto_posts = Post.objects.filter(is_auto_generated=True).order_by('-created_at')[:limit]
        serializer = PostSerializer(auto_posts, many=True)

        today_iso = date.today().isoformat()
        today_count = Post.objects.filter(
            is_auto_generated=True,
            created_at__date=date.today()
        ).count()

        return Response({
            'date': today_iso,
            'today_count': today_count,
            'total_recent': len(serializer.data),
            'notifications': serializer.data,
        })


class NewsCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # User -> Member
        member = getattr(self.request.user, 'member', None)
        if member:
            post = serializer.save(creator=member)
            
            # Handle Single or Multiple Image Uploads
            images = self.request.FILES.getlist('images') or self.request.FILES.getlist('image')
            if images:
                from .models import Media
                for image in images:
                    Media.objects.create(
                        uploader=member,
                        post=post,
                        media_url=image,
                        media_type='image'
                    )
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"error": "Your user account is not linked to a Family Member profile. Please contact an admin or complete your onboarding to post news."})


class NewsDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
