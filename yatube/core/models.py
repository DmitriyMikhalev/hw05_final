from django.db import models


class AbstractModel(models.Model):
    """Abstract model contains a DateTimeField
    with flag auto_now_add set to True"""

    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        abstract = True
