class ProductLine {
  final String id;
  final String key;
  final String name;
  final bool isActive;

  const ProductLine({
    required this.id,
    required this.key,
    required this.name,
    this.isActive = true,
  });

  factory ProductLine.fromJson(Map<String, dynamic> json) {
    return ProductLine(
      id: json['id'] as String,
      key: json['key'] as String? ?? '',
      name: json['name'] as String? ?? '',
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'key': key,
      'name': name,
      'is_active': isActive,
    };
  }
}
