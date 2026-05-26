import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/client_model.dart';
import '../utils/theme.dart';

class CrearPresupuestoScreen extends StatefulWidget {
  final Client client;

  const CrearPresupuestoScreen({super.key, required this.client});

  @override
  State<CrearPresupuestoScreen> createState() => _CrearPresupuestoScreenState();
}

class _CrearPresupuestoScreenState extends State<CrearPresupuestoScreen> {
  final _formKey = GlobalKey<FormState>();
  final _projectController = TextEditingController();
  final _amountController = TextEditingController();

  @override
  void dispose() {
    _projectController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Presupuesto creado para ${widget.client.name}'),
        behavior: SnackBarBehavior.floating,
        backgroundColor: AppColors.primary,
      ),
    );
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Crear presupuesto', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.client.name,
              style: GoogleFonts.inter(
                fontSize: 22,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              widget.client.company,
              style: GoogleFonts.inter(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Detalle del presupuesto',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _projectController,
                    decoration: const InputDecoration(
                      labelText: 'Descripción del proyecto',
                      hintText: 'Ej. instalación solar residencial',
                    ),
                    maxLines: 3,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Ingresá una descripción';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _amountController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Monto estimado',
                      hintText: 'Ej. 2850000',
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Ingresá el valor del presupuesto';
                      }
                      if (double.tryParse(value.replaceAll(',', '.')) == null) {
                        return 'Valor inválido';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 28),
                  ElevatedButton(
                    onPressed: _submit,
                    child: const Text('Generar presupuesto'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
