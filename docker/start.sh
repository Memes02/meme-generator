#!/bin/sh
envsubst < /app/config.toml.template | tee ~/.config/meme_generator/config.toml > /dev/null
exec uv run meme start