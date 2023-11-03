# godot-unpacker
godot archive unpacker for non-encrypted files

## system requirements
* python 3.10

## usage
move .pck or .exe (if game itself is a large exe file) file in the same directory as script and run:
```
python godot-unpacker.py data.pck
```
or
```
python godot-unpacker.py your_godot_game.exe
```
extracted game files should be in "output" directory.
## converting textures
unpacker will convert .tex texture files into corresponding image format (webp, png or jpg) automatically. if you want .tex files to remain intact make sure ```unpack_containers``` is set to ```False```.
