#!/usr/bin/env python
# -*-encoding:utf8-*-

from __future__ import (unicode_literals, division)

from simutils import *

class ${class_name}(Trigger):
	"""Define the action trigger for "${action_name}" for the
	entity "${entity_name}".
	"""

	@staticmethod
	def is_performed(data):
		"""Check the preconditions and return True if the action is
		triggered, else False.

		If not overriden, always returns True.

		This is checked at the beginning of each iteration.
		"""
		return True

	@staticmethod
	def action_performed(data):
		"""Define what happens when the action is executed."""
		pass
