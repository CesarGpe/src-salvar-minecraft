from types import SimpleNamespace
from beet import Context, Function

REDUCEABLE = []
SCOREBOARDS = []
def scoreboard(ctx:Context, id, name, objective, tick_reduce=False) -> str:
	full = f"mc2.{id}.{name}"
	SCOREBOARDS.append(full)

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
	scoreboard(ctx, "recovery_compass", "math", "dummy")
	scoreboard(ctx, "recovery_compass", "can_tp", "dummy")
	scoreboard(ctx, "recovery_compass", "timer", "dummy")
	scoreboard(ctx, "recovery_compass", "use", "dummy")

	scoreboard(ctx, "navigoggles", "coords.x", "dummy")
	scoreboard(ctx, "navigoggles", "coords.y", "dummy")
	scoreboard(ctx, "navigoggles", "coords.z", "dummy")
	scoreboard(ctx, "navigoggles", "temp", "dummy")
		