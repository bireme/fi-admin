from django.contrib import admin
from django.core.cache import cache

from classification.models import *


class CollectionLocalAdmin(admin.TabularInline):
    model = CollectionLocal
    extra = 1


class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    list_display = ('community_collection_path', 'country')
    inlines = [CollectionLocalAdmin, ]
    list_filter = (('country', admin.RelatedOnlyFieldListFilter),'community_flag',)
    ordering = ('parent',)
    actions = ['clear_cache']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def clear_cache(self, request, queryset):
        for collection in queryset:
            for cache_lang in ['pt', 'es', 'en']:
                cache_id_c = "classification_collection-{}-{}".format(cache_lang, collection.id)
                cache_id_f = "classification_collection_fullpath-{}-{}".format(cache_lang, collection.id)
                try:
                    cache.delete(cache_id_c)
                    cache.delete(cache_id_f)
                except:
                    pass

    clear_cache.short_description = 'Clear cache of selected communities/collections'



admin.site.register(Collection, CollectionAdmin)
admin.site.register(Relationship)
