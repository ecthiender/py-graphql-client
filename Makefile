install:
	python setup.py install

build:
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*
	make clean

clean:
	rm -rf build dist .egg py_graphql_client.egg-info
