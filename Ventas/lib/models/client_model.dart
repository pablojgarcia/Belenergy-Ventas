class Client {
  final int id;
  final int odooId;
  final String name;
  final String companyName;
  final String vat;
  final String cuit;
  final String vendedorInterno;
  final String email;
  final String phone;
  final String mobile;
  final String street;
  final String city;
  final String state;
  final String zipCode;
  final String country;
  final String website;
  final String? salespersonEmail;

  Client({
    required this.id,
    required this.odooId,
    required this.name,
    this.companyName = '',
    this.vat = '',
    this.cuit = '',
    this.vendedorInterno = '',
    this.email = '',
    this.phone = '',
    this.mobile = '',
    this.street = '',
    this.city = '',
    this.state = '',
    this.zipCode = '',
    this.country = '',
    this.website = '',
    this.salespersonEmail,
  });

  factory Client.fromJson(Map<String, dynamic> json) {
    return Client(
      id: json['id'] ?? 0,
      odooId: json['odoo_id'] ?? 0,
      name: json['name'] ?? '',
      companyName: json['company_name'] ?? '',
      vat: json['vat'] ?? '',
      cuit: json['cuit'] ?? '',
      vendedorInterno: json['vendedor_interno'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      mobile: json['mobile'] ?? '',
      street: json['street'] ?? '',
      city: json['city'] ?? '',
      state: json['state'] ?? '',
      zipCode: json['zip'] ?? '',
      country: json['country'] ?? '',
      website: json['website'] ?? '',
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

  String get address {
    return [
      street,
      city,
      state,
      country,
    ].where((e) => e.isNotEmpty).join(', ');
  }
}
