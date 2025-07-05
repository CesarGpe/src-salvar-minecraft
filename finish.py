from beet import Context, Function
from setup import REDUCEABLE, SCOREBOARDS, CLOCKS, clock

def beet_default(ctx: Context):
	# Set clock functions
	clock(ctx, "mc2:technical/second_clock", "1s")
	clock(ctx, "mc2:technical/ten_second_clock", "10s")
	
	# Message
	ctx.data.functions["mc2:load"].append('tellraw @a "Datapacks loaded!"')

	# Tick function
	for sc in REDUCEABLE:
		ctx.data.functions["mc2:player_tick"].append(f'execute if score @s {sc} matches 1.. run scoreboard players remove @s {sc} 1')
            
	# Debug: reset item advancements
	func = "mc2:commands/revoke_technical_advancements"
	ctx.data.functions[func] = Function('# Generated function')
	for adv in ctx.data.advancements:
		if adv.startswith("mc2:technical/"):
			ctx.data.functions[func].append(f'advancement revoke @s only {adv}')

	# Uninstall function
	func = "mc2:commands/uninstall"
	ctx.data.functions[func] = Function(['# Generated function','data remove storage mc2:storage data'])
	for sc in SCOREBOARDS:
		ctx.data.functions[func].append(f'scoreboard objectives remove {sc}')
	for sch in CLOCKS:
		ctx.data.functions[func].append(f'schedule clear {sch}')

	# Mcmeta file
	ctx.data.mcmeta.data["id"] = "save-minecraft"
	ctx.data.mcmeta.data["filter"] = {
		"block": [
			{
				"namespace": "minecraft",
				"path": "recipe/dried_ghast.json",
			},
			{
				"namespace": "minecraft",
				"path": "advancement/adventure/brush_armadillo.json",
			},
			{
				"namespace": "minecraft",
				"path": "advancement/adventure/walk_on_powder_snow_with_leather_boots.json",
			},
			{
				"namespace": "minecraft",
				"path": "advancement/husbandry/feed_snifflet.json",
			},
		]
	}
		