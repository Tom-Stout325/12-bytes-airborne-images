from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Value
from .models import Invoice

@receiver(post_save, sender=Invoice)
def update_search_vector(sender, instance, **kwargs):
    # Safely get joined values
    client_business = instance.client.business if instance.client else ""
    service_name = instance.service.service if instance.service else ""

    # Combine values into one vector
    vector = (
        SearchVector(Value(instance.invoice_numb), weight='A') +
        SearchVector(Value(client_business), weight='B') +
        SearchVector(Value(service_name), weight='B')
    )

    # Assign and save only the search_vector field
    instance.search_vector = vector
    instance.save(update_fields=['search_vector'])
