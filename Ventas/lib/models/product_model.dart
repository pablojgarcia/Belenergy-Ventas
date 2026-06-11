class Product {
  final int id;
  final int odooId;
  final String name;
  final String defaultCode;
  final String barcode;
  final double listPrice;
  final double standardPrice;
  final String type;
  final String categId;
  final String uomId;
  final String descriptionSale;
  final bool active;
  final bool saleOk;

  Product({
    required this.id,
    required this.odooId,
    required this.name,
    this.defaultCode = '',
    this.barcode = '',
    this.listPrice = 0.0,
    this.standardPrice = 0.0,
    this.type = 'product',
    this.categId = '',
    this.uomId = '',
    this.descriptionSale = '',
    this.active = true,
    this.saleOk = true,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      odooId: json['odoo_id'] ?? 0,
      name: json['name'] ?? '',
      defaultCode: json['default_code'] ?? '',
      barcode: json['barcode'] ?? '',
      listPrice: (json['list_price'] ?? 0.0).toDouble(),
      standardPrice: (json['standard_price'] ?? 0.0).toDouble(),
      type: json['type'] ?? 'product',
      categId: json['categ_id'] ?? '',
      uomId: json['uom_id'] ?? '',
      descriptionSale: json['description_sale'] ?? '',
      active: json['active'] ?? true,
      saleOk: json['sale_ok'] ?? true,
    );
  }

  String get formattedPrice {
    return '\$${listPrice.toStringAsFixed(2)}';
  }
}
