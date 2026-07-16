import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'storage_service.dart';

class ApiService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  VoidCallback? onAuthFailure;
  final ordersRefreshNotifier = ValueNotifier<int>(0);

  final String? overrideBaseUrl;

  String get baseUrl {
    if (overrideBaseUrl != null) return overrideBaseUrl!;
    final apiUrl = const String.fromEnvironment('API_URL', defaultValue: '');
    if (apiUrl.isNotEmpty) return apiUrl;
    if (kIsWeb) return 'http://localhost:8000';
    return 'http://10.0.2.2:8000';
  }

  late Dio _dio;
  final _storage = StorageService();
  bool _isRefreshing = false;

  ApiService({this.overrideBaseUrl}) {
    debugPrint('--- BASE URL: ${baseUrl} ---');
    _dio = Dio(BaseOptions(baseUrl: baseUrl));
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(_accessTokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode != 401 || _isRefreshing) {
          return handler.next(error);
        }

        _isRefreshing = true;
        try {
          final refreshToken = await _storage.read(_refreshTokenKey);
          if (refreshToken == null) {
            _isRefreshing = false;
            return handler.next(error);
          }

          final refreshResponse = await Dio(
            BaseOptions(baseUrl: baseUrl),
          ).post('/auth/refresh', data: {
            'refresh_token': refreshToken,
          });

          final newAccess = refreshResponse.data['access_token'] as String;
          final newRefresh = refreshResponse.data['refresh_token'] as String;

          await _storage.write(_accessTokenKey, newAccess);
          await _storage.write(_refreshTokenKey, newRefresh);

          final opts = error.requestOptions;
          opts.headers['Authorization'] = 'Bearer $newAccess';
          final retryDio = Dio(BaseOptions(baseUrl: baseUrl));
          final response = await retryDio.fetch(opts);
          _isRefreshing = false;
          return handler.resolve(response);
        } catch (_) {
          await _storage.delete(_accessTokenKey);
          await _storage.delete(_refreshTokenKey);
          _isRefreshing = false;
          onAuthFailure?.call();
          return handler.next(error);
        }
      },
    ));
  }

  Dio get dio => _dio;

  Future<Map<String, dynamic>> getCustomer(int id) async {
    try {
      final response = await _dio.get('/customers/$id');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching customer: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getCustomers() async {
    try {
      final response = await _dio.get('/customers');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching customers: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getContacts(int customerId) async {
    try {
      final response = await _dio.get('/customers/$customerId/contacts');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching contacts: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getProducts() async {
    try {
      final response = await _dio.get('/products');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching products: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createDraft(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/quotation-drafts', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error creating draft: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getDrafts({
    String? status,
    String? q,
    String? dateFrom,
    String? dateTo,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (status != null) params['status'] = status;
      if (q != null) params['q'] = q;
      if (dateFrom != null) params['date_from'] = dateFrom;
      if (dateTo != null) params['date_to'] = dateTo;
      final response =
          await _dio.get('/quotation-drafts', queryParameters: params);
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching drafts: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> getDraft(String id) async {
    try {
      final response = await _dio.get(
        '/quotation-drafts/$id',
        options: Options(validateStatus: (s) => s == 200 || s == 404),
      );
      if (response.statusCode == 404) return null;
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching draft: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>> updateDraft(
      String id, Map<String, dynamic> data) async {
    try {
      final response = await _dio.put('/quotation-drafts/$id', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error updating draft: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> generateQuotation(String draftId) async {
    try {
      final response = await _dio.post('/quotation-drafts/$draftId/generate');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error generating quotation: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getQuotations({
    int? customerId,
    String? dateFrom,
    String? dateTo,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (customerId != null) params['customer_id'] = customerId;
      if (dateFrom != null) params['date_from'] = dateFrom;
      if (dateTo != null) params['date_to'] = dateTo;
      final response = await _dio.get('/quotations', queryParameters: params);
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching quotations: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> getQuotation(String id) async {
    try {
      final response = await _dio.get(
        '/quotations/$id',
        options: Options(validateStatus: (s) => s == 200 || s == 404),
      );
      if (response.statusCode == 404) return null;
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching quotation: $e');
      return null;
    }
  }

  Future<void> syncCustomers() async {
    await _dio.post('/sync/customers');
  }

  Future<void> syncProducts() async {
    await _dio.post('/sync/products');
  }

  Future<List<Map<String, dynamic>>> getTaxes() async {
    try {
      final response = await _dio.get('/taxes');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching taxes: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getLeads({
    String? status,
    String? q,
    String? dateFrom,
    String? dateTo,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (status != null) params['status'] = status;
      if (q != null) params['q'] = q;
      if (dateFrom != null) params['date_from'] = dateFrom;
      if (dateTo != null) params['date_to'] = dateTo;
      final response = await _dio.get('/leads', queryParameters: params);
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching leads: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> getLead(String id) async {
    try {
      final response = await _dio.get(
        '/leads/$id',
        options: Options(validateStatus: (s) => s == 200 || s == 404),
      );
      if (response.statusCode == 404) return null;
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching lead: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>> createLead(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/leads', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error creating lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateLead(
      String id, Map<String, dynamic> data) async {
    try {
      final response = await _dio.put('/leads/$id', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error updating lead: $e');
      rethrow;
    }
  }

  Future<void> deleteLead(String id) async {
    try {
      await _dio.delete('/leads/$id');
    } catch (e) {
      debugPrint('Error deleting lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> approveLead(String id) async {
    try {
      final response = await _dio.post('/leads/$id/approve');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error approving lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> rejectLead(String id, String reason) async {
    try {
      final response = await _dio.post('/leads/$id/reject', data: {
        'rejection_reason': reason,
      });
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error rejecting lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> syncLead(String id) async {
    try {
      final response = await _dio.post('/leads/$id/sync');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error syncing lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> refreshLead(String id) async {
    try {
      final response = await _dio.post('/leads/$id/refresh');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error refreshing lead: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createDraftFromLead(String leadId) async {
    try {
      final response = await _dio.post('/leads/$leadId/create-draft');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      debugPrint('Error creating draft from lead: $e');
      rethrow;
    }
  }

  Future<Uint8List> downloadPdf(String quotationId) async {
    final response = await _dio.get(
      '/quotations/$quotationId/pdf',
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(response.data);
  }

  Future<void> saveToken(String token) async {
    await _storage.write(_accessTokenKey, token);
  }

  Future<String?> getToken() async {
    return await _storage.read(_accessTokenKey);
  }
}
