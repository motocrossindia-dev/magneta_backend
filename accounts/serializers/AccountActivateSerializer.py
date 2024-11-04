from rest_framework import serializers

from accounts.models import UserBase


class POSTAccountActivateSerializer(serializers.Serializer):

    def validate(self, data):
        user = UserBase.objects.filter(id=self.context.get('request').get('uid')).first()
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["User not found."]})
        else:
            user.is_active = True
            user.save()
            data['user'] = user
            return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        representation.pop('email', None)

        user = instance['user']
        representation['profile_picture'] = user.profile_picture.url if user.profile_picture else None
        representation['first_name'] = user.first_name
        representation['last_name'] = user.last_name if user.last_name else None
        return representation
