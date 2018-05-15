#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Script de **Scaffolding** de PropagationSimulator.

Construit les fichiers de config nécessaires à la définition d'une
simulation.

Quatre possibilités d'objet à créer :

* simulation  : crée une nouvelle simulation
* entity      : crée une nouvelle entité avec ses attributs
* action      : crée une nouvelle action sur une entité
* interaction : crée une nouvelle interaction entre deux entités

Utilisation
===========

Pour lancer le script, ouvrir une invite de commande dans le dossier du
script et appeler `python propsim.py`.

Les paramètres qui suivent s'écrivent selon la syntaxe suivante :

	cmd         = simulation | entity | action | interaction

	simulation  = "simulation" sim_name
	entity      = "entity" entity_name attribs sim_name
	action      = "action" action_name sim_name entity_name ["--script"]
    interaction = "interaction" interaction_name sim_name entity1_name entity2_name ["--script"]

	attribs     = [ "--attr" { attribute_name } ]
	X_name      = { "A" | ... | "Z" |
	                "a" | ... | "z" |
	                "0" | ... | "9" |
	                "_" }

Note : il est possible que l'ordre des arguments ne soit pas exactement
pareil.

L'option `--help` ou `-h` permet d'afficher l'aide. Il est aussi
possible d'afficher l'aide d'une sous-commande.
L'option `--debug` permet d'afficher les données de l'item qui sera créé
sans modifier ni créer de fichier.

Exemple : `python propsim.py human entity --help` affichera les
paramètres de la commande `entity`.

Templates
=========

Les templates se trouvent dans le dossier `templates` qui possède la
structure suivante :

    templates/
        <type d'objet 1>/
            <fichiers templates du type d'objet 1>
        <type d'objet 2>/
            <fichiers templates du type d'objet 2>
        ...

Créer une instance du type d'objet 1 par exemple créera à la racine une
copie du contenu du dossier <type d'objet 1>, avec les champs du
template remplacés par leur valeur.

Le format des champs est le suivant :

* Pour les noms de fichiers et de dossiers : `{nom_du_champ}`
* Pour le contenu des fichiers : `$nom_du_champ` ou `${nom_du_champ}`

Un exception pour le template des actions car celles-ci nécessitent
d'être ajoutées au fichier `action.json` du dossier de l'entité concernée.
Le fichier `action.json` contient donc le template de ce qui sera ajouté
à ce fichier.

Exécution
=========

Nécessite la librairie path.py. S'installe avec `pip install pyth.py`.

Si nécessaire, créer un virtalenv à partir de `../virtualenv/requirements.txt`.

"""

import argparse
from string import Template
from path import path
from utils.json_parser_utility import json_parser_utility
from pprint import pprint

USER_FOLDER = path('.')
TEMPLATES_FOLDER = path("templates")
SIMULATIONS_FOLDER = USER_FOLDER / "simulations"
TAB = "    "
NEXT_LINE = '\n' + TAB

def generate_file(template_file, destination):
    substituted_path = path(str(template_file).format(name=name))
    file = destination.joinpath(*substituted_path.splitall()[3:])
    if template_file.isdir():
        print "CREATE DIR\t'{}'".format(file)
        file.makedirs_p()
    else:
        print "CREATE FILE\t'{}'".format(file)
        file.touch()
        template = Template(template_file.text())
        file.write_text(template.substitute(context))

def to_camelcase(identifier):
    return "".join(c for c in identifier.title() \
                   if not (c.isspace() or c == '_'))

#
# Crée un parseur pour les arguments
#

# Arguments globaux
parser = argparse.ArgumentParser(
    description=\
    """Create a base structure for a new simulation, or for new itmes to
    add in the simulation (entites, interactions, ...).
    WARNING: if you try to create an item that is already defined, it will
    be overriden, so you will lose all modifications on the previous one!
    """
)
parser.add_argument('--debug', action='store_true',
    help="shows which data will be passed to the template files, \
          without actually modifiying or creating anything."
)

# Crée les sous-parseurs pour les arguments spécifiques
subparsers = parser.add_subparsers(dest='object_type')
simulation_parser = subparsers.add_parser('simulation')
entity_parser = subparsers.add_parser('entity')
interaction_parser = subparsers.add_parser('interaction')
action_parser = subparsers.add_parser('action')

# Crée les arguments spécifiques à chaque sous-parseur
simulation_parser.add_argument('simulation_name', type=str,
    help="name of the new simulation"
)
entity_parser.add_argument('entity_name', type=str,
    help="name of the new entity"
)
entity_parser.add_argument('--attr', metavar='attribute', type=str,
	nargs='*', help="attributes of the new entity"
)
action_parser.add_argument('action_name', type=str,
    help="name of the new action"
)
action_parser.add_argument('--script', action='store_true',
    help="define the action in a Python script"
)
interaction_parser.add_argument('--script', action='store_true',
    help="define the interaction in a Python script"
)
interaction_parser.add_argument('interaction_name', type=str,
    help="name of the new interaction"
)

# Version avec typage  (chaque attribut s'introduit par --attr)
# entity_parser.add_argument('--attr', metavar='attributes',
# 	action='append', nargs=2, help="Attributes of the new entity"
# )

# Crée les paramètres spécifiant les objets cibles du nouvel objet créé
entity_parser.add_argument('simulation_name', type=str,
    help="simulation in which the entity will be created"
)
action_parser.add_argument('simulation_name', type=str,
    help="simulation in which the action will be created"
)
interaction_parser.add_argument('simulation_name', type=str,
    help="simulation in which the interaction will be created"
)
action_parser.add_argument('entity_name', type=str,
    help="entity that executes the action"
)
interaction_parser.add_argument('interaction_entity1', metavar='entity1',
	type=str, help="first entity concerned by the interaction"
)
interaction_parser.add_argument('interaction_entity2', metavar='entity2',
 	type=str, help="second entity concerned by the interaction"
)

#
# Construit les fichiers de config à partir des arguments
#

# Récupère les arguments
args = parser.parse_args()
object_type = args.object_type

# Construit le dictionnaire de contexte à partir des arguments et en tire
# les informations nécessaires à l'appel des templates
context = vars(args)
obj_type = context['object_type']
name = context[obj_type + "_name"]
simulation_name = context.get('simulation_name', "")
template_suffix = ".script" if context.get('script', False) else ""
context['class_name'] = to_camelcase(name)
if obj_type == 'entity':
    def jsonize_attributes(attributes):
        txt = []
        for i, attr in enumerate(attributes):
            txt.append( \
                "\"{}\": \"\"{} //TODO Give an initial value to this attribute"\
                .format(attr, "," if i < len(attributes)-1 else ""))
        return NEXT_LINE.join(txt)
    context['attr'] = jsonize_attributes(context.get('attr', []) or [])
    context['add_comma'] = ", " if len(context['attr']) > 0 else ""
print "Add {} '{}' in simulation '{}'".format(obj_type, name, simulation_name)

#
# Création des fichiers selon le template
#

# Crée les dossiers nécessaires s'ils n'existent pas
if not SIMULATIONS_FOLDER.isdir():
    SIMULATIONS_FOLDER.mkdir()
destination = SIMULATIONS_FOLDER

if context['debug']:
    print "Context data:"
    pprint(context)
else:
    # Dans le cas d'une action, ajoute l'action (ou le lien dans le cas
    # d'un script) au fichier JSON des actions
    if obj_type == 'action':
        action_name = context['action_name']
        entity_name = context['entity_name']
        is_script = context.get('script', False)
        action_path = destination / simulation_name / "entities" \
                      / entity_name
        action_def_path = action_path / "actions.json"
        template_path = TEMPLATES_FOLDER / path(obj_type + template_suffix)
        action_def_template = template_path / "action.json"
        action_script_template = template_path / "{name}.py"
        json_content = Template(action_def_template.text()).substitute(context)
        if not action_def_path.isfile():
            print "Error: missing file '{}'".format(action_def_path.realpath())
            print "Maybe the simulation or the entity isn't created?"
        else:
            print "ALTER FILE\t'{}'".format(action_def_path)
            with json_parser_utility(action_def_path) as action_data:
                action_data.add_action_from_template(action_name, json_content)
            if is_script:
                generate_file(action_script_template, action_path)
    else:
        # Crée les fichiers de configuration à partir des fichiers de template
        if obj_type == 'entity':
            destination = destination / simulation_name / "entities"
        elif obj_type == 'interaction':
            destination = destination / simulation_name / "entities" \
                           / "interactions"
        template = TEMPLATES_FOLDER / path(obj_type + template_suffix)
        for template_file in template.walk():
            generate_file(template_file, destination)
