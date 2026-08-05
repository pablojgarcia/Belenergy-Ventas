import 'dart:convert';

class DiscountRuleResult {
  final int lineIndex;
  final String productName;
  final String? productLineKey;
  final double? maxDiscount;
  final bool requiresApproval;
  final String? tier;
  final String? message;

  DiscountRuleResult({
    required this.lineIndex,
    required this.productName,
    this.productLineKey,
    this.maxDiscount,
    this.requiresApproval = false,
    this.tier,
    this.message,
  });

  factory DiscountRuleResult.fromJson(Map<String, dynamic> json) {
    return DiscountRuleResult(
      lineIndex: json['line_index'] as int? ?? 0,
      productName: json['product_name'] as String? ?? '',
      productLineKey: json['product_line_key'] as String?,
      maxDiscount: json['max_discount'] != null
          ? (json['max_discount'] as num).toDouble()
          : null,
      requiresApproval: json['requires_approval'] as bool? ?? false,
      tier: json['tier'] as String?,
      message: json['message'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'line_index': lineIndex,
      'product_name': productName,
      'product_line_key': productLineKey,
      'max_discount': maxDiscount,
      'requires_approval': requiresApproval,
      'tier': tier,
      'message': message,
    };
  }
}