from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

#(ici, les champs du formulaire appartiennent a une page Contact precise)
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField


#pour mettre le portrait dans le snippet coach
from wagtail.images.models import Image 

# -------------------------------------------------------------------------------

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
class Cours(models.Model):  #il dit à Wagtail "ce modèle doit apparaître dans l'admin, avec son propre formulaire"

    # défini le contenu de mon model
    nom = models.CharField(max_length=100)
    horaire = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Liste des champs visibles dans le formulaire d'admin de CE Snippet.
    # On écrit "panels" et non "content_panels" : un Snippet n'est pas une Page,
    # il n'a donc pas de titre de page, de slug, de bouton "publier"... juste ses propres champs.
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

class FormField(AbstractFormField):
    # AbstractFormField fournit deja tout ce qu'il faut pour decrire UN champ
    # quelconque (label, type de champ, obligatoire ou non...). On ajoute juste
    # le lien vers la page Contact. Les vrais champs (Nom, Email, Message) ne sont
    # PAS ecrits ici : ils seront crees comme des donnees, depuis l'admin (etape 5).
    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,   # si la page Contact est supprimee, ses champs le sont aussi
        related_name="form_fields",
    )

# -------------------------------------------------------------------------------
    # On remplace Page par AbstractEmailForm : ContactPage reste une page (AbstractEmailForm herite de Page), mais une page qui sait aussi envoyer un email a chaque reponse.
class ContactPage(AbstractEmailForm):
    
    intro = RichTextField(blank=True)          # texte affiche au-dessus du formulaire
    thankyoutext = RichTextField(blank=True)  # message affiche apres l'envoi
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),

        # InlinePanel : widget d'admin qui affiche la liste des FormField de cette page, avec un bouton pour en ajouter, en retirer, ou changer leur ordre
        InlinePanel("form_fields", label="Champs du formulaire"),

        FieldPanel("thankyoutext"),
        FieldPanel("to_address"),    # l'email de Max, qui recevra chaque message
        FieldPanel("from_address"),  # l'adresse "expediteur" affichee sur l'email recu
        FieldPanel("subject"),       # le sujet de l'email envoye
    ]

# -------------------------------------------------------------------------------

class CoachsIndexPage(Page):

    #je créé une variable
    intro = RichTextField(blank=True)

    #Permet d'envoyer la variable
    content_panels = Page.content_panels + [
        FieldPanel("intro")
    ] 

    #sous cette page on ne pourras ajouter que des fiches de coach evite de se tromper par erreur dans l'admin
    subpage_type = ["Pages.CoachProfilPage"]

    #va contenir des fiche coach enfant et quand on l'affiche, va les chercher pour les afficher

    def get_context(self, request):

        # child_of(self) : va chercher uniquement les pages enfants de CETTE page .live(): seulement celles qui sont publiees
        contex = super().get_context(request)
        contex ["coachs"] = CoachProfilPage.objects.child_of(self).live()

        return contex

class CoachProfilPage (Page):

    specialite = models.CharField(max_length=100, blank=True)
    nom =  models.CharField(max_length=10, blank=True)
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    bio = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("specialite"),
        FieldPanel("nom"),
        FieldPanel("photo"),
        FieldPanel("bio"),
    ]

    # inverse de subpage_types : dit a Wagtail que cette page ne peut etre creee que sous une page "Notre equipe"
    parent_page_types = ["pages.CoachsIndexPage"]

# -------------------------------------------------------------------------------

