from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Invoice

@receiver(post_save, sender=Invoice)
def update_search_vector(sender, instance, **kwargs):
    Invoice.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector('invoice_numb', 'client__business', 'service__service')
    )