from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Snippet


# class SnippetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Snippet
#         owner = serializers.ReadOnlyField(source='owner.username')
#         fields = ('id', 'title', 'code', 'linenos', 'language', 'style')


# class UserSerializer(serializers.ModelSerializer):
#     snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'snippets')


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    url = serializers.HyperlinkedIdentityField(view_name='snippets-detail')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippets-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippets-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')
