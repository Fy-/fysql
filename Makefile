init:
	pip install -r requirements.txt

test:
	python tests.py

pep8:
	@flake8 fysql --ignore=F403,E241,E501 --exclude=__init__.py,tests.py

autopep8:
	@find . -name '*.py'|grep -v '__init__.py'| grep -v 'tests.py' |xargs autoflake --in-place --remove-all-unused-imports --remove-unused-variables
	@autopep8 --in-place --recursive --max-line-length=200 --exclude="*/migrations/*" .

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;