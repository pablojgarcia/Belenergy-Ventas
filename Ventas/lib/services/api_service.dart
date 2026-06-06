import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String _accessTokenKey = 'access_token';

  // Evaluamos en tiempo de ejecución para evitar problemas de caché de compilación
  String get baseUrl => kIsWeb ? 'http://localhost:8000' : 'http://10.0.2.2:8000';
  
  late Dio _dio;
  final _storage = const FlutterSecureStorage();

  ApiService() {
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

  Future<void> saveToken(String token) async {
    await _storage.write(key: _accessTokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _accessTokenKey);
  }
}
