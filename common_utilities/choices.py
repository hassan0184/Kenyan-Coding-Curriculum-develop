from django.db import models
from django.utils.translation import gettext_lazy as _



class GradeLevelChoices(models.TextChoices):
        FIRST = 1, _('First')
        SECOND = 2, _('Second')
        THIRD = 3, _('Third')
        FOURTH = 4, _('Fourth')
        FIFTH = 5, _('Fifth')
        SIXTH = 6, _('Sixth')
        SEVENTH = 7, _('Seventh')
        EIGHT = 8, _('Eight')
        NINTH = 9, _('Ninth')
        TENTH = 10, _('Tenth')
        ELEVENTH = 11, _('Eleventh')


class AssignmentTypeChoices(models.TextChoices):
    ASSESMENT_BY_TEKS = 1, _('Assesment by TEKS')
    ASSESMENT_BY_SKILLS = 2, _('Assesment by Skills')
    ASSESMENT_BY_WORKSHEET = 3, _('Assesment by Work sheet')