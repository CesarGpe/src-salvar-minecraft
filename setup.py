from types import SimpleNamespace
from beet import Context, Function

REDUCEABLE = []
SCOREBOARDS = SimpleNamespace()
def scoreboard(ctx:Context, id, name, objective, tick_reduce=False) -> str:
	full = f"mc2.{id}.{name}"

	if not hasattr(SCOREBOARDS, id):
		setattr(SCOREBOARDS, id, SimpleNamespace())
	getattr(SCOREBOARDS, id).__setattr__(name, full)

	if tick_reduce:
		REDUCEABLE.append(full)
	ctx.data.functions["mc2:load"].append(f'scoreboard objectives add {full} {objective}')
	return full

SCHEDULES = []
def schedule(ctx:Context, func, time):
	SCHEDULES.append(func)
	ctx.data.functions["mc2:load"].append(f'schedule function {func} {time} replace')

def beet_default(ctx: Context):
    # Technical scoreboards
	scoreboard(ctx, "recovery_compass", "cooldown", "dummy", True)
	scoreboard(ctx, "recovery_compass", "can_tp", "dummy")
	scoreboard(ctx, "recovery_compass", "timer", "dummy")
	scoreboard(ctx, "recovery_compass", "use", "dummy")

	scoreboard(ctx, "tinker_goggles", "coords.x", "dummy")
	scoreboard(ctx, "tinker_goggles", "coords.y", "dummy")
	scoreboard(ctx, "tinker_goggles", "coords.z", "dummy")
	scoreboard(ctx, "tinker_goggles", "temp", "dummy")
		