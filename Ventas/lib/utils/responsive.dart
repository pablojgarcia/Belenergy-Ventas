import 'package:flutter/material.dart';

class Responsive {
  static const double _phoneBreakpoint = 600;
  static const double _tabletBreakpoint = 1024;

  static bool isPhone(BuildContext context) =>
      MediaQuery.of(context).size.width < _phoneBreakpoint;

  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= _phoneBreakpoint && width < _tabletBreakpoint;
  }

  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= _tabletBreakpoint;

  static T value<T>(BuildContext context,
      {required T mobile, T? tablet, T? desktop}) {
    if (isDesktop(context)) return desktop ?? tablet ?? mobile;
    if (isTablet(context)) return tablet ?? mobile;
    return mobile;
  }

  static int gridColumns(BuildContext context) =>
      value(context, mobile: 2, tablet: 3, desktop: 4);
}

extension ResponsiveContext on BuildContext {
  bool get isPhone => Responsive.isPhone(this);
  bool get isTablet => Responsive.isTablet(this);
  bool get isDesktop => Responsive.isDesktop(this);

  T responsive<T>({required T mobile, T? tablet, T? desktop}) =>
      Responsive.value(this, mobile: mobile, tablet: tablet, desktop: desktop);
}
