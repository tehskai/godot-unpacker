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
extracted game files should be in ```data``` or ```your_godot_game``` directory.
## converting textures
unpacker will convert .tex, .stex, .oggstr container files into corresponding asset format (webp, png, jpg, ogg) automatically. if you want container files to remain intact make sure to use ```--raw``` argument.
```
python godot-unpacker.py data.pck --raw
```