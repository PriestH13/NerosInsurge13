from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from .models import Petition, PetitionStatus, Comment, Signature, PendingSignature, PetitionVote
from .serializers import PetitionSerializer, CommentSerializer
from .utils import get_client_ip


class PetitionListAPI(generics.ListCreateAPIView):
    queryset = Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)
    serializer_class = PetitionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PetitionDetailAPI(generics.RetrieveAPIView):
    queryset = Petition.objects.all()
    serializer_class = PetitionSerializer


class PetitionCommentsAPI(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        petition_id = self.kwargs['pk']
        return Comment.objects.filter(petition_id=petition_id).order_by('-created_at')

    def perform_create(self, serializer):
        petition = get_object_or_404(Petition, pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, petition=petition)


class PetitionVoteAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        petition = get_object_or_404(Petition, pk=pk)
        vote_value = request.data.get('vote')

        if vote_value not in ['up', 'down']:
            return Response({"error": "Valore voto non valido"}, status=status.HTTP_400_BAD_REQUEST)

        is_upvote = vote_value == 'up'
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)

        vote_filter = {'petition': petition}
        if user:
            vote_filter['user'] = user
            vote_filter['ip_address__isnull'] = True
        else:
            vote_filter['user__isnull'] = True
            vote_filter['ip_address'] = ip

        vote = PetitionVote.objects.filter(**vote_filter).first()

        if vote:
            if vote.is_upvote != is_upvote:
                vote.is_upvote = is_upvote
                vote.save()
            else:
                vote.delete()
        else:
            PetitionVote.objects.create(
                petition=petition,
                user=user,
                ip_address=None if user else ip,
                is_upvote=is_upvote,
            )
        return Response({'detail': 'Voto registrato'}, status=status.HTTP_200_OK)


class PetitionSignAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        petition = get_object_or_404(Petition, pk=pk)
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email richiesta"}, status=status.HTTP_400_BAD_REQUEST)

        if Signature.objects.filter(petition=petition, email=email).exists():
            return Response({"detail": "Hai già firmato questa petizione con questa email."}, status=status.HTTP_200_OK)
        else:
            pending = PendingSignature.objects.create(petition=petition, email=email)
            confirm_url = request.build_absolute_uri(
                reverse('petitions:confirm_signature', kwargs={'token': pending.token})
            )
            send_mail(
                subject='Conferma la tua firma',
                message=f'Clicca per confermare la firma:\n{confirm_url}',
                from_email='noreply@tuosito.it',
                recipient_list=[email],
            )
            return Response({"detail": "Email di conferma inviata."}, status=status.HTTP_201_CREATED)
