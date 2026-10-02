from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Users sign in with their email address; there is no username."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError('The email address is required.')
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        if not (extra['is_staff'] and extra['is_superuser']):
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        return self._create_user(email, password, **extra)
