from rest_framework import serializers
from ..models import Petition, Comment

class PetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Petition
        fields = ['id', 'title', 'description', 'status', 'category', 'created_by', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_at']
