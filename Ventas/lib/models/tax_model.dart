class Tax {
  final int id;
  final int odooId;
  final String name;
  final double amount;
  final String typeTaxUse;

  Tax({
    required this.id,
    required this.odooId,
    required this.name,
    this.amount = 0.0,
    this.typeTaxUse = 'sale',
  });

  factory Tax.fromJson(Map<String, dynamic> json) {
    return Tax(
      id: json['id'] ?? 0,
      odooId: json['odoo_id'] ?? 0,
      name: json['name'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      typeTaxUse: json['type_tax_use'] ?? 'sale',
    );
  }

  String get displayLabel {
    if (name.isNotEmpty) return name;
    if (amount > 0) return '${amount}%';
    return 'IVA';
  }
}
