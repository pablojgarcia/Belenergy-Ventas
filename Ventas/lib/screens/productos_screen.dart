import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../models/product_model.dart';
import '../utils/theme.dart';
import '../utils/responsive.dart';
import '../services/api_service.dart';
import '../widgets/app_table.dart';

class ProductosScreen extends StatefulWidget {
  const ProductosScreen({super.key});

  @override
  State<ProductosScreen> createState() => _ProductosScreenState();
}

class _ProductosScreenState extends State<ProductosScreen> {
  late Future<List<Product>> _productsFuture;
  List<Product> _allProducts = [];
  List<Product> _filteredProducts = [];
  final _searchController = TextEditingController();
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _productsFuture = _fetchProducts();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<List<Product>> _fetchProducts() async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    final data = await apiService.getProducts();
    final products = data.map((json) => Product.fromJson(json)).toList();
    if (mounted) {
      setState(() {
        _allProducts = products;
        _filteredProducts = products;
        _loaded = true;
      });
    }
    return products;
  }

  void _filterProducts(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredProducts = _allProducts;
      } else {
        final q = query.toLowerCase();
        _filteredProducts = _allProducts.where((p) =>
          p.name.toLowerCase().contains(q) ||
          p.defaultCode.toLowerCase().contains(q) ||
          p.categId.toLowerCase().contains(q)
        ).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Productos', style: GoogleFonts.inter()),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _loaded = false;
                _productsFuture = _fetchProducts();
              });
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Product>>(
        future: _productsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting && !_loaded) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError && !_loaded) {
            return Center(
              child: Text(
                'Error al cargar productos',
                style: GoogleFonts.inter(color: Colors.red),
              ),
            );
          }

          if (_filteredProducts.isEmpty && _loaded) {
            return Center(
              child: Text(
                'No se encontraron productos',
                style: GoogleFonts.inter(color: AppColors.textSecondary),
              ),
            );
          }

          if (context.isDesktop) {
            return _buildDesktopTable();
          }

          return _buildMobileGrid();
        },
      ),
    );
  }

  Widget _buildDesktopTable() {
    return Column(
      children: [
        _buildSearchBar(),
        Expanded(
          child: ClipRect(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: AppTable<Product>(
                columns: const [
                  AppColumn(title: 'Imagen', width: 72),
                  AppColumn(title: 'Título', flex: 4),
                  AppColumn(title: 'Código', width: 160),
                  AppColumn(title: 'Precio', width: 100),
                  AppColumn(title: 'Categoría', width: 160),
                ],
                items: _filteredProducts,
                rowHeight: 48,
                headerColor: AppColors.background,
                cellBuilder: (context, p, col) {
                  switch (col) {
                    case 0: return _ProductThumbnail(productId: p.id);
                    case 1: return Text(p.name, style: const TextStyle(fontWeight: FontWeight.w500));
                    case 2: return Text(p.defaultCode);
                    case 3: return Text(p.formattedPrice, style: const TextStyle(fontWeight: FontWeight.w600));
                    case 4: return Text(p.categId.isEmpty ? '—' : p.categId);
                    default: return const SizedBox();
                  }
                },
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
      child: TextField(
        controller: _searchController,
        onChanged: _filterProducts,
        decoration: InputDecoration(
          hintText: 'Buscar productos...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _filterProducts('');
                  },
                )
              : null,
          isDense: true,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }

  Widget _buildMobileGrid() {
    final columns = Responsive.value(context, mobile: 1, tablet: 2, desktop: 3);
    return Column(
      children: [
        _buildSearchBar(),
        Expanded(
          child: GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: columns,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: columns == 1 ? 2.6 : 1.3,
            ),
            itemCount: _filteredProducts.length,
            itemBuilder: (context, index) => _ProductCard(product: _filteredProducts[index]),
          ),
        ),
      ],
    );
  }
}

String _typeLabel(String type) {
  switch (type) {
    case 'product': return 'Producto';
    case 'consu': return 'Consumible';
    case 'service': return 'Servicio';
    default: return type;
  }
}

Widget _infoChip(IconData icon, String label) {
  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
    decoration: BoxDecoration(
      color: AppColors.background,
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: AppColors.divider),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 13, color: AppColors.textSecondary),
        const SizedBox(width: 5),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    ),
  );
}

class _ProductThumbnail extends StatefulWidget {
  final int productId;
  const _ProductThumbnail({required this.productId});

  @override
  State<_ProductThumbnail> createState() => _ProductThumbnailState();
}

class _ProductThumbnailState extends State<_ProductThumbnail> {
  Uint8List? _imageBytes;
  bool _loadingImage = true;

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  Future<void> _loadImage() async {
    try {
      final api = context.read<ApiService>();
      final response = await api.dio.get(
        '/products/${widget.productId}/image',
        options: Options(responseType: ResponseType.bytes),
      );
      if (mounted) setState(() { _imageBytes = response.data; _loadingImage = false; });
    } catch (_) {
      if (mounted) setState(() => _loadingImage = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: SizedBox(
        width: 40,
        height: 40,
        child: _imageBytes != null
            ? Image.memory(_imageBytes!, fit: BoxFit.cover, errorBuilder: (_, __, ___) => _placeholder())
            : _placeholder(),
      ),
    );
  }

  Widget _placeholder() {
    return Container(
      color: AppColors.accent.withOpacity(0.12),
      child: _loadingImage
          ? const Center(child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)))
          : const Icon(Icons.solar_power_rounded, color: AppColors.accent, size: 20),
    );
  }
}

class _ProductCard extends StatefulWidget {
  final Product product;
  const _ProductCard({required this.product});

  @override
  State<_ProductCard> createState() => _ProductCardState();
}

class _ProductCardState extends State<_ProductCard> {
  Uint8List? _imageBytes;
  bool _loadingImage = true;

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  Future<void> _loadImage() async {
    try {
      final api = context.read<ApiService>();
      final response = await api.dio.get(
        '/products/${widget.product.id}/image',
        options: Options(responseType: ResponseType.bytes),
      );
      setState(() { _imageBytes = response.data; _loadingImage = false; });
    } catch (_) {
      setState(() => _loadingImage = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final product = widget.product;
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.divider),
        boxShadow: const [
          BoxShadow(
            color: AppColors.cardShadow,
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: SizedBox(
                    width: 64,
                    height: 64,
                    child: _imageBytes != null
                        ? Image.memory(_imageBytes!, fit: BoxFit.cover, errorBuilder: (_, __, ___) => _cardPlaceholder())
                        : _cardPlaceholder(),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        product.name,
                        style: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
                      ),
                      if (product.defaultCode.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          product.defaultCode,
                          style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                        ),
                      ],
                    ],
                  ),
                ),
                Text(
                  product.formattedPrice,
                  style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.primary),
                ),
              ],
            ),
            const SizedBox(height: 14),
            OverflowBar(
              spacing: 8,
              children: [
                _infoChip(Icons.category_outlined, product.categId.isNotEmpty ? product.categId : 'Sin categoría'),
                _infoChip(Icons.inventory_2_outlined, _typeLabel(product.type)),
                if (product.uomId.isNotEmpty)
                  _infoChip(Icons.straighten, product.uomId),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _cardPlaceholder() {
    return Container(
      color: AppColors.accent.withOpacity(0.12),
      child: _loadingImage
          ? const Center(child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)))
          : const Icon(Icons.solar_power_rounded, color: AppColors.accent, size: 28),
    );
  }
}
