from gym.envs.registration import register

register(
    id="platenv-v0",
    entry_point="gym_plat.envs:GameEnv",
)
