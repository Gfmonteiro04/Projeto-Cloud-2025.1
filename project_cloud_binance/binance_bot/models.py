from django.db import models

class Exemplo(models.Model):
    id = models.AutoField(primary_key=True)  # Chave primária autoincrementada
    nome = models.CharField(max_length=100)  # Campo VARCHAR(100) NOT NULL
    descricao = models.CharField(max_length=255, blank=True, null=True)  # Campo VARCHAR(255), pode ser NULL
    quantidade = models.IntegerField()  # Campo INT NOT NULL
    preco = models.FloatField()  # Campo FLOAT NOT NULL

    class Meta:
        managed = False  # O Django NÃO tentará criar ou modificar a tabela
        db_table = 'exemplo'  # Nome real da tabela no banco de dados
