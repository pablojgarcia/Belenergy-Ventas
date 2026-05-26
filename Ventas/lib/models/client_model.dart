class Client {
  final int id;
  final String name;
  final String company;
  final String email;
  final String phone;
  final String address;

  Client({
    required this.id,
    required this.name,
    required this.company,
    required this.email,
    required this.phone,
    required this.address,
  });

  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }

  static List<Client> sampleClients() {
    return [
      Client(
        id: 1,
        name: 'Lucía Pereyra',
        company: 'Energía Verde SA',
        email: 'lucia.pereyra@energias.com',
        phone: '+54 9 11 3456 7890',
        address: 'Av. Corrientes 1234, CABA',
      ),
      Client(
        id: 2,
        name: 'Martín Gómez',
        company: 'Soluciones Renovables',
        email: 'martin.gomez@renovables.com',
        phone: '+54 9 11 5566 7788',
        address: 'Calle Florida 234, Córdoba',
      ),
      Client(
        id: 3,
        name: 'Sofía Ramírez',
        company: 'Construcciones del Sur',
        email: 'sofia.ramirez@cds.com.ar',
        phone: '+54 9 11 6677 8899',
        address: 'Ruta 3 KM 22, Buenos Aires',
      ),
      Client(
        id: 4,
        name: 'Diego Villalba',
        company: 'Grupo Solar Norte',
        email: 'diego.villalba@gsn.com.ar',
        phone: '+54 9 11 9988 7766',
        address: 'Av. Santa Fe 567, Rosario',
      ),
    ];
  }
}
