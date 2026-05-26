import 'package:flutter/foundation.dart';
import '../models/auth_model.dart';
import '../services/auth_service.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  AuthStatus _status = AuthStatus.initial;
  UserInfo? _user;
  String? _errorMessage;

  AuthStatus get status => _status;
  UserInfo? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _status == AuthStatus.loading;

  // ── Chequear sesión al inicio ────────────────────────────────────────────
  Future<void> checkAuthStatus() async {
    _setStatus(AuthStatus.loading);
    final loggedIn = await _authService.isLoggedIn();

    if (loggedIn) {
      _user = await _authService.getUserInfo();
      _setStatus(AuthStatus.authenticated);
    } else {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  // ── Login ────────────────────────────────────────────────────────────────
  Future<bool> login(String email, String password) async {
    _setStatus(AuthStatus.loading);
    _errorMessage = null;

    try {
      await _authService.login(email, password);
      _user = await _authService.getUserInfo();
      _setStatus(AuthStatus.authenticated);
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _setStatus(AuthStatus.error);
      return false;
    }
  }

  // ── Logout ───────────────────────────────────────────────────────────────
  Future<void> logout() async {
    await _authService.logout();
    _user = null;
    _setStatus(AuthStatus.unauthenticated);
  }

  void _setStatus(AuthStatus status) {
    _status = status;
    notifyListeners();
  }
}
