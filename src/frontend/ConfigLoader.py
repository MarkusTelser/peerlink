from appdirs import AppDirs

dirs = AppDirs("peerlink", "Markus Telser")

print(dirs.user_data_dir)
print(dirs.user_config_dir)

print("-")
print(dirs.user_cache_dir)
print(dirs.user_log_dir)
print(dirs.user_state_dir)