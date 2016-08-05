cd tmp
sh ../pack.sh test.7z aa bb dir1
7z a test2.7z aa bb dir1
diff test.7z test2.7z
