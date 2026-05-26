import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../config/app_config.dart';
import '../models/auth_model.dart';

class AuthService {
  static const String _baseUrl = 'https://tu-backend.com/api'; // ← Cambiar
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const bool _bypassAuth = AppConfig.bypassAuthentication;

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

  final Dio _dio = Dio(BaseOptions(
    baseUrl: _baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  // ── Login ────────────────────────────────────────────────────────────────
  Future<AuthToken> login(String email, String password) async {
    if (_bypassAuth) {
      await _saveTokens(_mockToken);
      return _mockToken;
    }

    try {
      final response = await _dio.post('/auth/login', data: {
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

  // ── Refresh token ────────────────────────────────────────────────────────
  Future<AuthToken?> refreshToken() async {
    if (_bypassAuth) {
      return _mockToken;
    }

    final refresh = await _storage.read(key: _refreshTokenKey);
    if (refresh == null) return null;

    try {
      final response = await _dio.post('/auth/refresh', data: {
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

  // ── Get user info ────────────────────────────────────────────────────────
  Future<UserInfo?> getUserInfo() async {
    if (_bypassAuth) {
      return _mockUser;
    }

    final token = await getAccessToken();
    if (token == null) return null;

    try {
      final response = await _dio.get(
        '/auth/me',
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );
      return UserInfo.fromJson(response.data);
    } on DioException {
      return null;
    }
  }

  // ── Token utilities ──────────────────────────────────────────────────────
  Future<String?> getAccessToken() async {
    if (_bypassAuth) {
      final token = await _storage.read(key: _accessTokenKey);
      if (token != null) return token;
      await _saveTokens(_mockToken);
      return _mockToken.accessToken;
    }

    final token = await _storage.read(key: _accessTokenKey);
    if (token == null) return null;

    // Si expiró, intentar refresh automático
    if (JwtDecoder.isExpired(token)) {
      final refreshed = await refreshToken();
      return refreshed?.accessToken;
    }
    return token;
  }

  Future<bool> isLoggedIn() async {
    if (_bypassAuth) {
      final token = await _storage.read(key: _accessTokenKey);
      if (token != null) return true;
      await _saveTokens(_mockToken);
      return true;
    }

    final token = await _storage.read(key: _accessTokenKey);
    if (token == null) return false;

    if (JwtDecoder.isExpired(token)) {
      final refreshed = await refreshToken();
      return refreshed != null;
    }
    return true;
  }

  Future<void> logout() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  // ── Privados ─────────────────────────────────────────────────────────────
  Future<void> _saveTokens(AuthToken token) async {
    await _storage.write(key: _accessTokenKey, value: token.accessToken);
    await _storage.write(key: _refreshTokenKey, value: token.refreshToken);
  }

  String _handleDioError(DioException e) {
    if (e.response?.statusCode == 401) {
      return 'Credenciales incorrectas';
    } else if (e.response?.statusCode == 422) {
      return 'Datos inválidos';
    } else if (e.type == DioExceptionType.connectionTimeout) {
      return 'No se pudo conectar al servidor';
    } else if (e.type == DioExceptionType.connectionError) {
      return 'Sin conexión a internet';
    }
    return 'Error inesperado. Intentá de nuevo.';
  }
}
