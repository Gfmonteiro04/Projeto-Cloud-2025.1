from django.db import models

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