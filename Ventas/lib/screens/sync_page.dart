import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';

class SyncPage extends StatefulWidget {
  const SyncPage({super.key});

  @override
  State<SyncPage> createState() => _SyncPageState();
}

class _SyncTarget {
  final String type;
  final String label;
  final IconData icon;

  const _SyncTarget(this.type, this.label, this.icon);
}

const _targets = [
  _SyncTarget('customers', 'Clientes', Icons.people_alt_rounded),
  _SyncTarget('products', 'Productos', Icons.solar_power_rounded),
  _SyncTarget('taxes', 'Impuestos', Icons.percent_rounded),
];

class _SyncPageState extends State<SyncPage> {
  final Map<String, SyncStatus> _status = {};
  final Map<String, bool> _wasRunning = {};
  Timer? _timer;
  bool _triggering = false;
  String? _triggeredType;

  @override
  void initState() {
    super.initState();
    _refresh();
    _timer = Timer.periodic(const Duration(seconds: 2), (_) => _refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _refresh() async {
    final api = context.read<ApiService>();
    final results = await Future.wait(_targets.map((t) async {
      try {
        return await api.syncStatus(t.type);
      } catch (_) {
        return null;
      }
    }));
    if (!mounted) return;
    setState(() {
      for (var i = 0; i < _targets.length; i++) {
        final target = _targets[i];
        final status = results[i];
        if (status == null) continue;
        final wasRunning = _wasRunning[target.type] ?? false;
        if (wasRunning && !status.isRunning) {
          api.listsRefreshNotifier.value++;
        }
        _wasRunning[target.type] = status.isRunning;
        _status[target.type] = status;
      }
    });
  }

  Future<void> _trigger(_SyncTarget target) async {
    setState(() {
      _triggering = true;
      _triggeredType = target.type;
    });
    try {
      await context.read<ApiService>().triggerSync(target.type);
    } catch (e) {
      if (!mounted) return;
      final msg = e is DioException
          ? ((e.response?.data as Map?)?['detail'] ?? 'Error de conexión').toString()
          : 'No se pudo iniciar la sincronización';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) {
        setState(() {
          _triggering = false;
          _triggeredType = null;
        });
      }
      _refresh();
    }
  }

  String _stageLabel(SyncStatus? s) {
    if (s == null) return 'Sin ejecuciones previas';
    switch (s.status) {
      case 'running':
        return _stageName(s.stage) ?? 'Sincronizando...';
      case 'completed':
        return 'Completado';
      case 'failed':
        return 'Falló';
      default:
        return _stageName(s.stage) ?? 'Sin ejecuciones previas';
    }
  }

  String? _stageName(String? stage) {
    switch (stage) {
      case 'descargando':
        return 'Descargando datos...';
      case 'contactos':
        return 'Sincronizando contactos...';
      case 'guardado':
        return 'Guardando en la base de datos...';
      case 'fallido':
        return 'Falló durante la ejecución';
      default:
        return stage;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Sincronización', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.primary,
        elevation: 0,
      ),
      backgroundColor: const Color(0xFFF7F8FA),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'Los datos se sincronizan con Odoo. La primera vez puede tomar unos minutos; luego, solo bajos cambios.',
              style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 16),
            for (final target in _targets) ...[
              _SyncCard(
                target: target,
                status: _status[target.type],
                stageLabel: _stageLabel(_status[target.type]),
                loading: _triggering && _triggeredType == target.type,
                onRun: () => _trigger(target),
              ),
              const SizedBox(height: 12),
            ],
          ],
        ),
      ),
    );
  }
}

class _SyncCard extends StatelessWidget {
  final _SyncTarget target;
  final SyncStatus? status;
  final String stageLabel;
  final bool loading;
  final VoidCallback onRun;

  const _SyncCard({
    required this.target,
    required this.status,
    required this.stageLabel,
    required this.loading,
    required this.onRun,
  });

  @override
  Widget build(BuildContext context) {
    final s = status;
    final isRunning = s?.isRunning ?? false;
    final isFailed = s?.isFailed ?? false;
    final color = isRunning
        ? AppColors.primary
        : isFailed
            ? AppColors.error
            : AppColors.textSecondary;

    final hadProgress = (s?.total ?? 0) > 0;
    final progress = hadProgress
        ? ((s?.processed ?? 0) / s!.total!).clamp(0.0, 1.0).toDouble()
        : 0.0;

    final elapsed = s?.elapsed;
    final finished = s?.finishedAt;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [BoxShadow(color: AppColors.cardShadow, blurRadius: 8)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(target.icon, color: AppColors.primary, size: 24),
              const SizedBox(width: 12),
              Text(target.label,
                  style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600)),
              const Spacer(),
              if (isRunning)
                const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
            ],
          ),
          const SizedBox(height: 12),
          if (s == null)
            Text(stageLabel, style: GoogleFonts.inter(fontSize: 13, color: AppColors.textSecondary))
          else ...[
            Text(stageLabel,
                style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500, color: color)),
            const SizedBox(height: 6),
            Text(
              'Procesados: ${s.processed ?? 0}${hadProgress ? ' de ${s.total}' : ''}'
              '${elapsed != null ? '  |  ${elapsed.toStringAsFixed(1)} s' : ''}',
              style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
            ),
            if (finished != null)
              Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Text('Última: $finished (UTC)',
                    style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary)),
              ),
            if (hadProgress) ...[
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 6,
                  backgroundColor: AppColors.divider,
                  color: color,
                ),
              ),
            ],
            if (isFailed && s.error != null) ...[
              const SizedBox(height: 8),
              Text(s.error!,
                  style: GoogleFonts.inter(fontSize: 12, color: AppColors.error)),
            ],
          ],
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: isRunning || loading ? null : onRun,
              icon: loading
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.sync_rounded, color: AppColors.primary),
              label: Text(isRunning ? 'En curso...' : 'Sincronizar',
                  style: GoogleFonts.inter(color: AppColors.primary)),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size.fromHeight(44),
                side: BorderSide(color: AppColors.primary.withOpacity(0.3)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}