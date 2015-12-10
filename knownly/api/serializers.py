from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = super(UserSerializer, self).restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user

    class Meta:
        model = User
        fields = ('password', 'confirm_password', 'first_name',
                  'last_name', 'email')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

        def update(self, instance, validated_data):
            instance.first_name = validated_data.get('first_name',
                                                     instance.first_name)
            instance.last_name = validated_data.get('last_name',
                                                    instance.last_name)

            instance.save()

            password = validated_data.get('password', None)
            confirm_password = validated_data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            update_session_auth_hash(self.context.get('request'), instance)

            return instance
