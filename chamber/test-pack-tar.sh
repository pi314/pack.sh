cd tmp
sh ../pack.sh test.tar aa bb dir1
tar cvf test2.tar aa bb dir1
diff test.tar test2.tar
