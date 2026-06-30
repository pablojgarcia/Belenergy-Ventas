class Lead {
  final String id;
  final String companyName;
  final String? contactName;
  final String? email;
  final String? phone;
  final String? mobile;
  final String? street;
  final String? city;
  final String? state;
  final String? zip;
  final String? country;
  final String? vat;
  final String? notes;
  final String status;
  final String? rejectionReason;
  final int createdBy;
  final int? reviewedBy;
  final DateTime? reviewedAt;
  final int? odooPartnerId;
  final int? odooCrmLeadId;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int version;

  Lead({
    required this.id,
    required this.companyName,
    this.contactName,
    this.email,
    this.phone,
    this.mobile,
    this.street,
    this.city,
    this.state,
    this.zip,
    this.country,
    this.vat,
    this.notes,
    required this.status,
    this.rejectionReason,
    required this.createdBy,
    this.reviewedBy,
    this.reviewedAt,
    this.odooPartnerId,
    this.odooCrmLeadId,
    required this.createdAt,
    this.updatedAt,
    required this.version,
  });

  factory Lead.fromJson(Map<String, dynamic> json) {
    return Lead(
      id: json['id'] ?? '',
      companyName: json['company_name'] ?? '',
      contactName: json['contact_name'],
      email: json['email'],
      phone: json['phone'],
      mobile: json['mobile'],
      street: json['street'],
      city: json['city'],
      state: json['state'],
      zip: json['zip'],
      country: json['country'],
      vat: json['vat'],
      notes: json['notes'],
      status: json['status'] ?? 'pendiente',
      rejectionReason: json['rejection_reason'],
      createdBy: json['created_by'] ?? 0,
      reviewedBy: json['reviewed_by'],
      reviewedAt: json['reviewed_at'] != null
          ? DateTime.tryParse(json['reviewed_at'])
          : null,
      odooPartnerId: json['odoo_partner_id'],
      odooCrmLeadId: json['odoo_crm_lead_id'],
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'])
          : null,
      version: json['version'] ?? 1,
    );
  }

  String get statusLabel {
    switch (status) {
      case 'pendiente':
        return 'Pendiente';
      case 'aprobado':
        return 'Aprobado';
      case 'rechazado':
        return 'Rechazado';
      case 'sincronizado':
        return 'Sincronizado';
      default:
        return status;
    }
  }
}
