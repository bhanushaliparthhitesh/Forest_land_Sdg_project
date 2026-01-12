# We are using MongoDB via PyMongo directly in views.py
# So no Django models are required for this project.

from django.db import models

class Population(models.Model):
    species = models.CharField(max_length=100)
    year = models.IntegerField()
    population = models.IntegerField()

    def __str__(self):
        return f"{self.species} - {self.year}"
