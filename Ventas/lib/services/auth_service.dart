import 'package:dio/dio.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../models/auth_model.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  final ApiService _apiService = ApiService();
  final StorageService _storage = StorageService();

  Future<AuthToken> login(String email, String password) async {
    try {
      final response = await _apiService.dio.post('/auth/login', data: {
        'username': email,
        'password': password,
      });

      final token = AuthToken.fromJson(response.data);
      await _saveTokens(token);
      return token;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<AuthToken?> refreshToken() async {
    final refresh = await _storage.read(_refreshTokenKey);
    if (refresh == null) return null;

    try {
      final response = await _apiService.dio.post('/auth/refresh', data: {
        'refresh_token': refresh,
      });
      final token = AuthToken.fromJson(response.data);
      await _saveTokens(token);
      return token;
    } on DioException {
      await logout();
      return null;
    }
  }

  Future<UserInfo?> getUserInfo() async {
    try {
      final response = await _apiService.dio.get('/auth/me');
      return UserInfo.fromJson(response.data);
    } on DioException {
      return null;
    }
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(_accessTokenKey);
    return token != null && !JwtDecoder.isExpired(token);
  }

  Future<void> logout() async {
    await _storage.delete(_accessTokenKey);
    await _storage.delete(_refreshTokenKey);
  }

  Future<void> _saveTokens(AuthToken token) async {
    await _storage.write(_accessTokenKey, token.accessToken);
    await _storage.write(_refreshTokenKey, token.refreshToken);
  }

  String _handleDioError(DioException e) {
    if (e.response?.statusCode == 401) return 'Credenciales incorrectas';
    return 'Error de conexión';
  }
}
