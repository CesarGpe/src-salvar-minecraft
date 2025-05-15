from types import SimpleNamespace
from beet import Context, Function
from setup import REDUCEABLE, SCHEDULES, SCOREBOARDS, schedule

def collect_values(ns: SimpleNamespace):
    results = []
    for value in vars(ns).values():
        if isinstance(value, SimpleNamespace):
            results.extend(collect_values(value))
        else:
            results.append(value)
    return results

def beet_default(ctx: Context):
	# Schedule functions
	schedule(ctx, "mc2:sch/20t", "20t")
	# Message
	ctx.data.functions["mc2:load"].append('tellraw @a "Datapacks loaded!"')

	# Uninstall function
	ctx.data.functions["mc2:uninstall"] = Function('data remove storage mc2:storage data')
	for sc in collect_values(SCOREBOARDS):
		ctx.data.functions["mc2:uninstall"].append(f'scoreboard objectives remove {sc}')
	for sch in SCHEDULES:
		ctx.data.functions["mc2:uninstall"].append(f'schedule clear {sch}')

	# Tick function
	for sc in REDUCEABLE:
		ctx.data.functions["mc2:player_tick"].append(f'execute if score @s {sc} matches 1.. run scoreboard players remove @s {sc} 1')
            
	# Debug: reset item advancements
	ctx.data.functions["mc2:debug/reset_item_advancements"] = Function('')
	for adv in ctx.data.advancements:
		if adv.startswith("mc2:items/"):
			ctx.data.functions["mc2:debug/reset_item_advancements"].append(f'advancement revoke @s only {adv}')

	# Smithed
	ctx.data.mcmeta.data["id"] = "save-minecraft"
		