class DiscountRule {
  final String id;
  final String sellerType;
  final String? productLineId;
  final String? productLineKey;
  final String? productLineName;
  final String conditionType;
  final double? minValue;
  final double? maxValue;
  final double? maxDiscount;
  final int priority;
  final bool isActive;

  const DiscountRule({
    required this.id,
    required this.sellerType,
    this.productLineId,
    this.productLineKey,
    this.productLineName,
    required this.conditionType,
    this.minValue,
    this.maxValue,
    this.maxDiscount,
    this.priority = 0,
    this.isActive = true,
  });

  factory DiscountRule.fromJson(Map<String, dynamic> json) {
    return DiscountRule(
      id: json['id'] as String,
      sellerType: json['seller_type'] as String? ?? '',
      productLineId: json['product_line_id'] as String?,
      productLineKey: json['product_line_key'] as String?,
      productLineName: json['product_line_name'] as String?,
      conditionType: json['condition_type'] as String? ?? '',
      minValue: (json['min_value'] as num?)?.toDouble(),
      maxValue: (json['max_value'] as num?)?.toDouble(),
      maxDiscount: (json['max_discount'] as num?)?.toDouble(),
      priority: json['priority'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'seller_type': sellerType,
      'product_line_id': productLineId,
      'product_line_key': productLineKey,
      'product_line_name': productLineName,
      'condition_type': conditionType,
      'min_value': minValue,
      'max_value': maxValue,
      'max_discount': maxDiscount,
      'priority': priority,
      'is_active': isActive,
    };
  }
}

class DiscountBand {
  final String key;
  final String label;
  final String conditionType;
  final double? min;
  final double? max;

  const DiscountBand({
    required this.key,
    required this.label,
    required this.conditionType,
    this.min,
    this.max,
  });

  factory DiscountBand.fromJson(Map<String, dynamic> json) {
    return DiscountBand(
      key: json['key'] as String? ?? '',
      label: json['label'] as String? ?? '',
      conditionType: json['condition_type'] as String? ?? '',
      min: (json['min'] as num?)?.toDouble(),
      max: (json['max'] as num?)?.toDouble(),
    );
  }
}
