from dataclasses import dataclass, field
from typing import List
from utils import damageItem, itemTickAdvancement
from setup import scoreboard, SCOREBOARDS
from beet import Context, Function, Advancement

@dataclass
class ItemConfig:
	tag: str # The item tag WITHOUT "mc2."
	slot: str|List[str] # The slot or slots where the item needs to be to loose durability
	max_damage: int = 50 # The durability of the item
	time: int = 1200 # Time that it takes for a damage event
	amt: int = 1 # Amount of damage the item takes per damage event
	tick_func: str|List[str]= "" # Commands to run every tick the item is in the correct slot
	break_func: List[str] = field( # Commands to run when the item breaks
		default_factory=lambda:['playsound minecraft:entity.item.break player @a ~ ~ ~ 1 1 0'])

# List of custom_data tags that will be affected by this plugin
ITEMS = [
    ItemConfig(tag="udjat",slot=["weapon.offhand","weapon.mainhand"]),
    ItemConfig(tag="hopoo_feather",slot=["weapon.offhand","weapon.mainhand"]),
    ItemConfig(tag="supershell",slot=["weapon.offhand","weapon.mainhand"]),
    ItemConfig(tag="spidercap",slot="armor.head",tick_func="effect give @s minecraft:night_vision 3 0 true",break_func=[
		'playsound minecraft:entity.item.break player @a ~ ~ ~ 0.8 1.2 0',
		'playsound minecraft:entity.spider.death player @a ~ ~ ~ 1 0.8 0',
		'particle item{item:"spider_spawn_egg"} ~ ~1.8 ~ 0 0 0 0.1 15 normal'
	]),
]

def beet_default(ctx: Context):
	for item in ITEMS:
		registerForDamage(ctx, item)

def registerForDamage(ctx:Context, item:ItemConfig):
	slots = item.slot if isinstance(item.slot, list) else [item.slot]
	for slot in slots:
		TIMER = scoreboard(ctx, item.tag, "durability_timer", "dummy")
		slot_name = slot.split(".")[-1]

		real_break_func = Function([
			f'execute unless items entity @s {slot} *[minecraft:custom_data={{mc2.{item.tag}:1b}},minecraft:damage={item.max_damage}] run return 0',
			f'item replace entity @s {slot} with air'
		])
		real_break_func.append(item.break_func)

		damage_once = damageItem(slot)
		damage_once.prepend(f'scoreboard players reset @s {TIMER}')
		damage_once.append(real_break_func)
		damage_func = f"mc2:items/{item.tag}/damage_{slot_name}"
		ctx.data.functions[damage_func] = damage_once

		registry = f"mc2:items/{item.tag}/tick_{slot_name}"
		ctx.data.advancements[registry] = Advancement(itemTickAdvancement(item.tag, slot_name))
		ctx.data.functions[registry] = Function([
			item.tick_func,
			f'execute if predicate mc2:in_creative run return run advancement revoke @s only {registry}',
			f'scoreboard players add @s {TIMER} 1',
			f'execute if score @s {TIMER} matches 1200.. run function {damage_func}',
			f'advancement revoke @s only {registry}'
		])




	""" TIMER = scoreboard(ctx, item.tag, "durability_timer", "dummy")
	
	real_break_func = Function([
		f'execute unless items entity @s {item.slot} *[minecraft:custom_data={{mc2.{item.tag}:1b}},minecraft:damage={item.max_damage}] run return 0',
		f'item replace entity @s {item.slot} with air'
	])
	real_break_func.append(item.break_func)

	damage_once = damageItem(item.slot)
	damage_once.prepend(f'scoreboard players reset @s {TIMER}')
	damage_once.append(real_break_func)
	damage_func = f"mc2:items/{item.tag}/damage"
	ctx.data.functions[damage_func] = damage_once

	registry = f"mc2:items/{item.tag}/tick"
	slot = item.slot.split(".")[-1]
	ctx.data.advancements[f"mc2:items/{item.tag}/tick_{slot}"] = Advancement(itemTickAdvancement(item.tag, slot))
	ctx.data.functions[registry] = Function([
		item.tick_func,
		f'execute if predicate mc2:in_creative run return run advancement revoke @s only {registry}',
		f'scoreboard players add @s {TIMER} 1',
		f'execute if score @s {TIMER} matches 1200.. run function {damage_func}',
		f'advancement revoke @s only {registry}'
	]) """