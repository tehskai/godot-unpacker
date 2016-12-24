<pre>
<?php 
/*
  godot-unpacker.php (https://github.com/tehskai/godot-unpacker)
  tool for extracting game files from godot engine data.pck binary packs (UNENCRYPTED)
  really just a proof-of-concept, tested on php 7.0.1 62bit (windows7 64bit)
*/

ini_set("display_errors", 1);
error_reporting(E_ALL);
set_time_limit(0);

$file = "data.pck";
$f = fopen("./${file}", "rb");

$bin_file_header = fread($f, 20+64+4);

$file_header_format = implode("/", [
  "Lmagic",
  "Lversion",
  "Lver_major",
  "Lver_minor",
  "Lver_rev",
  //"L16reserved",
  "x64reserved", // reserved null-bytes
  "Ifile_count" // total file count
]);

$file_header = unpack($file_header_format, $bin_file_header);

$packed_files = Array();

echo "File {$file} (Godot engine v{$file_header['ver_major']}.{$file_header['ver_minor']}), total of {$file_header['file_count']}:".PHP_EOL;

for ($i = 0; $i < $file_header["file_count"]; $i++) {
  $sl = fread($f, 4);
  $sl = unpack("Lsl", $sl);
  $sl = $sl["sl"]; // path length
  $file_info = fread($f, $sl+8+8+16);
  $packed_file_info = unpack("A{$sl}path/Qoffset/Qsize/H32md5", $file_info); // php 7 64bit
  $packed_files[] = $packed_file_info;
  // $packed_file = unpack("A${sl}path/Loffset/Lsize/H32md5", $file_info);  // php 5.5
  echo "{$packed_file_info['md5']} {$packed_file_info['path']} ({$packed_file_info['size']} bytes)".PHP_EOL;
}

for ($i = 0; $i < count($packed_files); $i++) {
  $offset = $packed_files[$i]['offset'];
  $size = $packed_files[$i]['size'];
  $complete_path = str_replace("res://", "", $packed_files[$i]['path']);
  $relative_path = dirname($complete_path);
  $filename = basename($complete_path);

  if (!file_exists($relative_path)) {
      mkdir($relative_path, 0777, true);
      echo "Directory {$relative_path} doesn't exist. Creating.".PHP_EOL;
  }

  fseek($f, $offset);
  $data = fread($f, $size);

  $u = fopen($complete_path, "wb");
  fputs($u, $data);
  fclose($u);

  echo "Extracting {$filename} from {$offset} / {$size} bytes / to {$complete_path} / {$relative_path}".PHP_EOL;
}

fclose($f);
?>