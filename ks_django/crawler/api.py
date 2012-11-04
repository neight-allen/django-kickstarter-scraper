# crawler/api.py
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from crawler.models import *

class RewardResource(ModelResource):
    class Meta:
        queryset = Reward.objects.all()
        resource_name = 'reward'
        filtering = {
            'price': ['gt', 'gte', 'lt', 'lte']
        }
        fields = ['price', 'backers']

class ProjectResource(ModelResource):
    rewards = fields.ToManyField(RewardResource, 'rewards', full=True)
    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'
        filtering = {
            'parentCat': ALL
        }
        excludes = ['about']

