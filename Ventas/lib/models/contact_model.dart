class Contact {
  final int id;
  final int customerId;
  final String name;
  final String email;
  final String phone;

  Contact({
    required this.id,
    required this.customerId,
    required this.name,
    this.email = '',
    this.phone = '',
  });

  factory Contact.fromJson(Map<String, dynamic> json) {
    return Contact(
      id: json['id'] ?? 0,
      customerId: json['customer_id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
    );
  }
}
