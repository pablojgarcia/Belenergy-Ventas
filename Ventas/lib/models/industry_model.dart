class IndustryOption {
  final String name;
  final String sellerType;

  const IndustryOption({required this.name, required this.sellerType});

  factory IndustryOption.fromJson(Map<String, dynamic> json) {
    return IndustryOption(
      name: json['name'] as String? ?? '',
      sellerType: json['seller_type'] as String? ?? '',
    );
  }
}

class IndustryOptions {
  final bool showSelector;
  final List<IndustryOption> industries;

  const IndustryOptions({required this.showSelector, required this.industries});

  factory IndustryOptions.fromJson(Map<String, dynamic> json) {
    final raw = json['industries'];
    return IndustryOptions(
      showSelector: json['show_selector'] as bool? ?? false,
      industries: raw is List
          ? raw
              .whereType<Map>()
              .map((e) => IndustryOption.fromJson(Map<String, dynamic>.from(e)))
              .toList()
          : const [],
    );
  }
}
