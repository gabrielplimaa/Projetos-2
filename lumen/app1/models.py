from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Categoria(models.Model):
    sugestao = models.CharField(max_length=100, verbose_name="categoria")


    def __str__(self):
        return self.sugestao

class Artigos(models.Model):
    titulo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo
#primeira hist
class Sugestao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="suggested_readings")
    article = models.ForeignKey(Artigos, on_delete=models.CASCADE, related_name="suggestions_for")
    suggested_article = models.ForeignKey(Artigos, on_delete=models.CASCADE, related_name="suggested_in")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "suggested_article", "user")

    def __str__(self):
        if self.user:
            return f"Sugestão para {self.user.username}: {self.suggested_article.title}"
        return f"Sugestão: {self.suggested_article.title}"
