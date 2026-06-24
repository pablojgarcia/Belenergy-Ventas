import 'dart:io';
import 'dart:typed_data';

void saveBytes(Uint8List bytes, String filename) {
  final dir = Directory.systemTemp;
  final file = File('${dir.path}/$filename');
  file.writeAsBytesSync(bytes);
}
