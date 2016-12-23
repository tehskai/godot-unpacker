<pre>
<?php
error_reporting(E_ALL);
ini_set("display_errors", 1);

$f = fopen('./data.pck', 'rb');

$bin_file_header = fread($f, 20+64+4);

$file_header_format = implode('/', [
  'Lmagic',
  'Lversion',
  'Lver_major',
  'Lver_minor',
  'Lver_rev',
  //'L16reserved',
  'x64reserved',
  'Ifile_count'
]);

$file_header = unpack($file_header_format, $bin_file_header);
$packed_files = Array();

for ($i = 0; $i < $file_header['file_count']; $i++) {
  $sl = fread($f, 4);
  $sl = unpack('Lsl', $sl);
  $sl = $sl['sl'];
  $file_info = fread($f, $sl+8+8+16);
  $packed_files[] = unpack('A'.$sl.'data/Qoffset/Qsize/H32md5', $file_info);
}

// fseek($f, 1685795);
// $data = fread($f, 2392);
// $u = fopen('ui.gdc', 'wb');
// fputs($u, $data);
// fclose($u);

fclose($f);
print_r($file_header);
print_r($packed_files);
?>
