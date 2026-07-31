import 'dart:convert';

class TermsAndConditions {
  final String id;
  final String name;
  final String content;
  final bool isDefault;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  TermsAndConditions({
    required this.id,
    required this.name,
    required this.content,
    this.isDefault = false,
    this.isActive = true,
    required this.createdAt,
    this.updatedAt,
  });

  factory TermsAndConditions.fromJson(Map<String, dynamic> json) {
    DateTime parseDateTime(String? value) {
      if (value == null) return DateTime.now();
      try {
        return DateTime.parse(value);
      } catch (_) {
        return DateTime.now();
      }
    }

    return TermsAndConditions(
      id: json['id'] as String,
      name: json['name'] as String? ?? '',
      content: json['content'] as String? ?? '',
      isDefault: json['is_default'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: parseDateTime(json['created_at'] as String?),
      updatedAt: json['updated_at'] != null
          ? parseDateTime(json['updated_at'] as String?)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'content': content,
      'is_default': isDefault,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}