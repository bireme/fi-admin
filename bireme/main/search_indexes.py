import datetime
from haystack import indexes
from main.models import Resource, Descriptor


class ResourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    link = indexes.CharField(model_attr='link')
    abstract = indexes.CharField(model_attr='abstract')
    descriptors = indexes.MultiValueField()

    def get_model(self):
        return Resource

    def prepare_descriptors(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [descriptor.code for descriptor in Descriptor.objects.filter(resource=obj.id)]


    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_time__lte=datetime.datetime.now())