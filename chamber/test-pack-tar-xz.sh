cd tmp
sh ../pack.sh test.tar.xz aa bb dir1
tar cvf test2.tar aa bb dir1
xz test2.tar
diff test.tar.xz test2.tar.xz
