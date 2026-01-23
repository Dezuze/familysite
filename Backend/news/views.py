from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly


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
        # News items OR Past events
        now = timezone.now()
        return Post.objects.filter(
            Q(post_type='news') | 
            Q(post_type='event', event_date__lt=now) |
            Q(post_type='event', event_date__isnull=True) # Fallback if no date set
        ).order_by('-created_at')


class NewsCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # User -> Member
        if hasattr(self.request.user, 'member') and self.request.user.member:
            post = serializer.save(creator=self.request.user.member)
            
            # Handle Image Upload
            if 'image' in self.request.FILES:
                from .models import Media
                image = self.request.FILES['image']
                Media.objects.create(
                    uploader=self.request.user.member,
                    post=post,
                    media_url=image,
                    media_type='image'
                )
        else:
            raise ValueError("User must be linked to a Family Member to post.")


class NewsDetailView(RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

