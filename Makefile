count_lines:
	wc -l src/*.py | sort -gk 1
clean:
	rm -rf src/*.pyc *~ */*~

