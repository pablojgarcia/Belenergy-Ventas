class AuthToken {
  final String accessToken;
  final String refreshToken;
  final String tokenType;

  AuthToken({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] ?? '',
      refreshToken: json['refresh_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
    );
  }

  Map<String, dynamic> toJson() => {
        'access_token': accessToken,
        'refresh_token': refreshToken,
        'token_type': tokenType,
      };
}

class UserInfo {
  final int id;
  final String name;
  final String email;
  final String? avatarUrl;
  final String role;

  UserInfo({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    required this.role,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id'] ?? 0,
      name: json['name'] ?? json['username'] ?? '',
      email: json['email'] ?? '',
      avatarUrl: json['avatar_url'],
      role: json['role'] ?? 'vendedor',
    );
  }

  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }
}
