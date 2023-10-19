from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notification_app.models import Notification


class PrivateChatRoom(models.Model):
    """
    A private room for people to chat
    """
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="user2", null=True, blank=True)

    # Users who are currently connected to the socket (Used to keep track of unread messages)
    connected_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user1}"

    def connect_user(self, user):
        """
        return true if user is added to the connected_users list
        """
        is_user_added = False
        if not user in self.connected_users.all():
            self.connected_users.add(user)
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        """
        return true if user is removed from connected_users list
        """
        is_user_removed = False
        if user in self.connected_users.all():
            self.connected_users.remove(user)
            is_user_removed = True
        return is_user_removed

    @property
    def group_name(self):
        """
        Returns the channels group name that socket shoup subscribe to so they get sent 
        messages as they are generated
        """
        return f"PrivateChatRoom-{self.id}"
    

class RoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = RoomChatMessage.objects.filter(room = room).order_by("-timestamp")
        return qs


class RoomChatMessage(models.Model):
    """
    Chat message created by a user inside a room
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add = True)
    content = models.TextField(unique = False, blank = False)

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.content
    

class UnreadChatRoomMessages(models.Model):
    """
    Keep track of the number of unread messages by a specific user in a specific private chat.
    When the user connects the chat room, the messages will be considered "read" and 'count' will be set to 0.
    """
    room                = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name="room")

    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    count               = models.IntegerField(default=0)

    most_recent_message = models.CharField(max_length=500, blank=True, null=True)

    # last time msgs were read by the user
    reset_timestamp     = models.DateTimeField()

    notifications       = GenericRelation(Notification)

    def __str__(self):
        return f"Messages that {str(self.user.username)} has not read yet."


    def save(self, *args, **kwargs):
        if not self.id: # if just created, add a timestamp. Otherwise do not automatically change it ever.
            self.reset_timestamp = timezone.now()
        return super(UnreadChatRoomMessages, self).save(*args, **kwargs)
    
    @property
    def get_cname(self):
        """
        For determining what kind of object is associated with a Notification
        """
        return "UnreadChatRoomMessages"
    
    @property
    def get_other_user(self):
        """
        Get the other user in the chat room
        """
        if self.user == self.room.user1:
            return self.room.user2
        else:
            return self.room.user1