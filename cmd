Anaconda:
	install

Without Anaconda:
	pip install scipy --user

python setup.py build
python setup.pu install

python tests/



Docker:

docker build -t pymcpsc .

docker run -v /home/asharma/workspace/spyder_workspace/pymcpsc/tests/:/usr/src/app/tests/ pymcpsc run-pymcpsc -d /usr/src/app/tests/chew_kedem_dataset/pdb_files/ -e pdb

docker run pymcpsc python -c "import sys; print '\n'.join(sys.path)"

docker run -v /home/asharma/phd/docker-test:/usr/shared pymcpsc:latest run-pymcpsc -e pdb -d /usr/shared/data/pdb_files -g /usr/shared/data/ground_truth_ck

sphinx-apidoc ../pymcpsc/ -o source/
