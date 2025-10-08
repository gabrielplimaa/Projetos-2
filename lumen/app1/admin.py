from django.contrib import admin
from .models import Artigos, Sugestao, Progresso, Progresso_diario
# Register your models here.
admin.site.register(Artigos)
admin.site.register(Sugestao)
admin.site.register(Progresso)
admin.site.register(Progresso_diario)