install:
	python setup.py install

build:
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*
	make clean

test_publish: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	make clean

clean:
	rm -rf build dist .egg py_graphql_client.egg-info
