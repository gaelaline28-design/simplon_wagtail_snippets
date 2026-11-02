from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from wagtail.images.models import Image #pour mettre le portrait dans le snippet coach

# Définition des choix (la première valeur est stockée en base, la seconde est affichée dans l'admin)
# 1. Définissions des choix
SPORT_CHOICES = [
    ('', '--- Choisissez un sport ---'), # Option vide ou textuelle par défaut
    ('fitness', 'Fitness'),
    ('zumba', 'Zumba'),
    ('pilate', 'Pilate'),
    ('caoch', 'Caoch'),
]

@register_snippet # je déclare mon DECORATEUR snippet
class Coachs(models.Model):
        # défini le contenu de mon model
    nomcoach = models.CharField(max_length=30)
    datearriver = models.DateField (null=True, blank=True)
    sport = models.CharField(
        max_length=50,
        choices=SPORT_CHOICES,
        default="",     # Valeur par défaut optionnelle
        blank=True,
        null=True
    )
    photo = models.ForeignKey(
        'wagtailimages.Image',  # Lien vers la bibliothèque d'images Wagtail
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image de la section L'équipe"
    )
    description = models.TextField(blank=True)

    panels = [
            FieldPanel("nomcoach"),
            FieldPanel("datearriver"),
            FieldPanel("sport"),
            FieldPanel("photo"),
            FieldPanel("description")
    ]
    
        # donne la valeur dans ma variable "nom", aux snippets qu'on va créer
    def __str__(self):
        return self.nomcoach


class CoachsPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context["coachs_list"] = Coachs.objects.all()
        return context

# -------------------------------------------------------------------------------

@register_snippet # je déclare mon DECORATEUR snippet
class Cours(models.Model):
    # défini le contenu de mon model
    nom = models.CharField(max_length=100)
    horaire = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("nom"),
        FieldPanel("horaire"),
        FieldPanel("niveau"),
        FieldPanel("description")
        # liste les champs visibles dans le form admin de ce snippet
        # panels et pas content panel parcequ'un snippet n'est pas une page -> ça exclu donc le slug, le btn publié etc
    ]

    # donne la valeur dans ma variable "nom", aux snippets qu'on va créer
    def __str__(self):
        return self.nom


class CoursPage(Page):
    def get_context(self, request):
        # get context permet de construire les données envoyées à cette page
        context = super().get_context(request)
        context["cours_list"] = Cours.objects.all()
        return context

# -------------------------------------------------------------------------------

class ContactPage(Page):
    pass
