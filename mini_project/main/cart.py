# class Cart:
#     def __init__(self, request):
#         self.cart = {}
#         self.request = request

#     def add_item(self, product, quantity):
#         if product.id in self.cart:
#             self.cart[product.id]['quantity'] += quantity
#         else:
#             self.cart[product.id] = {'quantity': quantity, 'product': product}

#     def remove_item(self, product_id):
#         if product_id in self.cart:
#             del self.cart[product_id]

#     def get_cart_items(self):
#         return self.cart.values()

#     def clear_cart(self):
#         self.cart = {}
