from django.db import models
from django.contrib.auth.models import User

# Entrada do tempo de tela do usuário
class ScreenTimeEntry(models.Model):
    CATEGORY_CHOICES = [
        ('PROD', 'Produtivo'),
        ('NAO_PROD', 'Não Produtivo'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    minutes = models.PositiveIntegerField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    note = models.TextField(blank=True, null=True)

    # Classe interna 
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Registro de tempo"
        verbose_name_plural = "Registros de tempo"

    def __str__(self):
        return f"{self.user.username} - {self.minutes} min ({self.get_category_display()})"
