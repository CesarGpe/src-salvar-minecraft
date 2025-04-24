import json
from beet import Context, ItemModifier, LootTable

def beet_default(ctx: Context):
	# Initialize the LootTable structure
	loot_table = {
		"pools": []
	}

	# Iterate over all mc2:* recipes
	for key, recipe in ctx.data.recipes.items():
		if not key.startswith("mc2"):
			continue
		
		# Parse recipe JSON (in case it's returned as a string)
		raw = recipe.get_content()
		content = json.loads(raw) if isinstance(raw, str) else raw

		# Extract the item name and components
		result = content.get("result", {})
		item_name = result.get("id")
		components = result.get("components", {})

		# Build the entry
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
		# Build the pool
		pool = {
            "rolls": 1,
            "entries": [entry]
        }
		# Add to the loot table
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