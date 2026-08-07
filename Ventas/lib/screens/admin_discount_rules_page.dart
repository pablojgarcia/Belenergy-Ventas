import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../models/discount_rule_model.dart';
import '../models/product_line_model.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../services/api_service.dart';
import '../widgets/app_table.dart';

const _sellerOptions = [
  ('', 'Todos'),
  ('vendedor_interno', 'Vendedor interno'),
  ('representante_general', 'Representante general'),
  ('representante_agro', 'Representante agro'),
];

const _panelLines = {'paneles_ja', 'paneles_astro_575', 'paneles_astro_615'};

String _sellerLabel(String s) {
  for (final (v, l) in _sellerOptions) {
    if (v == s) return l;
  }
  return s;
}

String _conditionLabel(String c) => c == 'qty' ? 'Cantidad' : 'Monto';

String _fmtNum(double v) =>
    v == v.roundToDouble() ? '${v.round()}' : v.toStringAsFixed(2);

String _fmtPct(double v) =>
    v == v.roundToDouble() ? '${v.round()}%' : '${v.toStringAsFixed(1)}%';

String _rangeText(DiscountRule r) {
  final min = r.minValue;
  final max = r.maxValue;
  if (min != null && max != null) return '${_fmtNum(min)} – ${_fmtNum(max)}';
  if (min != null) return '>= ${_fmtNum(min)}';
  if (max != null) return '< ${_fmtNum(max)}';
  return '—';
}

String? _bandKeyFor(double? min, double? max, List<DiscountBand> bands) {
  for (final b in bands) {
    final bMin = b.min;
    final bMax = b.max;
    final sameMin = (bMin == null && min == null) ||
        (bMin != null && min != null && (bMin - min).abs() < 0.01);
    final sameMax = (bMax == null && max == null) ||
        (bMax != null && max != null && (bMax - max).abs() < 0.01);
    if (sameMin && sameMax) return b.key;
  }
  return null;
}

String _suggestedCondition(ProductLine? line) =>
    (line != null && _panelLines.contains(line.key)) ? 'qty' : 'amount';

class AdminDiscountRulesPage extends StatefulWidget {
  const AdminDiscountRulesPage({super.key});

  @override
  State<AdminDiscountRulesPage> createState() => _AdminDiscountRulesPageState();
}

class _AdminDiscountRulesPageState extends State<AdminDiscountRulesPage> {
  List<DiscountRule> _rules = [];
  List<ProductLine> _lines = [];
  List<DiscountBand> _bands = [];
  bool _loading = true;
  String? _error;
  String _sellerFilter = '';
  String _lineFilter = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    final api = context.read<ApiService>();
    try {
      final rulesData = await api.getDiscountRules(
        sellerType: _sellerFilter.isEmpty ? null : _sellerFilter,
        productLineId: _lineFilter.isEmpty ? null : _lineFilter,
      );
      final linesData = await api.getProductLines();
      final bandsData = await api.getDiscountBands();
      if (!mounted) return;
      setState(() {
        _rules = rulesData.map(DiscountRule.fromJson).toList();
        _lines = linesData.map(ProductLine.fromJson).toList();
        _bands = bandsData.map(DiscountBand.fromJson).toList();
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Error al cargar los datos';
        _loading = false;
      });
    }
  }

  Future<void> _run(Future<bool> Function() action) async {
    try {
      final changed = await action();
      if (mounted && changed) _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          title: Text('Motor de descuentos', style: GoogleFonts.inter()),
          backgroundColor: AppColors.surface,
          foregroundColor: AppColors.textPrimary,
          elevation: 1,
          actions: [
            IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
          ],
          bottom: const TabBar(
            indicatorColor: AppColors.primary,
            labelColor: AppColors.primary,
            unselectedLabelColor: AppColors.textSecondary,
            tabs: [
              Tab(text: 'Reglas de descuento', height: 48),
              Tab(text: 'Líneas de producto', height: 48),
            ],
          ),
        ),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(child: Text(_error!, style: GoogleFonts.inter(color: AppColors.error)))
                : TabBarView(children: [_buildRulesTab(), _buildLinesTab()]),
      ),
    );
  }

  // ── Tab: Reglas ──────────────────────────────────────────────────────────
  Widget _buildRulesTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
          child: Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _sellerFilter,
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: 'Vendedor',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  items: _sellerOptions
                      .map((o) => DropdownMenuItem(value: o.$1, child: Text(o.$2)))
                      .toList(),
                  onChanged: (v) {
                    setState(() => _sellerFilter = v ?? '');
                    _load();
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _lineFilter,
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: 'Línea de producto',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    const DropdownMenuItem(value: '', child: Text('Todas')),
                    ..._lines.map((l) =>
                        DropdownMenuItem(value: l.id, child: Text(l.name))),
                  ],
                  onChanged: (v) {
                    setState(() => _lineFilter = v ?? '');
                    _load();
                  },
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: () => _showRuleDialog(),
                icon: const Icon(Icons.add, size: 18),
                label: Text('Nueva regla', style: GoogleFonts.inter()),
                style: FilledButton.styleFrom(backgroundColor: AppColors.primary),
              ),
            ],
          ),
        ),
        Expanded(
          child: _rules.isEmpty
              ? Center(
                  child: Text('No hay reglas', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                )
              : context.isDesktop ? _buildRulesDesktop() : _buildRulesMobile(),
        ),
      ],
    );
  }

  Widget _buildRulesDesktop() {
    return ClipRect(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
        child: AppTable<DiscountRule>(
          columns: const [
            AppColumn(title: 'Vendedor', width: 170),
            AppColumn(title: 'Línea', flex: 2),
            AppColumn(title: 'Condición', width: 100),
            AppColumn(title: 'Tramo', flex: 2),
            AppColumn(title: 'Máx', width: 70),
            AppColumn(title: 'Aprob.', width: 80),
            AppColumn(title: 'Estado', width: 90),
            AppColumn(title: 'Acciones', width: 120),
          ],
          items: _rules,
          rowHeight: 48,
          headerColor: AppColors.background,
          cellBuilder: (context, r, col) {
            switch (col) {
              case 0:
                return Text(_sellerLabel(r.sellerType),
                    style: const TextStyle(fontWeight: FontWeight.w500));
              case 1:
                return Text(r.productLineName ?? r.productLineKey ?? '—',
                    overflow: TextOverflow.ellipsis);
              case 2:
                return Text(_conditionLabel(r.conditionType));
              case 3:
                return Text(_rangeText(r));
              case 4:
                return Text(_fmtPct(r.maxDiscount),
                    style: const TextStyle(fontWeight: FontWeight.w600));
              case 5:
                return r.requiresApproval
                    ? const Icon(Icons.check_circle, size: 18, color: AppColors.warning)
                    : const Text('—');
              case 6:
                return _statusChip(r.isActive);
              case 7:
                return _ruleActions(r);
              default:
                return const SizedBox();
            }
          },
        ),
      ),
    );
  }

  Widget _buildRulesMobile() {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      itemCount: _rules.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final r = _rules[i];
        return Card(
          color: AppColors.surface,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: AppColors.divider.withValues(alpha: 0.4)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${_sellerLabel(r.sellerType)} · ${r.productLineName ?? r.productLineKey ?? '—'}',
                        style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                    ),
                    _statusChip(r.isActive),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _infoCol('Condición', _conditionLabel(r.conditionType)),
                    _infoCol('Tramo', _rangeText(r)),
                    _infoCol('Máx', _fmtPct(r.maxDiscount)),
                    if (r.requiresApproval)
                      _infoCol('Aprob.', 'Sí'),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: _ruleActionButtons(r, compact: true),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _infoCol(String label, String value) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary)),
          const SizedBox(height: 2),
          Text(value, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _statusChip(bool active) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: active
            ? AppColors.success.withValues(alpha: 0.12)
            : AppColors.textSecondary.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        active ? 'Activa' : 'Inactiva',
        style: GoogleFonts.inter(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: active ? AppColors.success : AppColors.textSecondary,
        ),
      ),
    );
  }

  Widget _ruleActions(DiscountRule r) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: _ruleActionButtons(r),
    );
  }

  List<Widget> _ruleActionButtons(DiscountRule r, {bool compact = false}) {
    return [
      Tooltip(
        message: 'Editar',
        child: IconButton(
          icon: const Icon(Icons.edit_outlined, size: 18),
          onPressed: () => _showRuleDialog(rule: r),
          visualDensity: compact ? VisualDensity.compact : null,
        ),
      ),
      Tooltip(
        message: r.isActive ? 'Desactivar' : 'Activar',
        child: IconButton(
          icon: Icon(
            r.isActive ? Icons.pause_circle_outline : Icons.play_circle_outline,
            size: 18,
            color: AppColors.textSecondary,
          ),
          onPressed: () => _toggleRule(r),
          visualDensity: compact ? VisualDensity.compact : null,
        ),
      ),
      Tooltip(
        message: 'Eliminar',
        child: IconButton(
          icon: const Icon(Icons.delete_outline, size: 18, color: AppColors.error),
          onPressed: () => _deleteRule(r),
          visualDensity: compact ? VisualDensity.compact : null,
        ),
      ),
    ];
  }

  Future<void> _toggleRule(DiscountRule r) async {
    await _run(() async {
      await context.read<ApiService>().updateDiscountRule(r.id, {'is_active': !r.isActive});
      return true;
    });
  }

  Future<void> _deleteRule(DiscountRule r) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar regla'),
        content: Text(
            '¿Desactivar la regla de ${_sellerLabel(r.sellerType)} · ${r.productLineName ?? r.productLineKey ?? '—'}?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
    if (ok != true) return;
    await _run(() async {
      await context.read<ApiService>().deleteDiscountRule(r.id);
      return true;
    });
  }

  Future<void> _showRuleDialog({DiscountRule? rule}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (context) => _RuleDialog(rule: rule, lines: _lines, bands: _bands),
    );
    if (saved == true) _load();
  }

  // ── Tab: Líneas ──────────────────────────────────────────────────────────
  Widget _buildLinesTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'Líneas de producto usadas por el motor de descuentos',
                  style: GoogleFonts.inter(color: AppColors.textSecondary, fontSize: 13),
                ),
              ),
              FilledButton.icon(
                onPressed: () => _showLineDialog(),
                icon: const Icon(Icons.add, size: 18),
                label: Text('Nueva línea', style: GoogleFonts.inter()),
                style: FilledButton.styleFrom(backgroundColor: AppColors.primary),
              ),
            ],
          ),
        ),
        Expanded(
          child: _lines.isEmpty
              ? Center(
                  child: Text('No hay líneas', style: GoogleFonts.inter(color: AppColors.textSecondary)),
                )
              : context.isDesktop ? _buildLinesDesktop() : _buildLinesMobile(),
        ),
      ],
    );
  }

  Widget _buildLinesDesktop() {
    return ClipRect(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
        child: AppTable<ProductLine>(
          columns: const [
            AppColumn(title: 'Clave', width: 200),
            AppColumn(title: 'Nombre', flex: 3),
            AppColumn(title: 'Estado', width: 100),
            AppColumn(title: 'Acciones', width: 120),
          ],
          items: _lines,
          rowHeight: 48,
          headerColor: AppColors.background,
          cellBuilder: (context, l, col) {
            switch (col) {
              case 0:
                return Text(l.key,
                    style: const TextStyle(fontWeight: FontWeight.w500));
              case 1:
                return Text(l.name, overflow: TextOverflow.ellipsis);
              case 2:
                return _statusChip(l.isActive);
              case 3:
                return Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Tooltip(
                      message: 'Editar',
                      child: IconButton(
                        icon: const Icon(Icons.edit_outlined, size: 18),
                        onPressed: () => _showLineDialog(line: l),
                      ),
                    ),
                    Tooltip(
                      message: l.isActive ? 'Desactivar' : 'Activar',
                      child: IconButton(
                        icon: Icon(
                          l.isActive ? Icons.pause_circle_outline : Icons.play_circle_outline,
                          size: 18,
                          color: AppColors.textSecondary,
                        ),
                        onPressed: () => _toggleLine(l),
                      ),
                    ),
                  ],
                );
              default:
                return const SizedBox();
            }
          },
        ),
      ),
    );
  }

  Widget _buildLinesMobile() {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      itemCount: _lines.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final l = _lines[i];
        return Card(
          color: AppColors.surface,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: AppColors.divider.withValues(alpha: 0.4)),
          ),
          child: ListTile(
            title: Text('${l.name} (${l.key})',
                style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _statusChip(l.isActive),
                const SizedBox(width: 4),
                IconButton(
                  icon: const Icon(Icons.edit_outlined, size: 18),
                  onPressed: () => _showLineDialog(line: l),
                ),
                IconButton(
                  icon: Icon(
                    l.isActive ? Icons.pause_circle_outline : Icons.play_circle_outline,
                    size: 18,
                    color: AppColors.textSecondary,
                  ),
                  onPressed: () => _toggleLine(l),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _toggleLine(ProductLine l) async {
    await _run(() async {
      await context.read<ApiService>().updateProductLine(l.id, {'is_active': !l.isActive});
      return true;
    });
  }

  Future<void> _showLineDialog({ProductLine? line}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (context) => _LineDialog(line: line),
    );
    if (saved == true) _load();
  }
}

// ── Diálogo: regla ─────────────────────────────────────────────────────────
class _RuleDialog extends StatefulWidget {
  final DiscountRule? rule;
  final List<ProductLine> lines;
  final List<DiscountBand> bands;

  const _RuleDialog({this.rule, required this.lines, required this.bands});

  @override
  State<_RuleDialog> createState() => _RuleDialogState();
}

class _RuleDialogState extends State<_RuleDialog> {
  final _formKey = GlobalKey<FormState>();
  late String _sellerType;
  late String _productLineId;
  late String _conditionType;
  String _bandKey = 'custom';
  late final TextEditingController _minCtrl;
  late final TextEditingController _maxCtrl;
  late final TextEditingController _maxDiscCtrl;
  late bool _requiresApproval;

  @override
  void initState() {
    super.initState();
    final r = widget.rule;
    final selectedLine = widget.lines.where((l) => l.id == r?.productLineId).firstOrNull;
    _sellerType = r?.sellerType ?? 'vendedor_interno';
    _productLineId = r?.productLineId ?? (widget.lines.isEmpty ? '' : widget.lines.first.id);
    _conditionType = r?.conditionType ?? _suggestedCondition(selectedLine);
    _maxDiscCtrl = TextEditingController(
      text: r != null ? _fmtNum(r.maxDiscount) : '',
    );
    _requiresApproval = r?.requiresApproval ?? false;

    if (r != null) {
      final bands = widget.bands.where((b) => b.conditionType == r.conditionType).toList();
      _bandKey = _bandKeyFor(r.minValue, r.maxValue, bands) ?? 'custom';
    }

    if (_bandKey == 'custom') {
      _minCtrl = TextEditingController(text: r?.minValue != null ? _fmtNum(r!.minValue!) : '');
      _maxCtrl = TextEditingController(text: r?.maxValue != null ? _fmtNum(r!.maxValue!) : '');
    } else {
      _minCtrl = TextEditingController();
      _maxCtrl = TextEditingController();
      _applyBand(_bandKey);
    }
  }

  @override
  void dispose() {
    _minCtrl.dispose();
    _maxCtrl.dispose();
    _maxDiscCtrl.dispose();
    super.dispose();
  }

  List<DiscountBand> get _conditionBands =>
      widget.bands.where((b) => b.conditionType == _conditionType).toList();

  void _applyBand(String key) {
    if (key == 'custom') {
      setState(() {
        _bandKey = key;
        _minCtrl.clear();
        _maxCtrl.clear();
      });
      return;
    }
    final band = widget.bands.firstWhere((b) => b.key == key);
    setState(() {
      _bandKey = key;
      _minCtrl.text = band.min != null ? _fmtNum(band.min!) : '';
      _maxCtrl.text = band.max != null ? _fmtNum(band.max!) : '';
    });
  }

  void _onConditionChanged(String? value) {
    final cond = value ?? 'amount';
    setState(() {
      _conditionType = cond;
      _bandKey = 'custom';
      _minCtrl.clear();
      _maxCtrl.clear();
    });
  }

  void _onLineChanged(String? lineId) {
    final line = widget.lines.where((l) => l.id == lineId).firstOrNull;
    if (line == null) return;
    if (widget.rule == null) {
      setState(() {
        _productLineId = line.id;
        _conditionType = _suggestedCondition(line);
        _bandKey = 'custom';
        _minCtrl.clear();
        _maxCtrl.clear();
      });
    } else {
      setState(() => _productLineId = line.id);
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (_productLineId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Seleccioná una línea de producto')),
      );
      return;
    }
    double? parseNum(String t) {
      final cleaned = t.trim().replaceAll(',', '.');
      if (cleaned.isEmpty) return null;
      return double.tryParse(cleaned);
    }

    double? minV;
    double? maxV;
    if (_bandKey == 'custom') {
      minV = parseNum(_minCtrl.text);
      maxV = parseNum(_maxCtrl.text);
      if (minV == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ingresá el límite mínimo del tramo')),
        );
        return;
      }
    } else {
      final band = widget.bands.firstWhere((b) => b.key == _bandKey);
      minV = band.min;
      maxV = band.max;
    }

    final maxDisc = parseNum(_maxDiscCtrl.text);
    if (maxDisc == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingresá el porcentaje máximo')),
      );
      return;
    }

    final payload = {
      'seller_type': _sellerType,
      'product_line_id': _productLineId,
      'condition_type': _conditionType,
      'min_value': minV,
      'max_value': maxV,
      'max_discount': maxDisc,
      'requires_approval': _requiresApproval,
    };

    try {
      final api = context.read<ApiService>();
      if (widget.rule == null) {
        await api.createDiscountRule(payload);
      } else {
        await api.updateDiscountRule(widget.rule!.id, payload);
      }
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al guardar: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.rule != null;
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(isEdit ? 'Editar regla' : 'Nueva regla', style: GoogleFonts.inter()),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                initialValue: _sellerType,
                decoration: const InputDecoration(labelText: 'Vendedor', border: OutlineInputBorder()),
                items: _sellerOptions
                    .where((o) => o.$1.isNotEmpty)
                    .map((o) => DropdownMenuItem(value: o.$1, child: Text(o.$2)))
                    .toList(),
                onChanged: (v) => setState(() => _sellerType = v ?? 'vendedor_interno'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _productLineId,
                decoration: const InputDecoration(labelText: 'Línea de producto', border: OutlineInputBorder()),
                items: widget.lines.map((l) =>
                    DropdownMenuItem(value: l.id, child: Text('${l.name} (${l.key})'))).toList(),
                onChanged: _onLineChanged,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _conditionType,
                decoration: const InputDecoration(labelText: 'Condición', border: OutlineInputBorder()),
                items: const [
                  DropdownMenuItem(value: 'amount', child: Text('Monto')),
                  DropdownMenuItem(value: 'qty', child: Text('Cantidad')),
                ],
                onChanged: _onConditionChanged,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _bandKey,
                decoration: const InputDecoration(labelText: 'Tramo', border: OutlineInputBorder()),
                items: [
                  const DropdownMenuItem(value: 'custom', child: Text('Personalizado')),
                  ..._conditionBands.map((b) =>
                      DropdownMenuItem(value: b.key, child: Text(b.label))),
                ],
                onChanged: (v) => _applyBand(v ?? 'custom'),
              ),
              if (_bandKey == 'custom') ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _minCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(labelText: 'Mínimo', border: OutlineInputBorder()),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _maxCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(labelText: 'Máximo (vacío = abierto)', border: OutlineInputBorder()),
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 12),
              TextFormField(
                controller: _maxDiscCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Máx % de descuento', border: OutlineInputBorder()),
                validator: (v) {
                  final val = double.tryParse((v ?? '').trim().replaceAll(',', '.'));
                  if (val == null) return 'Ingresá un número';
                  if (val < 0 || val > 100) return 'Entre 0 y 100';
                  return null;
                },
              ),
              const SizedBox(height: 4),
              CheckboxListTile(
                value: _requiresApproval,
                onChanged: (v) => setState(() => _requiresApproval = v ?? false),
                title: Text('Requiere aprobación', style: GoogleFonts.inter(fontSize: 14)),
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _save,
          style: FilledButton.styleFrom(backgroundColor: AppColors.primary),
          child: Text(isEdit ? 'Guardar' : 'Crear'),
        ),
      ],
    );
  }
}

// ── Diálogo: línea ─────────────────────────────────────────────────────────
class _LineDialog extends StatefulWidget {
  final ProductLine? line;
  const _LineDialog({this.line});

  @override
  State<_LineDialog> createState() => _LineDialogState();
}

class _LineDialogState extends State<_LineDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _keyCtrl;
  late final TextEditingController _nameCtrl;
  late bool _isActive;

  @override
  void initState() {
    super.initState();
    _keyCtrl = TextEditingController(text: widget.line?.key ?? '');
    _nameCtrl = TextEditingController(text: widget.line?.name ?? '');
    _isActive = widget.line?.isActive ?? true;
  }

  @override
  void dispose() {
    _keyCtrl.dispose();
    _nameCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final api = context.read<ApiService>();
    try {
      if (widget.line == null) {
        await api.createProductLine({'key': _keyCtrl.text.trim(), 'name': _nameCtrl.text.trim()});
      } else {
        await api.updateProductLine(widget.line!.id, {
          'name': _nameCtrl.text.trim(),
          'is_active': _isActive,
        });
      }
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al guardar: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.line != null;
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(isEdit ? 'Editar línea' : 'Nueva línea', style: GoogleFonts.inter()),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!isEdit)
              TextFormField(
                controller: _keyCtrl,
                decoration: const InputDecoration(labelText: 'Clave (key)', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Ingresá la clave' : null,
              ),
            if (!isEdit) const SizedBox(height: 12),
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Nombre', border: OutlineInputBorder()),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Ingresá el nombre' : null,
            ),
            if (isEdit) ...[
              const SizedBox(height: 12),
              CheckboxListTile(
                value: _isActive,
                onChanged: (v) => setState(() => _isActive = v ?? true),
                title: Text('Línea activa', style: GoogleFonts.inter(fontSize: 14)),
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _save,
          style: FilledButton.styleFrom(backgroundColor: AppColors.primary),
          child: Text(isEdit ? 'Guardar' : 'Crear'),
        ),
      ],
    );
  }
}
