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

class TradeOrder(models.Model):
    ORDER_TYPE_CHOICES = (
        ('BUY', 'Compra'),
        ('SELL', 'Venda'),
    )

    symbol = models.CharField(max_length=10)  # Ex: 'BTCUSDT', 'ETHUSDT'
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=50)
    executed_qty = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.symbol} - {self.order_type} - {self.status}'