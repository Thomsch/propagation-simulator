# exceptions, les exceptions

Ce dossier contient :

- **__init.py__** définit le dossier comme package.
- **json_error** problème de JSON pur
    - **json_maformated_error*** syntaxe JSON
    - **json_not_found** fichier introuvable
- **script_error** erreurs de scripts utilisateurs
    - **action_malformated_error** l'action est incomplète ou erronée
    - **invalid_identifier_error** nom de variable invalide
    - **missing_attribute_error** un attribut nécessaire n'est pas 
    définit.
    - **script_not_found** un script python est introuvable
    - **terrain_not_found** un terrain inexistant est référencé.
