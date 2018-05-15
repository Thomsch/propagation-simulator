source ../virtualenv/linux/bin/activate
rm -r ./simulations/*
python generate.py simulation gameoflife
python generate.py entity cellule gameoflife
python generate.py action survivre gameoflife cellule --script
