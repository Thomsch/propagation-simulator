source ../virtualenv/linux/bin/activate
rm -r ./simulations/*
python generate.py simulation malaria
python generate.py entity moustique malaria --attr taux_malaria couleur
python generate.py entity humain malaria
python generate.py action guerir malaria humain
python generate.py interaction piquer malaria moustique humain
python generate.py interaction contaminer malaria humain humain --script
