import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  VoidCallback? onAuthFailure;

  final String? overrideBaseUrl;

  String get baseUrl => overrideBaseUrl ?? (kIsWeb ? 'http://localhost:8000' : 'http://10.0.2.2:8000');

  late Dio _dio;
  final _storage = const FlutterSecureStorage();
  bool _isRefreshing = false;

  ApiService({this.overrideBaseUrl}) {
    debugPrint('--- BASE URL: ${baseUrl} ---');
    _dio = Dio(BaseOptions(baseUrl: baseUrl));
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: _accessTokenKey);
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
          final refreshToken = await _storage.read(key: _refreshTokenKey);
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

          await _storage.write(key: _accessTokenKey, value: newAccess);
          await _storage.write(key: _refreshTokenKey, value: newRefresh);

          final opts = error.requestOptions;
          opts.headers['Authorization'] = 'Bearer $newAccess';
          final retryDio = Dio(BaseOptions(baseUrl: baseUrl));
          final response = await retryDio.fetch(opts);
          _isRefreshing = false;
          return handler.resolve(response);
        } catch (_) {
          await _storage.delete(key: _accessTokenKey);
          await _storage.delete(key: _refreshTokenKey);
          _isRefreshing = false;
          onAuthFailure?.call();
          return handler.next(error);
        }
      },
    ));
  }

  Dio get dio => _dio;

  Future<List<Map<String, dynamic>>> getCustomers() async {
    try {
      final response = await _dio.get('/customers');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('Error fetching customers: $e');
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

  Future<void> saveToken(String token) async {
    await _storage.write(key: _accessTokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _accessTokenKey);
  }
}
