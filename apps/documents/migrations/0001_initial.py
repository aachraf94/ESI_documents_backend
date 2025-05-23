# Generated by Django 5.0.13 on 2025-05-18 16:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50, verbose_name="Prénom")),
                ("last_name", models.CharField(max_length=50, verbose_name="Nom")),
                ("date_naissance", models.DateField(verbose_name="Date de naissance")),
                (
                    "lieu_naissance",
                    models.CharField(max_length=100, verbose_name="Lieu de naissance"),
                ),
                ("grade", models.CharField(max_length=100, verbose_name="Grade")),
                ("fonction", models.CharField(max_length=100, verbose_name="Fonction")),
                (
                    "categorie",
                    models.CharField(
                        choices=[
                            ("ENSEIGNANT", "Enseignant/Chercheur"),
                            ("ADMINISTRATIF", "Administratif"),
                            ("TECHNIQUE", "Technique"),
                            ("OUVRIER", "Ouvrier professionnel"),
                        ],
                        default="ADMINISTRATIF",
                        max_length=20,
                        verbose_name="Catégorie",
                    ),
                ),
                ("date_embauche", models.DateField(verbose_name="Date d'embauche")),
                (
                    "date_depart",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de départ"
                    ),
                ),
                (
                    "service",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Service/Département"
                    ),
                ),
                (
                    "statut_emploi",
                    models.CharField(
                        choices=[
                            ("ACTIF", "Actif"),
                            ("DEMISSION", "Démission"),
                            ("RETRAITE", "Retraite"),
                        ],
                        default="ACTIF",
                        max_length=10,
                        verbose_name="Statut d'emploi",
                    ),
                ),
                (
                    "num_piece_identite",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Numéro de pièce d'identité",
                    ),
                ),
                (
                    "date_emission_piece",
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name="Date d'émission de la pièce d'identité",
                    ),
                ),
                (
                    "lieu_emission_piece",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="Lieu d'émission de la pièce d'identité",
                    ),
                ),
            ],
            options={
                "verbose_name": "Employé",
                "verbose_name_plural": "Employés",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="AttestationTravail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reference",
                    models.CharField(max_length=50, verbose_name="Référence"),
                ),
                (
                    "date_emission",
                    models.DateField(auto_now_add=True, verbose_name="Date d'émission"),
                ),
                (
                    "emetteur",
                    models.CharField(
                        default="Directeur de l'École Nationale Supérieure d'Informatique",
                        max_length=100,
                        verbose_name="Émetteur",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attestations",
                        to="documents.employee",
                        verbose_name="Employé",
                    ),
                ),
            ],
            options={
                "verbose_name": "Attestation de travail",
                "verbose_name_plural": "Attestations de travail",
                "ordering": ["-date_emission"],
            },
        ),
        migrations.CreateModel(
            name="OrdreMission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reference",
                    models.CharField(max_length=50, verbose_name="Numéro de référence"),
                ),
                (
                    "objet_mission",
                    models.TextField(
                        max_length=500, verbose_name="Objet de la mission"
                    ),
                ),
                (
                    "lieu_depart",
                    models.CharField(
                        default="Alger", max_length=100, verbose_name="Lieu de départ"
                    ),
                ),
                (
                    "lieu_destination",
                    models.CharField(
                        max_length=100, verbose_name="Lieu de destination"
                    ),
                ),
                (
                    "date_depart",
                    models.DateTimeField(verbose_name="Date et heure de départ"),
                ),
                (
                    "date_retour",
                    models.DateTimeField(verbose_name="Date et heure de retour"),
                ),
                (
                    "moyen_transport",
                    models.CharField(
                        choices=[
                            ("VOITURE", "Voiture de service"),
                            ("VOITURE_PERSONNELLE", "Voiture personnelle"),
                            ("AVION", "Avion"),
                            ("TRAIN", "Train"),
                            ("TRANSPORT_COMMUN", "Transport en commun"),
                            ("AUTRE", "Autre"),
                        ],
                        max_length=30,
                        verbose_name="Moyen de transport",
                    ),
                ),
                (
                    "avance",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Montant de l'avance",
                    ),
                ),
                (
                    "numero_avance",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Numéro du relevé d'avance",
                    ),
                ),
                (
                    "date_avance",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de l'avance"
                    ),
                ),
                (
                    "lieu_avance",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Lieu de l'avance"
                    ),
                ),
                (
                    "nuits_hebergement",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Nombre de nuits d'hébergement"
                    ),
                ),
                (
                    "duree_mission_jours",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Durée en jours"
                    ),
                ),
                (
                    "duree_mission_heures",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Durée en heures"
                    ),
                ),
                (
                    "date_creation",
                    models.DateField(
                        auto_now_add=True, verbose_name="Date de création"
                    ),
                ),
                (
                    "responsable_emission",
                    models.CharField(
                        max_length=100, verbose_name="Responsable émetteur"
                    ),
                ),
                (
                    "missionnaire",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="missions",
                        to="documents.employee",
                        verbose_name="Missionnaire",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ordre de mission",
                "verbose_name_plural": "Ordres de mission",
                "ordering": ["-date_creation"],
            },
        ),
        migrations.CreateModel(
            name="EtapeMission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "lieu_depart",
                    models.CharField(max_length=100, verbose_name="Lieu de départ"),
                ),
                (
                    "lieu_arrivee",
                    models.CharField(max_length=100, verbose_name="Lieu d'arrivée"),
                ),
                (
                    "date_depart",
                    models.DateTimeField(verbose_name="Date et heure de départ"),
                ),
                (
                    "date_arrivee",
                    models.DateTimeField(verbose_name="Date et heure d'arrivée"),
                ),
                (
                    "moyen_transport",
                    models.CharField(max_length=30, verbose_name="Moyen de transport"),
                ),
                (
                    "ordre_mission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="etapes",
                        to="documents.ordremission",
                        verbose_name="Ordre de mission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Étape de mission",
                "verbose_name_plural": "Étapes de mission",
                "ordering": ["date_depart"],
            },
        ),
    ]
