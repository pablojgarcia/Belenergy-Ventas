import 'package:flutter/material.dart';

class AppColumn {
  final String title;
  final double? width;
  final int? flex;
  final double? minWidth;

  const AppColumn({
    required this.title,
    this.width,
    this.flex,
    this.minWidth,
  });
}

class AppTable<T> extends StatelessWidget {
  final List<AppColumn> columns;
  final List<T> items;
  final Widget Function(BuildContext context, T item, int columnIndex) cellBuilder;
  final double rowHeight;
  final TextStyle? headerStyle;
  final TextStyle? cellStyle;
  final Color? headerColor;
  final Color? evenRowColor;
  final Color? dividerColor;

  const AppTable({
    super.key,
    required this.columns,
    required this.items,
    required this.cellBuilder,
    this.rowHeight = 48,
    this.headerStyle,
    this.cellStyle,
    this.headerColor,
    this.evenRowColor,
    this.dividerColor,
  });

  @override
  Widget build(BuildContext context) {
    final hStyle = headerStyle ?? const TextStyle(fontWeight: FontWeight.w600, fontSize: 13);
    final cStyle = cellStyle ?? const TextStyle(fontSize: 13);
    final hColor = headerColor ?? Colors.transparent;
    final eColor = evenRowColor ?? Colors.transparent;
    final dColor = dividerColor ?? const Color(0xFFE0E0E0);

    final hasFixedWidth = columns.any((c) => c.width != null);
    final hasFlex = columns.any((c) => c.flex != null);
    final totalFixed = columns.fold<double>(0, (s, c) => s + (c.width ?? 0));
    final flexSum = columns.fold<int>(0, (s, c) => s + (c.flex ?? 0));

    Widget buildHeader(double availW) {
      return Row(
        children: columns.map((col) {
          Widget cell = Text(col.title, style: hStyle, overflow: TextOverflow.ellipsis);
          return _sizedCell(col, cell, availW, flexSum);
        }).toList(),
      );
    }

    Widget buildRow(T item, double availW) {
      return Row(
        children: List.generate(columns.length, (i) {
          Widget cell = DefaultTextStyle(
            style: cStyle,
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
            child: cellBuilder(context, item, i),
          );
          return _sizedCell(columns[i], cell, availW, flexSum);
        }),
      );
    }

    Widget tableContent(double availW) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            height: rowHeight,
            color: hColor,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            alignment: Alignment.centerLeft,
            child: buildHeader(availW),
          ),
          Divider(height: 1, color: dColor),
          Expanded(
            child: ListView.builder(
              itemCount: items.length,
              itemExtent: rowHeight,
              itemBuilder: (_, index) {
                return Container(
                  height: rowHeight,
                  color: index.isEven ? eColor : null,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  alignment: Alignment.centerLeft,
                  child: buildRow(items[index], availW),
                );
              },
            ),
          ),
        ],
      );
    }

    if (hasFlex) {
      return tableContent(double.infinity);
    }

    if (hasFixedWidth) {
      return SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: SizedBox(
          width: totalFixed,
          child: tableContent(totalFixed),
        ),
      );
    }

    return tableContent(double.infinity);
  }

  Widget _sizedCell(AppColumn col, Widget child, double availW, int flexSum) {
    if (col.width != null) {
      return SizedBox(width: col.width!, child: child);
    }
    if (col.flex != null && flexSum > 0) {
      return Expanded(flex: col.flex!, child: child);
    }
    return SizedBox(width: col.minWidth ?? 120, child: child);
  }
}
