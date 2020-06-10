# -*- coding: utf-8 -*-
import graphene


class DefaultConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info):
        return self.length
