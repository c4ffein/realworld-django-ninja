from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from taggit.models import Tag
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from articles.models import Article


User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('username', 'bio', 'image', 'following')
        
    def get_following(self, other_user):
        return self.context.get('request').user.is_following(other_user)

    
class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)
    description = serializers.CharField(source='summary')
    body = serializers.CharField(source='content')
    tagList = TagListSerializerField(source='tags', required=False)
    createdAt = serializers.DateTimeField(source='created',format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
    updatedAt = serializers.DateTimeField(source='updated',format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body', 'tagList', 'createdAt',
                  'updatedAt', 'favorited', 'favoritesCount', 'author']
        read_only_fields = ['slug', 'createdAt', 'updatedAt', 'author']
    
    def get_author(self, obj):
        request = self.context.get('request') 
        # serializer = AuthorSerializer(request.user, context={'request': request})
        serializer = AuthorSerializer(obj.author, context={'request': request})
        return serializer.data
    
    def get_favorited(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return instance.favorites.filter(pk=request.user.pk).exists()
        return False
    
    def get_favoritesCount(self, instance):
        return instance.favorites.count()
       
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        article = Article(
            author=self.context['request'].user,
            **validated_data
        )
        article.save()
        article.tags.add(*tags)
        return article
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        instance.tags.clear()
        instance.tags.add(*tags)
        
        return instance
    
    
class TagSerializer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.CharField()
    )
