from django.contrib import admin
from .models import Exemplo

@admin.register(Exemplo)
class ExemploAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao', 'quantidade', 'preco')  # Exibe essas colunas no admin