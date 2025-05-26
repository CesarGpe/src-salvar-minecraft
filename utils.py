import re
from setup import scoreboard
from beet import Context, Function, Advancement

def beet_default(ctx: Context):
	scoreboard(ctx, "utils", "durability", "dummy")
	ctx.data.functions["mc2:utils/damage_macro"] = Function('$item modify entity @s $(slot) {"function": "minecraft:set_components","components": {"minecraft:damage": $(damage)}}')
	ctx.data.functions["mc2:utils/tp_macro"] = Function('$tp @s $(x) $(y) $(z)')
	
def damageItem(SLOT:str, AMOUNT=1) -> Function:
	DAMAGE = "mc2.utils.durability"
	DATA_SLOT = slot_to_nbt_path(SLOT)

	return Function([
		# For the first damage proc, damage component could not be present yet
		f'execute unless data entity @s {DATA_SLOT}.components."minecraft:damage" run return run item modify entity @s {SLOT} {{"function":"minecraft:set_components","components":{{"minecraft:damage":{AMOUNT}}}}}',

		# Get durability, add, then damage the item
		f'execute store result score @s {DAMAGE} run data get entity @s {DATA_SLOT}.components."minecraft:damage"',
		f'execute store result storage mc2:storage data.utils.damage int 1 run scoreboard players add @s {DAMAGE} {AMOUNT}',

		f'data modify storage mc2:storage data.utils merge value {{slot:{SLOT}}}',
		'function mc2:utils/damage_macro with storage mc2:storage data.utils',
	])

def itemTickAdvancement(ctx: Context, tag: str, slot:str) -> str:
	registry = f"mc2:items/{tag}/tick_{slot}"
	ctx.data.advancements[registry] = Advancement({
		"criteria": {
			"requirement": {
				"trigger": "minecraft:tick",
				"conditions": {
					"player": [
						{
							"condition": "minecraft:entity_properties",
							"entity": "this",
							"predicate": {
								"equipment": {
									slot: {
										"predicates": {
											"minecraft:custom_data": {
												f"mc2.{tag}": True
											}
										}
									}
								}
							}
						}
					]
				}
			}
		},
		"rewards": {
			"function": registry
		}
	})
	return registry

def slot_to_nbt_path(identifier: str) -> str:
	# Convert slot identifiers like 'armor.chest', 'weapon.mainhand', 'inventory.0',
	# 'hotbar.3', 'weapon.offhand' to NBT path strings for /data commands.
	identifier = identifier.lower()
	mapping = {
		'armor.head': 'equipment.head',
		'armor.chest': 'equipment.chest',
		'armor.legs': 'equipment.legs',
		'armor.feet': 'equipment.feet',
		'weapon.mainhand': 'SelectedItem',
		'weapon.offhand': 'equipment.offhand',
	}
	
	# Direct mapping
	if identifier in mapping:
		return mapping[identifier]
	
	# Hotbar slots: hotbar.0 - hotbar.8
	hotbar_match = re.match(r'hotbar\.(\d+)', identifier)
	if hotbar_match:
		idx = int(hotbar_match.group(1))
		if 0 <= idx <= 8:
			return f'Inventory[{{Slot:{idx}b}}]'
	
	# Inventory slots: inventory.0 - inventory.26 (maps to slots 9-35)
	inv_match = re.match(r'inventory\.(\d+)', identifier)
	if inv_match:
		idx = int(inv_match.group(1))
		if 0 <= idx <= 26:
			slot_idx = 9 + idx
			return f'Inventory[{{Slot:{slot_idx}b}}]'
	
	raise ValueError(f"Unknown slot identifier: '{identifier}'")
