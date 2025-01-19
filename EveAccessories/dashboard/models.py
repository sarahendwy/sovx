from django.db import models

class Setting(models.Model):
    instapay_image = models.ImageField(upload_to="dashboard/settings/")
    hero_image = models.ImageField(upload_to="dashboard/settings/")
    shipping_costs = models.JSONField(default=dict)

    def __str__(self):
        return self.key