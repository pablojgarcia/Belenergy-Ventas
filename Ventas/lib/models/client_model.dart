class Client {
  final int id;
  final String name;
  final String company;
  final String email;
  final String phone;
  final String address;
  final String? salespersonEmail;

  Client({
    required this.id,
    required this.name,
    this.company = '',
    this.email = '',
    this.phone = '',
    this.address = '',
    this.salespersonEmail,
  });

  factory Client.fromJson(Map<String, dynamic> json) {
    return Client(
      id: json['odoo_id'] ?? 0,
      name: json['name'] ?? '',
      company: json['vat'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      address: [
        json['street'],
        json['city'],
        json['state'],
        json['country']
      ].where((e) => e != null && e.toString().isNotEmpty).join(', '),
      salespersonEmail: json['salesperson_id'],
    );
  }

  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }

  int get odooId => id;

  static List<Client> sampleClients() => [];
}
