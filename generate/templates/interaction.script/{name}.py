#!/usr/bin/env python
# -*-encoding:utf8-*-

from __future__ import (unicode_literals, division)

from simutils import *

class ${class_name}(Trigger):
	"""Define the interaction "$interaction_name" that occurs between entites
	"$interaction_entity1" and "$interaction_entity2".
	"""

	@staticmethod
	def is_performed(data):
		"""Check the preconditions and return True if the interaction is
		triggered, else False.

		If not overriden, always returns True.

		This is checked at the beginning of each iteration.
		"""
		return True

	@staticmethod
	def action_performed(data):
		"""Define what happens when the interaction is executed."""
		pass
