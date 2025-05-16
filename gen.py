import re, json
from beet import Context, JsonFile, LootTable, Model, ItemModel, Equipment

def beet_default(ctx: Context):
	print("Dummy!")

def translate_key(raw):
		if raw is None:
			return None
		key:str = raw.get("translate")
		name = key.removeprefix("item.mc2.")
		return re.sub(r'\s+', '_', name.strip().lower())

def creative_menu(ctx: Context):
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
			name = result.get("id")
			entry = {
				"type": "minecraft:item",
				"name": name,
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
						if func.get("function") in {"minecraft:set_components", "set_components"}:
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
					return translate_key(components["minecraft:item_name"])
		# Fallback to the item id (like minecraft:diamond_sword)
		name = entry_dict.get("name", "").lower()
		if ":" in name:
			name = name.split(":", 1)[1]  # Remove namespace prefix
		return name
	
	def normalize_entry(entry):
		# Ensure type is fully qualified
		if entry.get("type") == "item":
			entry["type"] = "minecraft:item"

		# Normalize and clean functions
		functions = entry.get("functions", [])
		for func in functions:
			if func.get("function") == "set_components":
				func["function"] = "minecraft:set_components"

			# Remove unnecessary keys inside functions
			if func.get("function") == "minecraft:set_components":
				func.pop("add", None)
				func.pop("count", None)

		# Remove top-level keys that aren't needed
		entry.pop("weight", None)

		return entry

	# Parse back into list of dicts
	sorted_entries = sorted(
		(normalize_entry(json.loads(entry_str)) for entry_str in unique_entries),
		key=sort_key
	)

	# === Assemble and register the master loot table ===
	loot_table = {
		"pools": []
	}

	for entry in sorted_entries:
		pool = {
			"rolls": 1,
			"entries": [entry]
		}
		loot_table["pools"].append(pool)

	ctx.data.loot_tables["mc2:creative_loot_table"] = LootTable(
		_content = loot_table,
		serializer = lambda d: json.dumps(d, indent=4, sort_keys=True),
		deserializer = json.loads
	)

	# === Generate per-item loot tables ===
	for entry in sorted_entries:
		name:str = None
		for func in entry.get("functions", []):
			if func.get("function") == "minecraft:set_components":
				components = func.get("components", {})
				name = translate_key(components.get("minecraft:item_name"))
				break

		# If item_name was not found in components, use the fallback from entry["name"]
		if not name:
			raw_name = entry.get("name", "")
			name = raw_name.removeprefix("minecraft:")

		if name:
			single_entry_loot_table = {
				"pools": [{
					"rolls": 1,
					"entries": [entry]
				}]
			}

			ctx.data.loot_tables[f"mc2:item/{name}"] = LootTable(
				_content = single_entry_loot_table,
				serializer = lambda d: json.dumps(d, indent=4, sort_keys=True),
				deserializer = json.loads
			)

def components(ctx: Context):
	# Generate default component jsons
	for key, recipe in ctx.data.recipes.items():
		if not key.startswith("minecraft:"):
			continue

		raw = recipe.get_content()
		content = json.loads(raw) if isinstance(raw, str) else raw

		result = content.get("result", {})
		components = result.get("components")
		if components:
			item_id = result.get("id")
			if not item_id:
				continue

			output = {
				"targets": item_id,
				"components": components
			}
			file_name = item_id.split(":", 1)[-1]
			output_path = f"data/mc2/item_components/{file_name}.json"
			ctx.data.extra[output_path] = JsonFile(output)

	# Build an item modifier with the components from the recovery compass recipe
	""" raw = ctx.data.recipes["minecraft:recovery_compass"].get_content()
	content = json.loads(raw)
	components = content.get("result", {}).get("components", {})

	new_modifier = dict({"function": "minecraft:set_components"})
	new_modifier["components"] = components
	ctx.data.item_modifiers["mc2:change_recovery_compass"] = ItemModifier(new_modifier) """

	# Testing
	""" for k, v in ctx.data.item_modifiers.items():
		if k.startswith("mc2"):
			print("#", k)
			print(v)
			print() """
	
def models(ctx: Context):
	for tex in ctx.assets.textures:
		# Equipment
		if tex.startswith(f"mc2:entity/equipment/humanoid/"):
			_, name = tex.split("mc2:entity/equipment/humanoid/")
			val = f"mc2:{name}"
			ctx.assets.equipments[val] = Equipment({
				"layers": {
					"humanoid": [
						{
							"texture": val
						}
					]
				}
			})
		# Items
		if tex.startswith(f"mc2:item/"):
			_, name = tex.split('/')
			""" ctx.assets.models[f"mc2:item/{name}"] = Model({
				"parent": "item/handheld",
				"textures": {
					"layer0": tex
				}
			}) """
			ctx.assets.item_models[f"mc2:{name}"] = ItemModel({
				"model" : {
					"type" : "model",
					"model" : tex	
				}
			})