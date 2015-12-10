from django.contrib.auth.admin import UserAdmin


class DjangoUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'date_joined')

    def get_actions(self, request):
        #  Disable delete
        actions = super(DjangoUserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False
