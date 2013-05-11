import datetime
import pytz

from django.db import models
from django.db.models.query import QuerySet


class CustomManager(models.Manager):
    def get_query_set(self):
        return CustomQuerySet(self.model).exclude(dead=True)


class CustomQuerySet(QuerySet):
    def get(self, *args, **kwargs):
        pk = kwargs.get('pk') or kwargs.get('id')
        return super(CustomQuerySet, self).get(*args, **kwargs)

    def dead(self):
        return self.filter(dead=True)

    def non_dead(self):
        return self.filter(dead=False)

    def get_or_none(self, *args, **kwargs):
        try:
            result = self.get(*args, **kwargs)
            return result
        except self.model.DoesNotExist:
            return None


class CustomModel(models.Model):

    dead = models.BooleanField(default=False)
    create_date = models.DateTimeField("date added")

    objects = CustomManager()
    all_objects = models.Manager()

    def pre_save(self):
        if not self.create_date:
            self.create_date = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    def save(self, *args, **kwargs):
         self.pre_save()
         return super(CustomModel, self).save(*args, **kwargs)
 
    def delete(self):
        self.dead = True
        self.save()

    class Meta:
        abstract = True
