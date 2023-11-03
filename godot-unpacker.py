# godot-unpacker.py
# https://github.com/tehskai/godot-unpacker

import sys, os, pathlib, mmap, struct, re, argparse

def main(args):

	parser = argparse.ArgumentParser(description='Simple assets unpacker for Godot game engine')
	parser.add_argument('file', help="game resource pack e.g. data.pck or game.exe file", type=argparse.FileType('r+b'))
	parser.add_argument('--raw', help="do not unpack asset containers (.tex, .stex, .oggstr)", action=argparse.BooleanOptionalAction)
	parser_args = parser.parse_args(args)
	
	unpack_containers = not parser_args.raw
	
	magic = bytes.fromhex('47 44 50 43') # GDPC
	file_list = []
	import_file_list = []
	
	resource_pack_file_name = pathlib.Path(parser_args.file.name).name
	output_dir = resource_pack_file_name.replace(".", "_")
	
	f = mmap.mmap(parser_args.file.fileno(), 0)
	parser_args.file.close()

	if f.read(4) == magic:
		print(resource_pack_file_name + " looks like a .pck resource pack")
		f.seek(0)
	else:
		f.seek(-4, os.SEEK_END)
		if f.read(4) == magic:
			print(resource_pack_file_name + " looks like a self-contained .exe")
			f.seek(-12, os.SEEK_END)
			main_offset = int.from_bytes(f.read(8), byteorder="little")
			f.seek(f.tell() - main_offset - 8)
			if f.read(4) == magic:
				f.seek(f.tell() - 4)
		else:
			f.close()
			return "Error: file not supported"
	package_headers = struct.unpack_from("IIIII16II", f.read(20 + 64 + 4))
	print (resource_pack_file_name + " info:", package_headers)
	file_count = package_headers[-1]

	print("Reading metadata...")

	for file_num in range(1, file_count + 1):
		filepath_length = int.from_bytes(f.read(4), byteorder="little")
		file_info = struct.unpack_from("<{}sQQ16B".format(filepath_length), f.read(filepath_length + 8 + 8 + 16))
		path, offset, size = file_info[0:3]
		path = path.decode("utf-8").replace("://","/") # res:// and user://
		md5 = "".join([format(x, 'x') for x in file_info[-16:]])
		file_list.append({ 'path': path, 'offset': offset, 'size': size, 'md5': md5 })
		# print(file_num, "/", file_count, sep="", end=" ")
		# print(path, offset, size, md5)

	print("Unpacking ", file_count, " files...", sep="")

	for packed_file in file_list:
		path = os.path.join(output_dir, os.path.dirname(packed_file['path']))
		file_name_full = os.path.basename(packed_file['path']).rstrip("\0")
		file_name, file_extension = os.path.splitext(file_name_full)
		pathlib.Path(path).mkdir(parents=True, exist_ok=True)
		f.seek(packed_file['offset'])
		file_data = f.read(packed_file['size'])

		if unpack_containers:
			if file_extension == '.import':
				import_file_data = file_data.decode("utf-8")
				import_path = re.search(r"path=\"(.*)\"", import_file_data)
				import_source = re.search(r"source_file=\"(.*)\"", import_file_data)

				if import_path and import_source:
					import_path = import_path.group(1).replace("://","/")
					import_source = import_source.group(1).replace("://","/")
					import_file_list.append({"path": import_path, "source": import_source})

			if file_extension in ['.stex', '.tex', '.oggstr']:
				data = unpack_container(file_data)
				if isinstance(data, list):
					file_data = data[1]

		with open(os.path.join(path, file_name_full), "w+b") as p:
			p.write(file_data)

	f.close()
	
	for import_file in import_file_list:
		import_source = output_dir + "/" + import_file["source"]
		if os.path.exists(import_source):
			import_source = append_to_filename(import_source, "_import")
		os.rename(output_dir + "/" + import_file["path"], import_source)

def unpack_container(data):
	# webp
	start = data.find(bytes.fromhex("52 49 46 46"))
	if start >= 0:
		size = int.from_bytes(data[start + 4:start + 8], byteorder="little")
		return [".webp", data[start:start + 8 + size]]

	# png
	start = data.find(bytes.fromhex("89 50 4E 47 0D 0A 1A 0A"))
	if start >= 0:
		end = data.find(bytes.fromhex("49 45 4E 44 AE 42 60 82")) + 8
		return [".png", data[start:end]]

	# jpg
	start = data.find(bytes.fromhex("FF D8 FF"))
	if start >= 0:
		end = data.find(bytes.fromhex("FF D9")) + 2
		return [".jpg", data[start:end]]
	
	# ogg
	start = data.find(bytes.fromhex("4F 67 67 53"))
	if start >= 0:
		return [".ogg", data[start:-4]]
	
	return False

def append_to_filename(path, text):
	path = os.path.splitext(path)
	path = path[0] + text + path[1]
	return path

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))