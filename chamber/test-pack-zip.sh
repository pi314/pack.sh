cd tmp
sh ../pack.sh test.zip aa bb dir1
zip --symlinks --exclude test2.zip -r test2.zip aa bb dir1
diff test.zip test2.zip
