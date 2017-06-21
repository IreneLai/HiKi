from __future__ import print_function

import datetime

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.core import signing
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from google_api.gmail import send_mail

class UserQuerySet(models.QuerySet):
    """Custom queryset for User.
    """
    def get_valid_user(self):
        """Filter only valid users from the queryset.
        :seealso: ``User.is_valid_user``
        """
        users = self.filter(verified=True, is_active=True)
        users = users.exclude(name='')
        return users

class UserManager(BaseUserManager):
    """Custom manager for User
    """
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return custom_user.models.EmailUser user: user
        :raise ValueError: email is not set
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        last_login = extra_fields.pop('last_login', now)
        date_joined = extra_fields.pop('date_joined', now)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=last_login,
            date_joined=date_joined,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: regular user
        """
        if settings.DEBUG:
            return self._create_user(email, password, verified=True, **extra_fields)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: admin user
        """
        return self._create_user(
            email, password, verified=True,
            is_staff=True, is_superuser=True,
            **extra_fields)

    def get_with_verification_key(self, verification_key):
        """Get a user from verification key.
        """
        try:
            username = signing.loads(
                verification_key,
                salt=settings.SECRET_KEY,
            )
        except signing.BadSignature:
            raise self.model.DoseNotExist
        return self.get(**{self.model.USERNAME_FIELD: username})

def photo_upload_to(instance, filename):
    return 'avatars/{pk}/{date}-{filename}'.format(
        pk=instance.pk,
        date=str(datetime.date.today()),
        filename=filename,
        )

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_("Email Address"),
        max_length=255, unique=True, db_index=True,
    )
    name = models.CharField(
        verbose_name=_("User Name"),
        max_length=100, default='',
    )
    photo = models.ImageField(
        verbose_name=_('Photo'),
        blank=True, default='', upload_to='avatars/'
    )
    bio = models.TextField(
        verbose_name=_('Biography'),
        max_length=1000, blank=True, default='',
        help_text=_(
            "Describe yourself with 500 characters or less. "
            "There will be no formatting."
        ),
    )
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
        help_text=_(
            "Designates whether the user has verified email ownership."
        ),
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('users')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    @property
    def is_valid_user(self):
        """Whether the user is a valid user.
        :seealso: ``UserQuerySet.get_valid_user``
        """
        return (
            self.verified and self.is_active and self.name
        )

    def email_user(self, subject, message):
        send_mail(
            subject, message,
            settings.EMAIL_ADDRESS, self.email,
            settings.EMAIL_HOST, self.name
        )

    def get_verification_key(self):
        key = signing.dumps(
            obj=getattr(self, self.USERNAME_FIELD),
            salt=settings.SECRET_KEY,
        )
        return key

    def send_verification_email(self, request):
        verification_key = self.get_verification_key()
        verification_url =request.build_absolute_uri(
            reverse('user_verify', kwargs={
                'verification_key': verification_key,
            }),
        )

        context = {
            'user': self.email,
            'host': request.get_host(),
            'verification_key': verification_key,
            'verification_url': verification_url,
        }
        message = render_to_string(
            'registration/verification_email.txt', context,
        )

        self.email_user(
            subject=ugettext('Verify your email address on {host}').format(**context),
            message=message.strip(),
        )
