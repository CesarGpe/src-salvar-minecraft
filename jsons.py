import json
from beet import Context, ItemModifier, LootTable

def beet_default(ctx: Context):
	# Use a set to store unique JSON-stringified entries
	unique_entries = set()

	# === PART 1: Add entries from ALL recipes that have custom_data ===
	for key, recipe in ctx.data.recipes.items():
		raw = recipe.get_content()
		content = json.loads(raw) if isinstance(raw, str) else raw

		result = content.get("result", {})
		components = result.get("components", {})

		# Only add recipes whose result has minecraft:custom_data
		if "minecraft:custom_data" in components:
			item_name = result.get("id")
			entry = {
				"type": "minecraft:item",
				"name": item_name,
				"functions": [
					{
						"function": "minecraft:set_components",
						"components": components
					}
				]
			}
			unique_entries.add(json.dumps(entry, sort_keys=True))

	# === PART 2: Scan all loot tables for items with minecraft:custom_data ===
	for key, lt in ctx.data.loot_tables.items():
		raw = lt.get_content()
		content = json.loads(raw) if isinstance(raw, str) else raw

		pools = content.get("pools", [])
		for pool in pools:
			entries = pool.get("entries", [])
			for entry in entries:
				if entry.get("type") in {"minecraft:item", "item"}:
					for func in entry.get("functions", []):
						if func.get("function") in {"minecraft:set_components"}:
							components = func.get("components", {})
							if "minecraft:custom_data" in components:
								unique_entries.add(json.dumps(entry, sort_keys=True))
								break

	# === Sort entries ===
	def sort_key(entry_dict):
		# Look for item_name inside components if available
		for func in entry_dict.get("functions", []):
			if func.get("function") in {"minecraft:set_components", "set_components"}:
				components = func.get("components", {})
				if "minecraft:item_name" in components:
					return components["minecraft:item_name"].lower()
		# Fallback to the item id (like minecraft:diamond_sword)
		return entry_dict.get("name", "").lower()

	# Parse back into list of dicts
	sorted_entries = sorted(
		(json.loads(entry_str) for entry_str in unique_entries),
		key=sort_key
	)

	# === Assemble final loot table ===
	loot_table = {
		"pools": []
	}

	for entry in sorted_entries:
		pool = {
			"rolls": 1,
			"entries": [entry]
		}
		loot_table["pools"].append(pool)

	# Register the loot table
	ctx.data.loot_tables["mc2:creative_loot_table"] = LootTable(loot_table)

	# Testing
	""" for k, v in ctx.data.item_modifiers.items():
		if k.startswith("mc2"):
			print("#", k)
			print(v)
			print() """

	# Get components from the parsed contents of the recovery compass recipe
	raw = ctx.data.recipes["minecraft:recovery_compass"].get_content()
	content = json.loads(raw)
	components = content.get("result", {}).get("components", {})

	# Build an item modifier with the components of the recipe
	new_modifier = dict({"function": "minecraft:set_components"})
	new_modifier["components"] = components
	ctx.data.item_modifiers["mc2:change_recovery_compass"] = ItemModifier(new_modifier)