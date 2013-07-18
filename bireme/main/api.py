from tastypie.resources import ModelResource
from tastypie import fields
import models


class ResourceAPI(ModelResource):
    # descriptors relationship 
    descriptors = fields.ToManyField('main.api.DescriptorResource', 'resources', related_name='resource', full=True, null=True)

    class Meta:
        queryset = models.Resource.objects.all()
        allowed_methods = ['get']
        resource_name = 'resource'

class DescriptorResource(ModelResource):    
    resource = fields.ToOneField('main.api.ResourceAPI', 'resource')

    class Meta:
        queryset = models.Descriptor.objects.all()
        resource_name = 'descriptor'
