count_lines:
	wc -l src/*.py src/api/cpp/*.cpp src/api/cpp/*.hpp | sort -gk 1
clean:
	rm -rf src/*.pyc *~ */*~ */*/*~ */*/*/*~ */*/*/*.o

