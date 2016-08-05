cd tmp
sh ../pack.sh test.Z aa bb dir1
tar cvf test2.tar aa bb dir1
compress test2.tar
diff test.tar.Z test2.tar.Z
