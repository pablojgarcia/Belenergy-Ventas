import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../config/app_config.dart';
import '../models/auth_model.dart';
import 'api_service.dart';

class AuthService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const bool _bypassAuth = AppConfig.bypassAuthentication;
  
  final ApiService _apiService = ApiService();

  static final AuthToken _mockToken = AuthToken(
    accessToken: 'mock_access_token',
    refreshToken: 'mock_refresh_token',
    tokenType: 'bearer',
  );

  static final UserInfo _mockUser = UserInfo(
    id: 0,
    name: 'Usuario de prueba',
    email: 'test@local',
    avatarUrl: null,
    role: 'vendedor',
  );

  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  Future<AuthToken> login(String email, String password) async {
    if (_bypassAuth) {
      await _saveTokens(_mockToken);
      return _mockToken;
    }

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
    if (_bypassAuth) return _mockToken;

    final refresh = await _storage.read(key: _refreshTokenKey);
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
    if (_bypassAuth) return _mockUser;

    try {
      final response = await _apiService.dio.get('/auth/me');
      return UserInfo.fromJson(response.data);
    } on DioException {
      return null;
    }
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: _accessTokenKey);
    return token != null && !JwtDecoder.isExpired(token);
  }

  Future<void> logout() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  Future<void> _saveTokens(AuthToken token) async {
    await _storage.write(key: _accessTokenKey, value: token.accessToken);
    await _storage.write(key: _refreshTokenKey, value: token.refreshToken);
  }

  String _handleDioError(DioException e) {
    if (e.response?.statusCode == 401) return 'Credenciales incorrectas';
    return 'Error de conexión';
  }
}
