from django.db import models

egypt_governorates = [('Cairo', 'Cairo'), ('Alexandria', 'Alexandria'), ('Giza', 'Giza'), ('Qalyubia', 'Qalyubia'),
                      ('Port Said', 'Port Said'), ('Suez', 'Suez'), ('Dakahlia', 'Dakahlia'), ('Sharkia', 'Sharkia'),
                      ('Monufia', 'Monufia'), ('Gharbia', 'Gharbia'), ('Kafr El Sheikh', 'Kafr El Sheikh'),
                      ('Beheira', 'Beheira'), ('Ismailia', 'Ismailia'), ('Beni Suef', 'Beni Suef'),
                      ('Fayoum', 'Fayoum'), ('Minya', 'Minya'), ('Assiut', 'Assiut'), ('Sohag', 'Sohag'),
                      ('Qena', 'Qena'), ('Luxor', 'Luxor'), ('Aswan', 'Aswan'), ('Red Sea', 'Red Sea'),
                      ('New Valley', 'New Valley'), ('Matruh', 'Matruh'), ('North Sinai', 'North Sinai'),
                      ('South Sinai', 'South Sinai')]

class Setting(models.Model):
    payment_image = models.ImageField(upload_to="dashboard/settings/")
    hero_image = models.ImageField(upload_to="dashboard/settings/")
    homepage_categories_count = models.PositiveIntegerField(default=4, help_text="Number of categories to display on homepage")
    cairo_shipping = models.PositiveIntegerField(default=0)
    alexandria_shipping = models.PositiveIntegerField(default=0)
    giza_shipping = models.PositiveIntegerField(default=0)
    qalyubia_shipping = models.PositiveIntegerField(default=0)
    port_said_shipping = models.PositiveIntegerField(default=0)
    suez_shipping = models.PositiveIntegerField(default=0)
    dakahlia_shipping = models.PositiveIntegerField(default=0)
    sharkia_shipping = models.PositiveIntegerField(default=0)
    monufia_shipping = models.PositiveIntegerField(default=0)
    gharbia_shipping = models.PositiveIntegerField(default=0)
    kafr_sheikh_shipping = models.PositiveIntegerField(default=0)
    beheira_shipping = models.PositiveIntegerField(default=0)
    ismailia_shipping = models.PositiveIntegerField(default=0)
    benisuef_shipping = models.PositiveIntegerField(default=0)
    fayoum_shipping = models.PositiveIntegerField(default=0)
    minya_shipping = models.PositiveIntegerField(default=0)
    assiut_shipping = models.PositiveIntegerField(default=0)
    sohag_shipping = models.PositiveIntegerField(default=0)
    qena_shipping = models.PositiveIntegerField(default=0)
    luxor_shipping = models.PositiveIntegerField(default=0)
    aswan_shipping = models.PositiveIntegerField(default=0)
    red_sea_shipping = models.PositiveIntegerField(default=0)
    new_valley_shipping = models.PositiveIntegerField(default=0)
    matruh_shipping = models.PositiveIntegerField(default=0)
    north_sinai_shipping = models.PositiveIntegerField(default=0)
    south_sinai_shipping = models.PositiveIntegerField(default=0)

