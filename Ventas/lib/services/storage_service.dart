import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static final StorageService _instance = StorageService._();
  factory StorageService() => _instance;
  StorageService._();

  final FlutterSecureStorage _native = const FlutterSecureStorage();

  Future<void> write(String key, String value) async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(key, value);
    } else {
      await _native.write(key: key, value: value);
    }
  }

  Future<String?> read(String key) async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      final value = prefs.getString(key);
      // Migrate old flutter_secure_storage_web encoded values.
      // Valid JWTs always start with "eyJ" (base64 of JSON header).
      // If value exists but doesn't start with "eyJ", it's leftover from
      // flutter_secure_storage_web encoding. Delete it.
      if (value != null && value.isNotEmpty && !value.startsWith('eyJ')) {
        await prefs.remove(key);
        return null;
      }
      return value;
    }
    return await _native.read(key: key);
  }

  Future<void> delete(String key) async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(key);
    } else {
      await _native.delete(key: key);
    }
  }
}