import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class MyCustomersScreen extends StatefulWidget {
  const MyCustomersScreen({super.key});

  @override
  State<MyCustomersScreen> createState() => _MyCustomersScreenState();
}

class _MyCustomersScreenState extends State<MyCustomersScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic> _customers = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchCustomers();
  }

  Future<void> _fetchCustomers() async {
    try {
      final response = await _apiService.dio.get('/customers');
      final userResponse = await _apiService.dio.get('/auth/me');
      final currentUserEmail = userResponse.data['email'];

      setState(() {
        // Filtramos en memoria: clientes cuyo salesperson_id coincide con el email del usuario logueado
        _customers = (response.data as List).where((c) => c['salesperson_id'] == currentUserEmail).toList();
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error fetching customers: $e');
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Mis Clientes', style: GoogleFonts.inter())),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _customers.isEmpty
              ? const Center(child: Text('No tienes clientes asignados.'))
              : ListView.builder(
                  itemCount: _customers.length,
                  itemBuilder: (context, index) {
                    final customer = _customers[index];
                    return ListTile(
                      title: Text(customer['name']),
                      subtitle: Text('Vendedor: ${customer['salesperson_id'] ?? "Sin vendedor"}'),
                    );
                  },
                ),
    );
  }
}
